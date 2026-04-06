import os
import sys

import anthropic
from dotenv import load_dotenv

from agents import PMAgent, MarketerAgent, TechAgent, DesignAgent
from config import Config
from models.brief import ProductBrief
from orchestrator.message_bus import MessageBus
from orchestrator.debate_loop import DebateOrchestrator
from output.formatter import OutputFormatter
from output.exporter import Exporter

load_dotenv()

BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def print_banner() -> None:
    print(f"""
{BOLD}╔══════════════════════════════════════════════════════════╗
║       PRODUCT VALIDATION SPRINT — Multi-Agent Debate     ║
║  Marketer · Tech Co-founder · Design Co-founder · PM     ║
╚══════════════════════════════════════════════════════════╝{RESET}

{DIM}The PM submits a product idea. Three founding team agents
debate it across 2-3 rounds. The PM synthesizes a Go/No-Go
scorecard with next actions.{RESET}
""")


def collect_brief() -> ProductBrief:
    print(f"{BOLD}Tell us about your product idea:{RESET}\n")

    def ask(prompt: str, hint: str = "") -> str:
        hint_str = f" {DIM}(e.g. {hint}){RESET}" if hint else ""
        value = input(f"  {prompt}{hint_str}\n  > ").strip()
        while not value:
            value = input(f"  {BOLD}(required){RESET} {prompt}\n  > ").strip()
        print()
        return value

    idea_title = ask(
        "Idea title:",
        "AI expense tracker for solopreneurs"
    )
    problem_statement = ask(
        "What problem does it solve?",
        "Solopreneurs waste hours manually tracking expenses and preparing tax reports"
    )
    proposed_solution = ask(
        "What does the product do?",
        "Snap a photo of any receipt; AI categorizes it and generates monthly reports"
    )
    target_user = ask(
        "Who is the primary user?",
        "Solopreneurs and freelancers in the US, earning $50k-$200k/year"
    )
    revenue_model = ask(
        "How does it make money?",
        "Freemium with a $12/month Pro tier for unlimited receipts and tax export"
    )
    known_competitors = ask(
        "Known competitors or alternatives?",
        "Expensify, Wave, Excel spreadsheets"
    )
    stage = ask(
        "Current stage? (idea / prototype / mvp / live)",
        "idea"
    ).lower()
    if stage not in ("idea", "prototype", "mvp", "live"):
        stage = "idea"

    return ProductBrief(
        idea_title=idea_title,
        problem_statement=problem_statement,
        proposed_solution=proposed_solution,
        target_user=target_user,
        revenue_model=revenue_model,
        known_competitors=known_competitors,
        stage=stage,
    )


def main() -> None:
    print_banner()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: ANTHROPIC_API_KEY environment variable is not set.\n"
            "Set it with: export ANTHROPIC_API_KEY=sk-ant-..."
        )

    brief = collect_brief()

    print(f"{BOLD}Starting validation sprint...{RESET}")
    print(f"{DIM}This will take ~60-90 seconds depending on debate length.{RESET}\n")

    config = Config()
    client = anthropic.Anthropic(api_key=api_key)

    pm = PMAgent(client, config)
    marketer = MarketerAgent(client, config)
    tech = TechAgent(client, config)
    design = DesignAgent(client, config)

    bus = MessageBus()
    formatter = OutputFormatter()

    current_round = [0]

    def on_message(agent_name: str, content: str, round_num: int) -> None:
        if round_num != current_round[0]:
            current_round[0] = round_num
            formatter.print_round_header(round_num)
        formatter.print_agent_message(agent_name, content, round_num)

    orchestrator = DebateOrchestrator(
        pm=pm,
        marketer=marketer,
        tech=tech,
        design=design,
        bus=bus,
        config=config,
        on_message=on_message,
    )

    scorecard = orchestrator.run(brief)

    formatter.print_scorecard(scorecard, brief.idea_title)

    exporter = Exporter(output_dir=config.OUTPUT_DIR)
    json_path = exporter.save_json(scorecard, brief)
    md_path = exporter.save_markdown(scorecard, brief, bus)

    print(f"{DIM}Saved to:{RESET}")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}\n")


if __name__ == "__main__":
    main()
