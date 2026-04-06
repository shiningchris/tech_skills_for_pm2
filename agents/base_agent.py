from abc import ABC, abstractmethod

import anthropic

from config import Config
from models.brief import ProductBrief
from models.message import AgentMessage


class BaseAgent(ABC):
    name: str

    def __init__(self, client: anthropic.Anthropic, config: Config):
        self.client = client
        self.config = config
        self.system_prompt = self.build_system_prompt()

    @abstractmethod
    def build_system_prompt(self) -> str:
        """Return the system prompt that defines this agent's persona."""
        ...

    def respond(
        self,
        conversation_history: list[dict],
        brief: ProductBrief,
        instruction: str,
        round_number: int,
    ) -> AgentMessage:
        """
        Call the Anthropic API with the full shared conversation history.
        The instruction is NOT appended here — it must already be the last
        message in conversation_history (added by the orchestrator).
        """
        response = self.client.messages.create(
            model=self.config.MODEL_NAME,
            max_tokens=self.config.MAX_TOKENS_PER_RESPONSE,
            temperature=self.config.TEMPERATURE,
            system=self.system_prompt,
            messages=conversation_history,
        )
        content = response.content[0].text
        return AgentMessage(
            agent_name=self.name,
            content=content,
            round_number=round_number,
        )
