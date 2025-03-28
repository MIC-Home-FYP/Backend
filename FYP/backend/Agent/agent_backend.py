import json
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from pyprojroot import here
from DBLogic import DBLogic

db = DBLogic()
class State(TypedDict):
    """Represents the state structure containing a list of messages.

    Attributes:
        messages (list): A list of messages, where each message can be processed
        by adding messages using the `add_messages` function.
    """
    messages: Annotated[list, add_messages]
    context: str
    user_id: int
    care_plan: str

def retrieve_context(state: State):
    """Node to fetch context from MySQL database"""
    user_id = state.get('user_id')
    chat_history = db.get_recent_user_conversations(user_id)
    # Format chat history as context
    context = "\n".join([f"{row['sender']}: {row['message']} ({row['timestamp']})" for row in chat_history])
    care_plan_path = f"FYP/backend/docs/Careplan/user_{user_id}.txt"
    try:
        with(open(here(care_plan_path, 'r'))) as file:
            care_plan = file.read().strip()
    except FileNotFoundError:
        care_plan = "No care plan found for this user."         
    return {"context": context, "care_plan": care_plan}



class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage.

    This class retrieves tool calls from the most recent AIMessage in the input
    and invokes the corresponding tool to generate responses.

    Attributes:
        tools_by_name (dict): A dictionary mapping tool names to tool instances.
    """

    def __init__(self, tools: list) -> None:
        """Initializes the BasicToolNode with available tools.

        Args:
            tools (list): A list of tool objects, each having a `name` attribute.
        """
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        """Executes the tools based on the tool calls in the last message.

        Args:
            inputs (dict): A dictionary containing the input state with messages.

        Returns:
            dict: A dictionary with a list of `ToolMessage` outputs.

        Raises:
            ValueError: If no messages are found in the input.
        """
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

def route_tools(state: State) -> Literal["rag_tools", "search_tool", "supervisor"]:
    if isinstance(state, dict):
        messages = state.get("messages", [])
    elif isinstance(state, list):
        messages = state
    else:
        raise ValueError(f"Unexpected state type: {type(state)}")

    if not messages:
        raise ValueError("No messages found in input state")

    last_message = messages[-1]
    if not last_message.tool_calls:
        return "supervisor"
    elif last_message.tool_calls == "search_tool":
        return "search_tool"
    else:
        return "rag_tools"


def plot_agent_schema(graph):
    """Plots the agent schema using a graph object, if possible.

    Tries to display a visual representation of the agent's graph schema
    using Mermaid format and IPython's display capabilities. If the required
    dependencies are missing, it catches the exception and prints a message
    instead.

    Args:
        graph: A graph object that has a `get_graph` method, returning a graph
        structure that supports Mermaid diagram generation.

    Returns:
        None
    """
    try:
        display(Image(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API,output_file_path="my_graph_mermaid.png")))
    except Exception:
        # This requires some extra dependencies and is optional
        return print("Graph could not be displayed.")