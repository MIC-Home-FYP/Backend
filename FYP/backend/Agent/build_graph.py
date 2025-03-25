from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from Agent.RAG_tool import lookup_jaundice, lookup_dengue
from Agent.load_tools_config import LoadToolsConfig
from Agent.agent_backend import State, BasicToolNode, route_tools, plot_agent_schema
from Agent.reminder_subagent import ReminderSubAgent, reminder_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pyprojroot import here
import os

load_dotenv()

os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')
TOOL_CFG = LoadToolsConfig()
user_id = 1
reminder_agent = ReminderSubAgent (user_id)
schedule_tool = reminder_tool(reminder_agent)
# Load Procedural Memory Instructions
with open(here("FYP/backend/procedural_memory.txt")) as fp:
    current_procedure = fp.read()
with (open(here("FYP/backend/docs/Careplan/careplan_dengue.txt"))) as fp1:
    care_plan = fp1.read()

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
            schedule_tool, 
            ]
    all_tools = [*tools, search_tool]
    # Tell the LLM which tools it can call
    primary_llm_with_tools = primary_llm.bind_tools(all_tools)
    system_prompt = ChatPromptTemplate.from_template(
            """
            You are a nurse assistant chatbot designed to help patients manage their care and improve well-being as they recover from their homes.
            Your tone should be friendly, supportive, and conversational, as though you are a caring nurse speaking directly to the patient.
            You are first to internalise the care plan of the patient provided below.
            Next, follow the instruction guide for you in procedures provided below.
            If you don't know the answer, just say that you don't know and that the question is out of your knowledge.
            Use three sentences maximum and keep the answer concise.
            You are provided with tools relating to the medical condition of the patients, you can use these tools to provide the patient with the necessary information, avoid thanking for any tools used!
            Avoid using your own knowledge to answer questions related to any medical condition.
            The search_tool is an internet search tool which can only be accessed by the "look_up" keyword, you are to only use search_tool if the other tools have inadequate information and users have to grant you permission by providing the "look_up" keyword. avoid thanking for any tools used!
            You can use the 'schedule_tool' tool to retrieve information about the patient's medication and vital check schedules.
            Avoid thanking for any tools used!
            Here is the care plan for the patient:
            {care_plan}
            Follow the instructions here:
            {current_procedure}
            Important note: 
            - Strictly adhere to the care plan and procedure instructions and do not mention usage of care plan or tools used.
            - Maintain a caring and supportive tone throughout the interaction.
            - Prioritize patient safety and well-being in all responses. 
            - Do not use medical jargons or complex terms. 
            - Do not mention specific medical pointers in the care plan to users. maintain confidentiality of the care plan. 

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
            "content": system_prompt.format(context=state.get('context', ''), current_procedure=current_procedure, care_plan = care_plan) 
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
    rag_tools_node = BasicToolNode(
        tools=[
            lookup_dengue,
            lookup_jaundice,
            schedule_tool
        ])
    search_tool_node = search_tool
    graph_builder.add_node("rag_tools", rag_tools_node)
    graph_builder.add_node("search_tool", search_tool_node)
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        {"rag_tools": "rag_tools", "search_tool": "search_tool", "__end__": "__end__"}
    )

    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("rag_tools", "chatbot")
    graph_builder.add_edge("search_tool", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    #plot_agent_schema(graph)
    return graph