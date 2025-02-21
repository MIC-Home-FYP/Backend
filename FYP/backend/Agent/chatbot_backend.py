from typing import List, Tuple
from Agent.load_tools_config import LoadToolsConfig
from Agent.build_graph import build_graph


TOOL_CFG = LoadToolsConfig()
graph = build_graph()
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
    def respond(chatbot: List, message: str) -> Tuple:
        """
        Processes a user message using the agent graph, generates a response, and appends it to the chat history.
        The chat history is also saved to a memory file for future reference.

        Args:
            chatbot (List): A list representing the chatbot conversation history. Each entry is a tuple of the user message and the bot response.
            message (str): The user message to process.

        Returns:
            Tuple: Returns an empty string (representing the new user input placeholder) and the updated conversation history.
        """
        
        # The config is the **second positional argument** to stream() or invoke()!
        events = graph.stream(
            {"messages": [("user", message)]}, config, stream_mode="values"
        )
        for event in events:
            event["messages"][-1].pretty_print()
        #print(f"printing event:", event)
        
        #Appends AIMessage, the format of chatbot is list
        #TODO check if chatbot output format needs any changes
        chatbot.append(event["messages"][-1].content)
        print(f"printing list:" ,chatbot)

        return "", chatbot