import json
import os
from dataclasses import asdict
from datetime import datetime

from models.brief import ProductBrief
from models.scorecard import Scorecard
from orchestrator.message_bus import MessageBus


class Exporter:

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _slug(self, title: str) -> str:
        return title.lower().replace(" ", "_")[:40]

    def _timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def save_json(self, scorecard: Scorecard, brief: ProductBrief) -> str:
        payload = {
            "idea_title": brief.idea_title,
            "exported_at": datetime.utcnow().isoformat(),
            "scorecard": {
                "dimensions": {
                    "market_size": self._dim(scorecard.market_size),
                    "icp_clarity": self._dim(scorecard.icp_clarity),
                    "gtm_viability": self._dim(scorecard.gtm_viability),
                    "technical_feasibility": self._dim(scorecard.technical_feasibility),
                    "build_complexity": self._dim(scorecard.build_complexity),
                    "ux_viability": self._dim(scorecard.ux_viability),
                    "user_journey_clarity": self._dim(scorecard.user_journey_clarity),
                    "competitive_moat": self._dim(scorecard.competitive_moat),
                    "revenue_model_strength": self._dim(scorecard.revenue_model_strength),
                },
                "overall_score": scorecard.overall_score,
                "go_no_go": scorecard.go_no_go,
                "go_condition": scorecard.go_condition,
                "next_actions": [
                    {"action": a.action, "owner": a.owner} for a in scorecard.next_actions
                ],
                "debate_rounds_completed": scorecard.debate_rounds_completed,
                "consensus_reached": scorecard.consensus_reached,
            },
        }
        filename = f"{self._slug(brief.idea_title)}_{self._timestamp()}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

    def save_markdown(self, scorecard: Scorecard, brief: ProductBrief, bus: MessageBus) -> str:
        lines = [
            f"# Product Validation: {brief.idea_title}",
            f"\n_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_\n",
            "## Product Brief",
            f"\n{brief.to_text()}\n",
            "## Scorecard\n",
            "| Dimension | Score | Rationale |",
            "|---|---|---|",
        ]

        dimensions = [
            scorecard.market_size, scorecard.icp_clarity, scorecard.gtm_viability,
            scorecard.technical_feasibility, scorecard.build_complexity,
            scorecard.ux_viability, scorecard.user_journey_clarity,
            scorecard.competitive_moat, scorecard.revenue_model_strength,
        ]
        for dim in dimensions:
            if dim:
                lines.append(f"| {dim.dimension} | {dim.score}/10 | {dim.rationale} |")

        lines += [
            f"\n**Overall Score: {scorecard.overall_score}/10**\n",
            f"**Verdict: {scorecard.go_no_go}**",
        ]
        if scorecard.go_condition:
            lines.append(f"\n_Condition: {scorecard.go_condition}_")

        lines.append("\n## Next Actions\n")
        for i, action in enumerate(scorecard.next_actions, 1):
            lines.append(f"{i}. [{action.owner}] {action.action}")

        lines.append("\n## Debate Transcript\n")
        for round_num in range(1, scorecard.debate_rounds_completed + 1):
            messages = bus.get_round_messages(round_num)
            if messages:
                lines.append(f"\n### Round {round_num}\n")
                for msg in messages:
                    lines.append(f"**[{msg.agent_name}]**\n\n{msg.content}\n")

        content = "\n".join(lines)
        filename = f"{self._slug(brief.idea_title)}_{self._timestamp()}.md"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _dim(self, dim) -> dict:
        if dim is None:
            return {}
        return {"score": dim.score, "rationale": dim.rationale, "risks": dim.risks}
