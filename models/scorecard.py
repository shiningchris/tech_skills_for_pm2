from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class DimensionScore:
    dimension: str
    score: int  # 1-10
    rationale: str
    risks: List[str] = field(default_factory=list)


@dataclass
class NextAction:
    action: str
    owner: str  # "PM" | "Marketer" | "Tech Co-founder" | "Design Co-founder"


@dataclass
class LeanCanvas:
    problem: str = ""
    customer_segments: str = ""
    early_adopter: str = ""
    unique_value_prop: str = ""
    solution: str = ""
    channels: str = ""
    revenue_streams: str = ""
    cost_structure: str = ""
    key_metrics: str = ""
    unfair_advantage: str = ""


@dataclass
class Scorecard:
    # Per-agent dimensions
    market_size: DimensionScore = None
    icp_clarity: DimensionScore = None
    gtm_viability: DimensionScore = None
    technical_feasibility: DimensionScore = None
    build_complexity: DimensionScore = None
    ux_viability: DimensionScore = None
    user_journey_clarity: DimensionScore = None
    competitive_moat: DimensionScore = None
    revenue_model_strength: DimensionScore = None

    overall_score: float = 0.0
    go_no_go: str = "NO-GO"  # "GO" | "NO-GO" | "CONDITIONAL GO"
    go_condition: Optional[str] = None
    next_actions: List[NextAction] = field(default_factory=list)
    lean_canvas: Optional[LeanCanvas] = None
    debate_rounds_completed: int = 0
    consensus_reached: bool = False

    WEIGHTS: dict = field(default_factory=lambda: {
        "market_size": 0.20,
        "technical_feasibility": 0.20,
        "icp_clarity": 0.10,
        "gtm_viability": 0.10,
        "build_complexity": 0.10,
        "ux_viability": 0.10,
        "competitive_moat": 0.10,
        "user_journey_clarity": 0.05,
        "revenue_model_strength": 0.05,
    })

    def compute_overall_score(self) -> float:
        total = 0.0
        dimensions = {
            "market_size": self.market_size,
            "technical_feasibility": self.technical_feasibility,
            "icp_clarity": self.icp_clarity,
            "gtm_viability": self.gtm_viability,
            "build_complexity": self.build_complexity,
            "ux_viability": self.ux_viability,
            "competitive_moat": self.competitive_moat,
            "user_journey_clarity": self.user_journey_clarity,
            "revenue_model_strength": self.revenue_model_strength,
        }
        for key, dim in dimensions.items():
            if dim is not None:
                total += dim.score * self.WEIGHTS.get(key, 0)
        self.overall_score = round(total, 1)
        return self.overall_score

    def compute_verdict(self) -> str:
        if self.overall_score >= 7.0:
            self.go_no_go = "GO"
        elif self.overall_score >= 5.0:
            self.go_no_go = "CONDITIONAL GO"
        else:
            self.go_no_go = "NO-GO"
        return self.go_no_go
