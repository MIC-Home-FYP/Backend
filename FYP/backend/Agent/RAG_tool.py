from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.tools import tool
from Agent.load_tools_config import LoadToolsConfig

TOOL_CFG = LoadToolsConfig()

class JaundiceRAGTool:
    """
    A tool for retrieving relevant Jaundice documents using RAG with vector embeddings.

    This tool uses a vector embeddor to transform queries into 
    vector representations. These vectors are then used to query a Chroma-based 
    vector database (persisted on disk) to retrieve the top-k most relevant 
    documents or entries from a specific collection, such as Jaundice.

    Attributes:
        embedding_model (str): The name of the OpenAI embedding model used for 
            generating vector representations of the queries.
        vectordb_dir (str): The directory where the Chroma vector database is 
            persisted on disk.
        k (int): The number of top-k nearest neighbors (most relevant documents) 
            to retrieve from the vector database.
        vectordb (Chroma): The Chroma vector database instance connected to the 
            specified collection and embedding model.

    Methods:
        __init__: Initializes the tool by setting up the embedding model, 
            vector database, and retrieval parameters.
    """

    def __init__(self, vectordb_dir: str, k: int, collection_name: str) -> None:
        """
        Initializes the JaundiceRAGTool with the necessary configuration.

        Args:
            embedding_model (str): The name of the embedding model (e.g., "text-embedding-ada-002")
                used to convert queries into vector representations.
            vectordb_dir (str): The directory path where the Chroma vector database is stored 
                and persisted on disk.
            k (int): The number of nearest neighbor documents to retrieve based on query similarity.
            collection_name (str): The name of the collection inside the vector database that holds 
                the Juandice documents.
        """
        #self.embedding_model = embedding_model
        # Definine embedding function 
        embedding_function = FastEmbedEmbeddings()
        self.vectordb_dir = vectordb_dir
        self.k = k
        self.vectordb = Chroma(
            collection_name=collection_name,
            persist_directory=self.vectordb_dir,
            embedding_function=embedding_function
        )
        print("Number of vectors in vectordb:",
              self.vectordb._collection.count(), "\n\n")


@tool
def lookup_jaundice(query: str) -> str:
    """Retreive Jaundice related information."""
    rag_tool = JaundiceRAGTool(
        #embedding_model=TOOL_CFG.jaundice_rag_embedding_model,
        vectordb_dir=TOOL_CFG.jaundice_rag_vectordb_directory,
        k=TOOL_CFG.jaundice_rag_k,
        collection_name=TOOL_CFG.jaundice_rag_collection_name)
    docs = rag_tool.vectordb.similarity_search(query, k=rag_tool.k)
    return "\n\n".join([doc.page_content for doc in docs])

class DengueRAGTool:
    
    def __init__(self, vectordb_dir: str, k: int, collection_name: str) -> None:

        # Definine embedding function 
        embedding_function = FastEmbedEmbeddings()
        self.vectordb_dir = vectordb_dir
        self.k = k
        self.vectordb = Chroma(
            collection_name=collection_name,
            persist_directory=self.vectordb_dir,
            embedding_function=embedding_function
        )
        print("Number of vectors in vectordb:",
              self.vectordb._collection.count(), "\n\n")

@tool
def lookup_dengue(query: str) -> str:
    """Retreive Dengue related information. symptoms and treatment of dengue is available here"""
    rag_tool = DengueRAGTool(
        #embedding_model=TOOL_CFG.dengue_rag_embedding_model,
        vectordb_dir=TOOL_CFG.dengue_rag_vectordb_directory,
        k=TOOL_CFG.dengue_rag_k,
        collection_name=TOOL_CFG.dengue_rag_collection_name)
    docs = rag_tool.vectordb.similarity_search(query, k=rag_tool.k)
    return "\n\n".join([doc.page_content for doc in docs])