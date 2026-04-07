from dataclasses import dataclass, field


@dataclass
class Config:
    MODEL_NAME: str = "claude-sonnet-4-6"
    MAX_ROUNDS: int = 3
    MIN_ROUNDS: int = 2
    MAX_TOKENS_PER_RESPONSE: int = 2048
    TEMPERATURE: float = 0.7
    CONSENSUS_MIN_SIGNALS: int = 2
    OUTPUT_DIR: str = "./output"

    GO_THRESHOLD: float = 7.0
    CONDITIONAL_THRESHOLD: float = 5.0
