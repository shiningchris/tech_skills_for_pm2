import json

from agents.pm_agent import PMAgent
from agents.marketer_agent import MarketerAgent
from agents.tech_agent import TechAgent
from agents.design_agent import DesignAgent
from config import Config
from models.brief import ProductBrief
from models.scorecard import DimensionScore, Scorecard
from orchestrator.message_bus import MessageBus


class DebateOrchestrator:

    def __init__(
        self,
        pm: PMAgent,
        marketer: MarketerAgent,
        tech: TechAgent,
        design: DesignAgent,
        bus: MessageBus,
        config: Config,
        on_message=None,  # optional callback(agent_name, content, round_num) for live display
    ):
        self.pm = pm
        self.marketer = marketer
        self.tech = tech
        self.design = design
        self.bus = bus
        self.config = config
        self.on_message = on_message or (lambda *args: None)

    def run(self, brief: ProductBrief) -> Scorecard:
        self._inject_brief(brief)

        rounds_completed = 0
        consensus = False

        for round_num in range(1, self.config.MAX_ROUNDS + 1):
            self._run_round(round_num, brief)
            rounds_completed = round_num

            if round_num >= self.config.MIN_ROUNDS and self._consensus_reached():
                consensus = True
                break

        return self._synthesize(brief, rounds_completed, consensus)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _inject_brief(self, brief: ProductBrief) -> None:
        intro = (
            "You are a founding team about to run a structured product validation debate. "
            "The PM has submitted the following product brief. Study it carefully — "
            "every analysis and pushback must be grounded in these specifics.\n\n"
            + brief.to_text()
        )
        self.bus.add_orchestrator_prompt(intro)

    def _run_round(self, round_num: int, brief: ProductBrief) -> None:
        agents = [
            (self.marketer, self._marketer_instruction(round_num)),
            (self.tech, self._tech_instruction(round_num)),
            (self.design, self._design_instruction(round_num)),
        ]

        for agent, instruction in agents:
            self.bus.add_orchestrator_prompt(instruction)
            msg = agent.respond(
                conversation_history=self.bus.get_history(),
                brief=brief,
                instruction=instruction,
                round_number=round_num,
            )
            self.bus.add_agent_response(msg)
            self.on_message(agent.name, msg.content, round_num)

        # PM summarizes the round
        pm_instruction = self._pm_summary_instruction(round_num)
        self.bus.add_orchestrator_prompt(pm_instruction)
        pm_msg = self.pm.respond(
            conversation_history=self.bus.get_history(),
            brief=brief,
            instruction=pm_instruction,
            round_number=round_num,
        )
        self.bus.add_agent_response(pm_msg)
        self.on_message("PM", pm_msg.content, round_num)

    def _marketer_instruction(self, round_num: int) -> str:
        if round_num == 1:
            return (
                "Round 1 — Initial Positions.\n"
                "Marketer: give your initial market analysis of this product idea. "
                "Cover market size, ICP, GTM motion, and revenue model viability."
            )
        elif round_num == self.config.MAX_ROUNDS:
            return (
                f"Round {round_num} — Final Positions.\n"
                "Marketer: this is the last round. State your final position concisely. "
                "Where were you persuaded by the team? Where do you still disagree? "
                "Keep each section to one short paragraph maximum."
            )
        else:
            last_pm = self.bus.last_pm_message() or ""
            return (
                f"Round {round_num} — Challenge & Pushback.\n"
                f"The PM summarized round {round_num - 1} as follows:\n{last_pm}\n\n"
                "Marketer: push back on the specific claims you disagree with. "
                "If you were persuaded on any point, say so and explain why. "
                "Bring new evidence or arguments — don't just repeat round 1."
            )

    def _tech_instruction(self, round_num: int) -> str:
        if round_num == 1:
            return (
                "Round 1 — Initial Positions.\n"
                "Tech Co-founder: give your initial technical feasibility analysis. "
                "Cover build complexity, stack, time-to-MVP, and the biggest technical risks."
            )
        elif round_num == self.config.MAX_ROUNDS:
            return (
                f"Round {round_num} — Final Positions.\n"
                "Tech Co-founder: state your final position. Where were you persuaded? "
                "Where do you still disagree? One short paragraph per section maximum."
            )
        else:
            return (
                f"Round {round_num} — Challenge & Pushback.\n"
                "Tech Co-founder: respond to the Marketer's points above. "
                "Address the specific technical claims being made. "
                "If the Marketer raised a market constraint that changes your technical view, "
                "acknowledge it. If not, explain why the market argument doesn't hold technically."
            )

    def _design_instruction(self, round_num: int) -> str:
        if round_num == 1:
            return (
                "Round 1 — Initial Positions.\n"
                "Design Co-founder: give your initial UX viability analysis. "
                "Cover user journey clarity, onboarding, design complexity, "
                "and how quickly a prototype could validate the core hypothesis."
            )
        elif round_num == self.config.MAX_ROUNDS:
            return (
                f"Round {round_num} — Final Positions.\n"
                "Design Co-founder: state your final position. Where were you persuaded? "
                "Where do you still disagree? One short paragraph per section maximum."
            )
        else:
            return (
                f"Round {round_num} — Challenge & Pushback.\n"
                "Design Co-founder: respond to both the Marketer and Tech Co-founder. "
                "Address any UX implications of the market segment or technical choices discussed. "
                "Push back on over-engineering. Advocate for the simplest testable version."
            )

    def _pm_summary_instruction(self, round_num: int) -> str:
        return (
            f"Round {round_num} complete.\n"
            "PM: summarize this round using your standard format. "
            "Name the specific points where the team converged and the "
            "1-2 most important unresolved disagreements going into the next round. "
            "Be precise — name the agents and the specific claims in dispute."
        )

    def _consensus_reached(self) -> bool:
        last_pm = self.bus.last_pm_message()
        if not last_pm:
            return False
        signals = [
            "consensus", "team agrees", "no major disagreements",
            "all agree", "aligned on", "converged", "agreement on",
        ]
        hits = sum(1 for s in signals if s in last_pm.lower())
        return hits >= self.config.CONSENSUS_MIN_SIGNALS

    def _synthesize(self, brief: ProductBrief, rounds_completed: int, consensus: bool) -> Scorecard:
        # Notify UI that synthesis is starting (debate messages are done, scorecard coming)
        self.on_message("__status__", "Generating final scorecard…", rounds_completed)
        synthesis_prompt = self.pm.build_synthesis_prompt(rounds_completed, consensus)
        self.bus.add_orchestrator_prompt(synthesis_prompt)
        pm_msg = self.pm.respond(
            conversation_history=self.bus.get_history(),
            brief=brief,
            instruction=synthesis_prompt,
            round_number=rounds_completed,
            max_tokens=4096,  # scorecard JSON needs more room than regular responses
        )
        self.bus.add_agent_response(pm_msg)
        return self._parse_scorecard(pm_msg.content, rounds_completed, consensus)

    def _parse_scorecard(self, json_text: str, rounds_completed: int, consensus: bool) -> Scorecard:
        # Strip markdown fences if present
        text = json_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object within text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(text[start:end])
            else:
                raise ValueError(f"Could not parse scorecard JSON from PM response:\n{json_text}")

        # New compact schema: scores are flat top-level integers (e.g. data["market_size"] = 7)
        def dim(key: str, label: str) -> DimensionScore:
            raw = data.get(key, 5)
            # Handle both compact (int) and legacy nested ({"score": int, ...}) formats
            if isinstance(raw, dict):
                score = int(raw.get("score", 5))
            else:
                score = int(raw)
            return DimensionScore(dimension=label, score=score, rationale="", risks=[])

        scorecard = Scorecard(
            market_size=dim("market_size", "Market Size"),
            icp_clarity=dim("icp_clarity", "ICP Clarity"),
            gtm_viability=dim("gtm_viability", "GTM Viability"),
            technical_feasibility=dim("technical_feasibility", "Technical Feasibility"),
            build_complexity=dim("build_complexity", "Build Complexity (ease)"),
            ux_viability=dim("ux_viability", "UX Viability"),
            user_journey_clarity=dim("user_journey_clarity", "User Journey Clarity"),
            competitive_moat=dim("competitive_moat", "Competitive Moat"),
            revenue_model_strength=dim("revenue_model_strength", "Revenue Model Strength"),
            next_actions=data.get("next_actions", []),
            go_condition=data.get("go_condition"),
            debate_rounds_completed=rounds_completed,
            consensus_reached=consensus,
        )

        # Always compute weighted average locally — don't trust model arithmetic
        scorecard.compute_overall_score()
        # Use model's verdict if provided, otherwise derive from score
        scorecard.go_no_go = data.get("go_no_go") or scorecard.compute_verdict()

        return scorecard

