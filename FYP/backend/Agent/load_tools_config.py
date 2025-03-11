import os
import yaml
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv()


class LoadToolsConfig:
    
    def __init__(self) -> None:
        with open(here("FYP/backend/configs/tools_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        # Set environment variables
        os.environ['TAVILY_API_KEY'] = os.environ.get("TAVILY_API_KEY")
        os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')

        # Load langsmith config
        os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = app_config["langsmith"]["tracing"]
        os.environ["LANGCHAIN_PROJECT"] = app_config["langsmith"]["project_name"]
        os.environ["LANGSMITH_ENDPOINT"] = app_config["langsmith"]["end_point"]
    

        # Primary agent
        self.primary_agent_llm = app_config["primary_agent"]["llm"]
        self.primary_agent_llm_temperature = app_config["primary_agent"]["llm_temperature"]

        # Internet Search config
        self.tavily_search_max_results = int(
            app_config["tavily_search_api"]["tavily_search_max_results"])

        # Knowledge base RAG configs
        # # TODO check if all the configs are needed
        # self.knowledgebase_rag_vectordb_directory = str(here(
        #     app_config["knowledgebase_rag"]["vectordb"]))  # needs to be string for summation in chromadb backend: self._settings.require("persist_directory") + "/chroma.sqlite3"
        # self.knowledgebase_rag_unstructured_docs_directory = str(here(
        #     app_config["knowledgebase_rag"]["unstructured_docs"]))
        # self.knowledgebase_rag_k = app_config["knowledgebase_rag"]["k"]
        # self.knowledgebase_rag_chunk_size = app_config["knowledgebase_rag"]["chunk_size"]
        # self.knowledgebase_rag_chunk_overlap = app_config["knowledgebase_rag"]["chunk_overlap"]

        # Jaundice RAG configs
        self.jaundice_rag_llm = app_config["Jaundice_rag"]["llm"]
        self.jaundice_rag_llm_temperature = float(
            app_config["Jaundice_rag"]["llm_temperature"])
        #self.jaundice_rag_embedding_model = app_config["Jaundice_rag"]["embedding_model"]
        self.jaundice_rag_vectordb_directory = str(here(
            app_config["Jaundice_rag"]["vectordb"]))  # needs to be string for summation in chromadb backend: self._settings.require("persist_directory") + "/chroma.sqlite3"
        self.jaundice_rag_unstructured_docs_directory = str(here(
            app_config["Jaundice_rag"]["unstructured_docs"]))
        self.jaundice_rag_k = app_config["Jaundice_rag"]["k"]
        self.jaundice_rag_chunk_size = app_config["Jaundice_rag"]["chunk_size"]
        self.jaundice_rag_chunk_overlap = app_config["Jaundice_rag"]["chunk_overlap"]
        self.jaundice_rag_collection_name = app_config["Jaundice_rag"]["collection_name"]
# Dengue RAG configs
        self.dengue_rag_llm = app_config["Dengue_rag"]["llm"]
        self.dengue_rag_llm_temperature = float(
            app_config["Dengue_rag"]["llm_temperature"])
        #self.jaundice_rag_embedding_model = app_config["Jaundice_rag"]["embedding_model"]
        self.dengue_rag_vectordb_directory = str(here(
            app_config["Dengue_rag"]["vectordb"]))  
        self.dengue_rag_unstructured_docs_directory = str(here(
            app_config["Dengue_rag"]["unstructured_docs"]))
        self.dengue_rag_k = app_config["Dengue_rag"]["k"]
        self.dengue_rag_chunk_size = app_config["Dengue_rag"]["chunk_size"]
        self.dengue_rag_chunk_overlap = app_config["Dengue_rag"]["chunk_overlap"]
        self.dengue_rag_collection_name = app_config["Dengue_rag"]["collection_name"]
# Graph configs
# TODO update configs settings to  chatbot backend
        self.thread_id = str(
            app_config["graph_configs"]["thread_id"])