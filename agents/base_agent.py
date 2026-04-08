from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import List

import anthropic

from config import Config
from models.brief import ProductBrief
from models.message import AgentMessage

MAX_CONTINUATIONS = 3  # safety cap on follow-up calls
MAX_RETRIES = 4        # retries on 529 overloaded


class BaseAgent(ABC):
    name: str

    def __init__(self, client: anthropic.Anthropic, config: Config):
        self.client = client
        self.config = config
        self.system_prompt = self.build_system_prompt()

    @abstractmethod
    def build_system_prompt(self) -> str: ...

    def _call_api(self, history: list, limit: int) -> anthropic.types.Message:
        """Call the API with exponential backoff on 529 overloaded errors."""
        delay = 10  # seconds — start longer since overload takes time to clear
        for attempt in range(MAX_RETRIES):
            try:
                return self.client.messages.create(
                    model=self.config.MODEL_NAME,
                    max_tokens=limit,
                    temperature=self.config.TEMPERATURE,
                    system=self.system_prompt,
                    messages=history,
                )
            except anthropic.APIStatusError as exc:
                if exc.status_code == 529 and attempt < MAX_RETRIES - 1:
                    print(f"[API 529 overloaded] waiting {delay}s before retry {attempt + 1}/{MAX_RETRIES - 1}…", flush=True)
                    time.sleep(delay)
                    delay *= 2  # 10s → 20s → 40s → 80s
                else:
                    raise

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
        Retries up to MAX_RETRIES times on 529 overloaded errors.
        """
        limit = max_tokens or self.config.MAX_TOKENS_PER_RESPONSE
        history = list(conversation_history)  # local copy we can extend

        full_text = ""
        for attempt in range(1 + MAX_CONTINUATIONS):
            response = self._call_api(history, limit)
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
