from models.scorecard import Scorecard
from orchestrator.message_bus import MessageBus

AGENT_COLORS = {
    "Marketer": "\033[36m",           # Cyan
    "Tech Co-founder": "\033[33m",    # Yellow
    "Design Co-founder": "\033[35m",  # Magenta
    "PM": "\033[32m",                 # Green
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class OutputFormatter:

    def print_round_header(self, round_num: int) -> None:
        print(f"\n{BOLD}{'═' * 60}{RESET}")
        print(f"{BOLD}  ROUND {round_num}{RESET}")
        print(f"{BOLD}{'═' * 60}{RESET}\n")

    def print_agent_message(self, agent_name: str, content: str, round_num: int) -> None:
        color = AGENT_COLORS.get(agent_name, "")
        print(f"{color}{BOLD}[{agent_name.upper()}]{RESET}")
        for line in content.split("\n"):
            print(f"  {line}")
        print()

    def print_debate_transcript(self, bus: MessageBus, max_rounds: int) -> None:
        """Print the full debate transcript grouped by round."""
        print(f"\n{BOLD}{'═' * 60}{RESET}")
        print(f"{BOLD}  DEBATE TRANSCRIPT{RESET}")
        print(f"{BOLD}{'═' * 60}{RESET}")

        for round_num in range(1, max_rounds + 1):
            messages = bus.get_round_messages(round_num)
            if not messages:
                break
            self.print_round_header(round_num)
            for msg in messages:
                self.print_agent_message(msg.agent_name, msg.content, round_num)

    def print_scorecard(self, scorecard: Scorecard, idea_title: str) -> None:
        print(f"\n{BOLD}{'╔' + '═' * 58 + '╗'}{RESET}")
        print(f"{BOLD}{'║':1}{'  PRODUCT VALIDATION SCORECARD':^58}{'║':1}{RESET}")
        print(f"{BOLD}{'╚' + '═' * 58 + '╝'}{RESET}\n")

        print(f"  {BOLD}Idea:{RESET} {idea_title}")
        print(f"  {DIM}Rounds: {scorecard.debate_rounds_completed} | "
              f"Consensus: {'yes' if scorecard.consensus_reached else 'no'}{RESET}\n")

        print(f"  {BOLD}{'DIMENSION':<30} {'SCORE':>5}   {'RATIONALE'}{RESET}")
        print(f"  {'─' * 70}")

        dimensions = [
            scorecard.market_size,
            scorecard.icp_clarity,
            scorecard.gtm_viability,
            scorecard.technical_feasibility,
            scorecard.build_complexity,
            scorecard.ux_viability,
            scorecard.user_journey_clarity,
            scorecard.competitive_moat,
            scorecard.revenue_model_strength,
        ]

        for dim in dimensions:
            if dim is None:
                continue
            score_bar = self._score_bar(dim.score)
            rationale_short = dim.rationale[:45] + "..." if len(dim.rationale) > 45 else dim.rationale
            print(f"  {dim.dimension:<30} {dim.score:>2}/10  {score_bar}  {DIM}{rationale_short}{RESET}")

        print(f"  {'─' * 70}")
        print(f"  {BOLD}{'OVERALL SCORE':<30} {scorecard.overall_score:>4.1f}/10{RESET}\n")

        verdict_color, verdict_symbol = self._verdict_style(scorecard.go_no_go)
        print(f"  {verdict_color}{BOLD}┌{'─' * 50}┐{RESET}")
        print(f"  {verdict_color}{BOLD}│  VERDICT: {verdict_symbol} {scorecard.go_no_go:<38}│{RESET}")
        if scorecard.go_condition:
            cond = scorecard.go_condition[:44]
            print(f"  {verdict_color}{BOLD}│  Condition: {cond:<37}│{RESET}")
        print(f"  {verdict_color}{BOLD}└{'─' * 50}┘{RESET}\n")

        if scorecard.next_actions:
            print(f"  {BOLD}NEXT ACTIONS:{RESET}")
            for i, action in enumerate(scorecard.next_actions, 1):
                print(f"  {i}. {action}")

        print()

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _score_bar(self, score: int) -> str:
        filled = round(score / 10 * 8)
        return "[" + "█" * filled + "░" * (8 - filled) + "]"

    def _verdict_style(self, verdict: str):
        if verdict == "GO":
            return "\033[32m", "✦"    # Green
        elif verdict == "NO-GO":
            return "\033[31m", "✗"    # Red
        else:
            return "\033[33m", "◈"    # Yellow — CONDITIONAL GO
