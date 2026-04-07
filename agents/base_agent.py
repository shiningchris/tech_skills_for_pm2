from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import anthropic

from config import Config
from models.brief import ProductBrief
from models.message import AgentMessage

MAX_CONTINUATIONS = 3  # safety cap on follow-up calls


class BaseAgent(ABC):
    name: str

    def __init__(self, client: anthropic.Anthropic, config: Config):
        self.client = client
        self.config = config
        self.system_prompt = self.build_system_prompt()

    @abstractmethod
    def build_system_prompt(self) -> str: ...

    def respond(
        self,
        conversation_history: List[dict],
        brief: ProductBrief,
        instruction: str,
        round_number: int,
        max_tokens: int = None,
    ) -> AgentMessage:
        """
        Call the API and automatically continue if the response is cut off
        (stop_reason == 'max_tokens'). Appends continuation calls until the
        model signals end_turn or MAX_CONTINUATIONS is reached.
        """
        limit = max_tokens or self.config.MAX_TOKENS_PER_RESPONSE
        history = list(conversation_history)  # local copy we can extend

        full_text = ""
        for attempt in range(1 + MAX_CONTINUATIONS):
            response = self.client.messages.create(
                model=self.config.MODEL_NAME,
                max_tokens=limit,
                temperature=self.config.TEMPERATURE,
                system=self.system_prompt,
                messages=history,
            )
            chunk = response.content[0].text
            full_text += chunk

            if response.stop_reason != "max_tokens":
                break  # finished naturally

            # Response was cut — ask the model to continue exactly where it left off
            history.append({"role": "assistant", "content": full_text})
            history.append({"role": "user",      "content": "Continue exactly where you left off."})

        return AgentMessage(
            agent_name=self.name,
            content=full_text,
            round_number=round_number,
        )
