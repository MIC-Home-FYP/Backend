from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langchain_groq import ChatGroq
from Agent.RAG_tool import lookup_jaundice, lookup_dengue
from Agent.load_tools_config import LoadToolsConfig
from Agent.agent_backend import State, BasicToolNode, route_tools, plot_agent_schema
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pyprojroot import here
import os

load_dotenv()

os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')
TOOL_CFG = LoadToolsConfig()

def build_graph():
    """
    Builds an agent decision-making graph by combining an LLM with various tools
    and defining the flow of interactions between them.

    This function sets up a state graph where a primary language model (LLM) interacts
    with several predefined tools (e.g., databases, search functions).
    The agent can invoke tools based on conditions and use their outputs to inform
    further decisions. The flow involves conditional tool invocation, returning back
    to the chatbot after tool execution to guide the next step.

    Steps:
    1. Initializes the primary language model (LLM) with tool-binding functionality.
    2. Defines nodes in the graph where each node represents a specific action:
       - Chatbot node: Executes the LLM with the given state and messages.
       - Tools node: Runs the tool invocations based on the last message in the input state.
    3. Implements conditional routing between the chatbot and tools:
       - If a tool is required, it routes to the tools node.
       - Otherwise, the flow ends.
    4. Establishes connections between the chatbot and tools nodes to form the agent loop.
    5. Uses a memory-saving mechanism to track and save checkpoints in the graph.

    Returns:
        graph (StateGraph): The compiled state graph that represents the decision-making process
        of the agent, integrating the chatbot, tools, and conditional routing.

    Components:
        - `primary_llm`: The primary language model responsible for generating responses.
        - `tools`: A list of tools including SQL queries, search functionalities, knowledge base lookups, etc.
        - `tool_node`: A node responsible for handling tool execution based on the chatbot's request.
        - `chatbot`: A function that takes the state as input and returns a message generated by the LLM.
        - `route_tools`: A conditional function to determine whether the chatbot should call a tool.
        - `graph`: The complete graph with nodes and conditional edges.
    """

    primary_llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="Llama3-8b-8192")

    graph_builder = StateGraph(State)
    # Load tools with their proper configs
    max_results = TOOL_CFG.tavily_search_max_results
    search_tool = TavilySearchResults(max_results=max_results)
    tools = [
            lookup_dengue,
            lookup_jaundice,
            search_tool
            ]
    # Tell the LLM which tools it can call
    primary_llm_with_tools = primary_llm.bind_tools(tools)
    system_prompt = ChatPromptTemplate.from_template(
            """
            You are a nurse assistant chatbot designed to help patients manage their care and improve well-being as they recover from their homes. 
            Your tone should be friendly, supportive, and conversational, as though you are a caring nurse speaking directly to the patient. 
            You should aim to build trust, offer empathy, and provide clear guidance. Avoid using medical jargon and complex terms.
            Answer the questions based on the provided context only. 
            If you don't know the answer, just say that you don't know and that the question is out of your knowledge. 
            Use three sentences maximum and keep the answer concise.
            Follow these procedures closly:
            {current_procedure}
            <context>
            {context}
            </context>
            
            """
        ) 
    
    # Load Procedural Memory Instructions
    with open(here("FYP/backend/procedural_memory.txt")) as content:
        current_procedure = content.read()

    def preprocess_state(state: State) -> State:
        """
        Preprocesses the state to include a system prompt in the messages.

        Args:
            state (State): The original state object.

        Returns:
            State: The modified state with the system prompt prepended.
        """
       # Extract existing messages from state
        messages = state.get("messages", [])
        
        #Create a new message with the system prompt
        system_message = {
            "role": "system",
            "content": system_prompt.format(context=state.get('context', ''), current_procedure=current_procedure) 
        }

        #Prepend the new message to the list of existing messages
        updated_messages = [system_message] + messages

        #Return the modified state
        return State(messages=updated_messages, context=state.get('context', ''))

    def chatbot(state: State):
        """Executes the primary language model with tools bound and returns the generated message.
            Preprocesses the state to include a system prompt."""
        state = preprocess_state(state)
        return {"messages": [primary_llm_with_tools.invoke(state["messages"])]}

    #Add chatbot node to graph
    graph_builder.add_node("chatbot", chatbot)
    # Define the tool node with the available tools
    tool_node = BasicToolNode(
        tools=[
            lookup_dengue,
            lookup_jaundice,
            search_tool
        ])
    graph_builder.add_node("tools", tool_node)


    # The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "__end__" if
    # it is fine directly responding. This conditional routing defines the main agent loop.
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
        # It defaults to the identity function, but if you
        # want to use a node named something else apart from "tools",
        # You can update the value of the dictionary to something else
        # e.g., "tools": "my_tools"
        {"tools": "tools", "__end__": "__end__"}
    )

    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    #plot_agent_schema(graph)
    return graph