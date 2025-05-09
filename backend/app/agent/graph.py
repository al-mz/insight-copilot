"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from backend.power_sim_agent.configuration import Configuration
from backend.power_sim_agent.state import AgentState, InputState
from backend.power_sim_agent.tools import TOOLS
from backend.power_sim_agent.utils import load_chat_model


# Define the function that calls the model
async def call_model(state: AgentState) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_context()

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(configuration.model).bind_tools(TOOLS)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke([{"role": "system", "content": system_message}, *state.messages]),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}


# Define a new graph
builder = StateGraph(AgentState, input=InputState, config_schema=Configuration)

# Define the two nodes we will cycle between
builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))

# Set the entrypoint as `call_model`
# This means that this node is the first one called
builder.add_edge("__start__", "call_model")


def route_model_output(state: AgentState) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(f"Expected AIMessage in output edges, but got {type(last_message).__name__}")
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"


# Add a conditional edge to determine the next step after `call_model`
builder.add_conditional_edges(
    "call_model",
    # After call_model finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    route_model_output,
)

# Add a normal edge from `tools` to `call_model`
# This creates a cycle: after using tools, we always return to the model
builder.add_edge("tools", "call_model")

# Compile the builder into an executable graph
memory = MemorySaver()
graph = builder.compile(name="powersim_agent", checkpointer=memory)

if __name__ == "__main__":
    import asyncio

    from langchain_core.messages import HumanMessage

    async def main():
        # Define the input using proper message format
        input_data = {
            "messages": [
                # HumanMessage(content="What are the available signal types in the database?")
                HumanMessage(content="Can you plot V_MV for case 04_LVRT_Lead_Preferred_01 from 5 to 10 seconds?"),
            ]
        }

        config = {
            "configurable": {
                "thread_id": "12345",
            }
        }

        # Stream the execution to see what's happening inside
        print("\n=== STARTING AGENT EXECUTION ===\n")

        # Use astream to see intermediate steps
        async for chunk in graph.astream(input_data, config, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                print(f"\n--- OUTPUT FROM NODE: {node_name} ---")

                # Extract messages if they exist
                if "messages" in node_output and node_output["messages"]:
                    latest_message = node_output["messages"][-1]

                    # Print message content based on type
                    print(f"MESSAGE TYPE: {type(latest_message).__name__}")

                    if hasattr(latest_message, "content") and latest_message.content:
                        print(f"CONTENT: {latest_message.content[:500]}...")

                    # Print tool calls if present
                    if hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
                        print(f"TOOL CALLS: {latest_message.tool_calls}")

                    # Handle tool messages specifically
                    if hasattr(latest_message, "name") and hasattr(latest_message, "tool_call_id"):
                        print(f"TOOL: {latest_message.name}")
                        print(f"TOOL CALL ID: {latest_message.tool_call_id}")
                        if hasattr(latest_message, "content"):
                            print(f"RESULT: {latest_message.content[:500]}...")

                print("-----------------------------------")

            print("\n==== CHUNK COMPLETE ====\n")

        # Get the final response
        final_response = await graph.ainvoke(input_data, config)

        print("\n=== FINAL RESPONSE ===\n")
        print(final_response)

    # Run the async main function
    asyncio.run(main())
