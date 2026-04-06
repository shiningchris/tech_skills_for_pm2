from agents.base_agent import BaseAgent

SCORECARD_SCHEMA = """
{
  "scores": {
    "market_size":              { "score": <1-10>, "rationale": "<one sentence>", "risks": ["<risk>", "..."] },
    "icp_clarity":              { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "gtm_viability":            { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "technical_feasibility":    { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "build_complexity":         { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "ux_viability":             { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "user_journey_clarity":     { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "competitive_moat":         { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] },
    "revenue_model_strength":   { "score": <1-10>, "rationale": "<one sentence>", "risks": ["..."] }
  },
  "overall_score": <float>,
  "go_no_go": "<GO|NO-GO|CONDITIONAL GO>",
  "go_condition": "<string or null>",
  "next_actions": ["<action 1>", "...", "<up to 7 actions>"],
  "debate_rounds_completed": <int>,
  "consensus_reached": <true|false>
}
"""


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
            "For the final synthesis, you will be given explicit JSON schema instructions "
            "and must output ONLY valid JSON — no markdown, no commentary."
        )

    def build_synthesis_prompt(self, rounds_completed: int, consensus: bool) -> str:
        return (
            f"The debate is complete ({rounds_completed} rounds, "
            f"consensus_reached={consensus}). "
            "Based on everything the team discussed, produce the final validation scorecard. "
            "Output ONLY valid JSON — no markdown fences, no commentary before or after. "
            f"Use exactly this schema:\n{SCORECARD_SCHEMA}\n\n"
            "Scoring notes:\n"
            "- build_complexity: score HIGH (8-10) if the build is SIMPLE/fast, LOW (1-3) if complex\n"
            "- overall_score: compute as the weighted average using these weights: "
            "market_size=0.20, technical_feasibility=0.20, icp_clarity=0.10, "
            "gtm_viability=0.10, build_complexity=0.10, ux_viability=0.10, "
            "competitive_moat=0.10, user_journey_clarity=0.05, revenue_model_strength=0.05\n"
            "- go_no_go: 'GO' if overall>=7.0, 'CONDITIONAL GO' if 5.0-6.9, 'NO-GO' if <5.0\n"
            "- go_condition: required string if CONDITIONAL GO, null otherwise\n"
            "- next_actions: 3-7 concrete, ordered actions the PM should take next"
        )
