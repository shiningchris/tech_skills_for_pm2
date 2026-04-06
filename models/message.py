from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMessage:
    agent_name: str
    content: str
    round_number: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
