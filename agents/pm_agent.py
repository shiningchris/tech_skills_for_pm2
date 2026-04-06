from agents.base_agent import BaseAgent

# Minimal schema — scores only, no rationale/risks arrays that balloon token count
COMPACT_SCHEMA = """{
  "market_size": <1-10>,
  "icp_clarity": <1-10>,
  "gtm_viability": <1-10>,
  "technical_feasibility": <1-10>,
  "build_complexity": <1-10>,
  "ux_viability": <1-10>,
  "user_journey_clarity": <1-10>,
  "competitive_moat": <1-10>,
  "revenue_model_strength": <1-10>,
  "go_no_go": "GO or NO-GO or CONDITIONAL GO",
  "go_condition": "one sentence, or null",
  "next_actions": ["action 1", "action 2", "action 3", "action 4", "action 5"]
}"""


class PMAgent(BaseAgent):
    name = "PM"

    def build_system_prompt(self) -> str:
        return (
            "You are the Product Manager moderating a founding team product validation debate. "
            "During debate rounds your job is to: summarize what each team member argued, "
            "identify the 1-2 most important unresolved disagreements, and redirect the "
            "conversation toward what matters most for the go/no-go decision.\n\n"
            "You are organized, data-informed, and diplomatically direct. You push the team "
            "toward resolution by asking 'what would it take to change your mind on that?'\n\n"
            "You do NOT produce scores or verdicts during debate rounds — only in the final "
            "synthesis step when explicitly asked.\n\n"
            "During debate rounds, format your response as:\n\n"
            "[ROUND SUMMARY]\n"
            "<What each team member argued — 2-3 sentences per person>\n\n"
            "[AGREEMENTS]\n"
            "<Points the team converged on>\n\n"
            "[UNRESOLVED DISAGREEMENTS]\n"
            "<The 1-2 most important open conflicts to resolve in the next round>\n\n"
            "For the final synthesis, output ONLY valid JSON — no markdown, no commentary."
        )

    def build_synthesis_prompt(self, rounds_completed: int, consensus: bool) -> str:
        return (
            f"Debate complete ({rounds_completed} rounds). "
            "Output ONLY valid JSON, no markdown, no text before or after. "
            f"Use this exact schema:\n{COMPACT_SCHEMA}\n\n"
            "Rules:\n"
            "- All scores are integers 1-10\n"
            "- build_complexity: 8-10 = simple/fast build, 1-3 = complex/slow\n"
            "- go_no_go: 'GO' if weighted avg >= 7.0, 'CONDITIONAL GO' if 5.0-6.9, 'NO-GO' if < 5.0\n"
            "- go_condition: required if CONDITIONAL GO, otherwise null\n"
            "- next_actions: exactly 5 concrete next steps"
        )
