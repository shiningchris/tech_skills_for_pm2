import json

from agents.pm_agent import PMAgent
from agents.marketer_agent import MarketerAgent
from agents.tech_agent import TechAgent
from agents.design_agent import DesignAgent
from config import Config
from models.brief import ProductBrief
from models.scorecard import DimensionScore, LeanCanvas, NextAction, Scorecard
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

        scorecard = self._synthesize(brief, rounds_completed, consensus)
        scorecard.lean_canvas = self._synthesize_lean_canvas(brief, rounds_completed)
        return scorecard

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
        self.on_message("__status__", "Generating scorecard…", rounds_completed)
        synthesis_prompt = self.pm.build_synthesis_prompt(rounds_completed, consensus)
        self.bus.add_orchestrator_prompt(synthesis_prompt)
        pm_msg = self.pm.respond(
            conversation_history=self.bus.get_history(),
            brief=brief,
            instruction=synthesis_prompt,
            round_number=rounds_completed,
            max_tokens=1024,
        )
        self.bus.add_agent_response(pm_msg)
        return self._parse_scorecard(pm_msg.content, rounds_completed, consensus)

    def _synthesize_lean_canvas(self, brief: ProductBrief, rounds_completed: int) -> LeanCanvas:
        self.on_message("__status__", "Building Lean Canvas…", rounds_completed)

        from agents.pm_agent import LEAN_CANVAS_SCHEMA

        # Use a FRESH minimal conversation — not the full debate history.
        # The full history (12+ long messages) makes JSON output unreliable.
        last_pm_summary = self.bus.last_pm_message() or ""
        user_content = (
            f"{brief.to_text()}\n\n"
            f"TEAM FINAL SUMMARY:\n{last_pm_summary[:1500]}\n\n"
            "Based on the product brief and team summary above, output ONLY valid JSON "
            "with no markdown and no text before or after, using this exact schema:\n"
            f"{LEAN_CANVAS_SCHEMA}\n\n"
            "Rules:\n"
            "- early_adopter: specific job title, company stage, pain trigger, WTP signal\n"
            "- channels: reference the specific early_adopter profile\n"
            "- key_metrics: measurable leading indicators, not vanity metrics\n"
            "- unfair_advantage: honest — if none yet, say so"
        )
        system = (
            "You are a product strategist. Output ONLY a valid JSON object. "
            "No markdown fences, no explanation, no text outside the JSON."
        )

        for attempt in range(2):
            try:
                response = self.pm.client.messages.create(
                    model=self.pm.config.MODEL_NAME,
                    max_tokens=2048,
                    temperature=0.3,
                    system=system,
                    messages=[{"role": "user", "content": user_content}],
                )
                raw = response.content[0].text
                print(f"[LEAN CANVAS attempt {attempt+1}] raw[:400]:\n{raw[:400]}", flush=True)
                canvas = self._parse_lean_canvas(raw)
                if not any([canvas.problem, canvas.customer_segments, canvas.early_adopter,
                            canvas.unique_value_prop, canvas.solution]):
                    raise ValueError("All key fields are empty after parsing")
                return canvas
            except Exception as exc:
                print(f"[LEAN CANVAS attempt {attempt+1} FAILED]: {exc}", flush=True)
                if attempt == 0:
                    self.on_message("__status__", "Lean Canvas retry…", rounds_completed)

        self.on_message("__status__", "Lean Canvas could not be generated.", rounds_completed)
        return LeanCanvas()

    def _parse_scorecard(self, json_text: str, rounds_completed: int, consensus: bool) -> Scorecard:
        data = self._extract_json(json_text)

        def dim(key: str, label: str) -> DimensionScore:
            raw = data.get(key, 5)
            if isinstance(raw, dict):
                score = int(raw.get("score", 5))
            else:
                score = int(raw)
            return DimensionScore(dimension=label, score=score, rationale="", risks=[])

        # Parse next_actions — support both old (list of str) and new (list of {action, owner})
        raw_actions = data.get("next_actions", [])
        next_actions = []
        for item in raw_actions:
            if isinstance(item, dict):
                next_actions.append(NextAction(
                    action=item.get("action", ""),
                    owner=item.get("owner", "PM"),
                ))
            else:
                next_actions.append(NextAction(action=str(item), owner="PM"))

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
            next_actions=next_actions,
            go_condition=data.get("go_condition"),
            debate_rounds_completed=rounds_completed,
            consensus_reached=consensus,
        )

        scorecard.compute_overall_score()
        scorecard.go_no_go = data.get("go_no_go") or scorecard.compute_verdict()
        return scorecard

    def _parse_lean_canvas(self, json_text: str) -> LeanCanvas:
        try:
            data = self._extract_json(json_text)
            return LeanCanvas(
                problem=data.get("problem", ""),
                customer_segments=data.get("customer_segments", ""),
                early_adopter=data.get("early_adopter", ""),
                unique_value_prop=data.get("unique_value_prop", ""),
                solution=data.get("solution", ""),
                channels=data.get("channels", ""),
                revenue_streams=data.get("revenue_streams", ""),
                cost_structure=data.get("cost_structure", ""),
                key_metrics=data.get("key_metrics", ""),
                unfair_advantage=data.get("unfair_advantage", ""),
            )
        except Exception:
            raise  # bubble up so _synthesize_lean_canvas can report the error

    def _extract_json(self, text: str) -> dict:
        import re
        text = text.strip()
        # Strip markdown code fences
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        # Isolate the first {...} block (handles preamble text)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        # Clean common LLM JSON mistakes: trailing commas before } or ]
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Could not parse JSON ({exc}):\n{text[:300]}")
