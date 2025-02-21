from langchain_groq import ChatGroq
from langchain.schema import AIMessage
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
import os
"""
To run this script, make sure you have install the following packages using pip:
- langchain
- langchain-groq
- langchain-community
- pypdf 
- fastembed 
- chroma
Additionally, store ur grog API key in the .env file 
"""
load_dotenv()

#Initialise llm
os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')

llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="Llama3-8b-8192")
#embeddings to be used
embedding = FastEmbedEmbeddings()
#text split settings
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100, length_function=len, is_separator_regex=False)

#Load PDF documents for LLM to reference 
loader = PyPDFDirectoryLoader("docs")
docs = loader.load_and_split()
chunks = text_splitter.split_documents(docs)
db_path = "db"
vector_store = Chroma(persist_directory=db_path, embedding_function=embedding)

#prompt template
prompt = ChatPromptTemplate.from_template(
"""
You are a nurse assistant chatbot designed to help patients manage their care and improve well-being. 
Your tone should be friendly, supportive, and conversational, as though you are a caring nurse speaking directly to the patient. 
You should aim to build trust, offer empathy, and provide clear guidance. Avoid using medical jargon and complex terms.
Answer the questions based on the provided context only. 
If you don't know the answer, just say that you don't know and that the question is out of your knowledge. 
Use three sentences maximum and keep the answer concise.
<context>
{context}
</context>
Question: {input}
Answer:
"""
)

def process_query(query):
    response = llm.invoke(query)
    if isinstance(response, AIMessage):
        return response.content
    return str(response)

def process_pdf_query(query):
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 20, "score_threshold": 0.1},
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, document_chain)
    result = chain.invoke({"input": query})
    
    if isinstance(result, dict) and 'answer' in result:
        return {"answer": result['answer']}
    return {"answer": str(result)}