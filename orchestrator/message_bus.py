from models.message import AgentMessage


class MessageBus:
    """
    Maintains the single shared conversation thread used by ALL agents.
    Every agent sees the full history — this is what makes debate feel real.

    The Anthropic API requires strictly alternating user/assistant roles.
    The orchestrator injects a user-role prompt before each agent response
    to maintain valid alternation.
    """

    def __init__(self):
        self.history: list[dict] = []           # [{role, content}] for Anthropic API
        self.agent_messages: list[AgentMessage] = []  # Typed log for export/display

    def add_orchestrator_prompt(self, content: str) -> None:
        """Append a user-role orchestrator instruction to the shared thread."""
        self.history.append({"role": "user", "content": content})

    def add_agent_response(self, message: AgentMessage) -> None:
        """
        Append an agent's response as assistant-role, prefixed with agent name
        so all subsequent agents know who said what.
        """
        prefixed = f"[{message.agent_name.upper()}]:\n{message.content}"
        self.history.append({"role": "assistant", "content": prefixed})
        self.agent_messages.append(message)

    def get_history(self) -> list[dict]:
        """Return a copy of the full conversation history."""
        return list(self.history)

    def get_round_messages(self, round_num: int) -> list[AgentMessage]:
        return [m for m in self.agent_messages if m.round_number == round_num]

    def last_pm_message(self) -> str | None:
        for msg in reversed(self.agent_messages):
            if msg.agent_name == "PM":
                return msg.content
        return None
