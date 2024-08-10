from langchain_core.messages import BaseMessage

from bale_of_turtles import use_state
from bale_of_turtles.tool_turtle import TurtleTool


class ChatTurtle(TurtleTool):

    def register(self, state):
        super().register(state)
        state.update_state(turtle_llm_message_history=[])

    @use_state(
        "llm-message-changed",
        ["turtle_human_message", "turtle_ai_message", "turtle_system_message"],
    )
    def message_added(
        self,
        turtle_human_message: BaseMessage | None = None,
        turtle_ai_message: BaseMessage | None = None,
        turtle_system_message: BaseMessage | None = None,
        turtle_llm_message_history: list[BaseMessage] | None = None,
        *args,
        **kwargs,
    ):
        message = next(
            filter(
                None, [turtle_human_message, turtle_ai_message, turtle_system_message]
            ),
            None,
        )
        if message is not None:
            turtle_llm_message_history.append(message)
