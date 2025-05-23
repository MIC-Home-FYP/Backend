from typing import List, Tuple
from Agent.load_tools_config import LoadToolsConfig
from Agent.build_graph import build_graph
from langchain_core.messages import ToolMessage
from DBLogic import DBLogic

TOOL_CFG = LoadToolsConfig()
graph = build_graph()
save_chat = DBLogic()
# TODO: Sort out thread_id
config = {"configurable": {"thread_id": TOOL_CFG.thread_id}}

class ChatBot:
    """
    A class to handle chatbot interactions by utilizing a pre-defined agent graph. The chatbot processes
    user messages, generates appropriate responses, and saves the chat history to a specified memory directory.

    Attributes:
        config (dict): A configuration dictionary that stores specific settings such as the `thread_id`.

    Methods:
        respond(chatbot: List, message: str) -> Tuple:
            Processes the user message through the agent graph, generates a response, appends it to the chat history,
            and writes the chat history to a file.
    """
    @staticmethod
    def respond( message: str, user_id: int):
        """
        Processes a user message using the agent graph, generates a response, and appends it to the chat history.
        The chat history is also saved to a memory file for future reference.

        Args:
            chatbot (List): A list representing the chatbot conversation history. Each entry is a tuple of the user message and the bot response.
            message (str): The user message to process.

        Returns:
            Tuple: Returns an empty string (representing the new user input placeholder) and the updated conversation history.
        """
        initial_state = {
            "messages": [("user", message)],
            "user_id": user_id  # Add user_id to the initial state
        }
        # The config is the **second positional argument** to stream() or invoke()!
        events = graph.stream(initial_state, config, stream_mode="values")

        for event in events:
            event["messages"][-1].pretty_print()
            msg = event["messages"]
            human_msg = str(message)
            ai_msg = str(msg[-1].content.strip("\n"))
            
            for message in event["messages"][-1]:
                if isinstance(message, ToolMessage):
                    print(f"Tool used: {message.name}")
       
        #print(f"printing human message:", human_msg)
        #print(f"printing ai message:", ai_msg)
        save_chat.insert_chat_interaction(user_id, human_msg, 'Human Message')
        save_chat.insert_chat_interaction(user_id, ai_msg, 'AI Message')
        print("saved chat")
        # print(f"printing msg:", msg)

        return ai_msg