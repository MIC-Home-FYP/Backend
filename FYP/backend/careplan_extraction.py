from langchain_groq import ChatGroq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from pyprojroot import here
import DBLogic
import os

load_dotenv()
os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')
primary_llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="Llama3-8b-8192")
embedding = FastEmbedEmbeddings()
save_careplan = DBLogic.DBLogic()

with open(here("FYP/backend/docs/Careplan/jack.txt")) as content:
    vectordb_content = content.read() 
system_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an AI assistant tasked with extracting specific medical information from patient records. 
    The input will be a vector file containing various details about a patient. 
    Your job is to accurately identify and extract the following information:

    1. Patient Name
    2. Medical condition
    3. Doctor's Recommendations
    4. Medication (including name and dosage if available)
    5. Medication Timing (frequency or schedule)
    6. Vitals (any mentioned vital signs to be monitored)
    7. Vitals Timing (when the vitals should be taken)
     
    Please format your response as follows:
    Output valid JSON in exactly this format
    {{
        "patient_name": // Name of the patient
        "ailment":       // Medical condition
        "recommendations":  // Doctor's recommendations
        "medication":        // Medication
        "med_timing":        // Medication timing
        "vitals":            // Vitals
        "vitals_time":     // Vitals timing
    }}
    Examples:
    {{
    "patient_name": "John Doe",
    "ailment": "Hypertension",
    "recommendations": "Regular exercise and low-sodium diet",
    "medication": "Lisinopril 10mg",
    "med_timing": "twice daily, morning and afternoon at 12pm after meal",
    "vitals": "Record BP and heart rate",
    "vitals_time": "thrice daily, morning, afternoon and night at 8am, 2pm, and 8pm"
    }}

    If any information is not present in the text, please indicate with "Not mentioned" for that field. 
    Be as accurate and concise as possible in your extraction. 
    Do not infer or add information that is not explicitly stated in the text.
    Always output valid JSON, even if some fields are empty or not found.
    Do not include any text outside the JSON object in your response.
    """),
    ("human", "Here is the vector file: {vectordb_dir}")
])
chain = system_prompt | primary_llm | JsonOutputParser()
extraction = chain.invoke({"vectordb_dir": vectordb_content})
print(extraction)

# save entities to patient records table in the database
user_id =1 
save_careplan.insert_patient_record(
    user_id, 
    extraction["patient_name"], 
    extraction["ailment"], 
    extraction["recommendations"], 
    extraction["medication"], 
    extraction["med_timing"], 
    extraction["vitals"], 
    extraction["vitals_time"]
    )