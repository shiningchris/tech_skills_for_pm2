from dataclasses import dataclass


@dataclass
class ProductBrief:
    idea_title: str
    problem_statement: str
    proposed_solution: str
    target_user: str
    revenue_model: str
    known_competitors: str
    stage: str  # "idea" | "prototype" | "mvp" | "live"

    def to_text(self) -> str:
        return (
            f"PRODUCT BRIEF\n"
            f"=============\n"
            f"Idea: {self.idea_title}\n"
            f"Stage: {self.stage}\n\n"
            f"Problem: {self.problem_statement}\n\n"
            f"Solution: {self.proposed_solution}\n\n"
            f"Target User: {self.target_user}\n\n"
            f"Revenue Model: {self.revenue_model}\n\n"
            f"Known Competitors: {self.known_competitors}\n"
        )
