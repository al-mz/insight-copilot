# Define agent state
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Sequence

from copilotkit import CopilotKitState  # noqa: F401
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps


def merge_lists(a: list, b: list) -> list:
    """Merge two lists by extending the first with the second"""
    return [*a, *b] if isinstance(a, list) and isinstance(b, list) else b


@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """


@dataclass
class AgentState(InputState):
    data: Annotated[List[Dict[str, Any]], merge_lists] = field(default_factory=list)
    remaining_steps: RemainingSteps = 25
    is_last_step: IsLastStep = field(default=False)

    def items(self):
        """Make AgentState behave like a dictionary for CopilotKit compatibility.

        This method returns key-value pairs for all attributes in the dataclass.
        """
        return self.__dict__.items()

    def __getitem__(self, key):
        """Support dictionary-like access."""
        return getattr(self, key)

    def get(self, key, default=None):
        """Provide dictionary-like get method with default support."""
        return getattr(self, key, default)
