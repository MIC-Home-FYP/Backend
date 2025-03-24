from langchain_groq import ChatGroq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from Agent.load_tools_config import LoadToolsConfig
from dotenv import load_dotenv
from pyprojroot import here
from DBLogic import DBLogic
import os


load_dotenv()
os.environ["GROQ_API_KEY"] = os.environ.get('GROQ_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')
primary_llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="Llama3-8b-8192")
embedding = FastEmbedEmbeddings()
TOOL_CFG = LoadToolsConfig()
save_careplan = DBLogic()

with open(here("FYP/backend/docs/Careplan/careplan_dengue.txt")) as content:
    care_plan = content.read() 
system_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an AI assistant tasked with extracting specific medical information from patient records. 
    Your job is to accurately identify and extract the following information:

    Please format your response as follows:
    Output valid JSON in exactly this format:
    {{
        "medications": [
            {{
                "medication_name": "<value>",
                "dosage": "<value>",
                "schedule_type_med": "<interval or fixed>",
                "interval_hours_med": <value>,
            }},
            ...
        ],
        "vitals": [
            {{
                "vital_name": "<value>",
                "schedule_type_vitals": "<interval or fixed>",
                "interval_hours_vitals": <value>,
            }},
            ...
        ]
    }}

    Example: 
    {{
        "medications": [
            {{
                "medication_name": "Paracetamol, 81mg",
                "dosage": "2 tablets",
                "schedule_type_med": "interval",
                "interval_hours_med": 6
            }},
            {{
                "medication_name": "Aspirin, 500mg",
                "dosage": "1 tablet",
                "schedule_type_med": "fixed",
                "interval_hours_med": ""
            }}
        ],
        "vitals": [
            {{
                "vital_name": "Temperature",
                "schedule_type_vitals": "interval",
                "interval_hours_vitals": 4
            }},
            {{
                "vital_name": "Blood Pressure",
                "schedule_type_vitals": "fixed",
                "interval_hours_vitals": ""
            }}
        ]
    }}

    If any information is not present in the text, please indicate with " " for that field. 
    Be as accurate and concise as possible in your extraction. 
    Do not infer or add information that is not explicitly stated in the text.
    If short forms are found in the given text convert it to readable text form.  
    For vitals only, suggest the vitals that is needed specific to monitor the specific condition
    Always output valid JSON, even if some fields are empty or not found.
    Do not include any text outside the JSON object in your response.
    {care_plan}
    """)
])

chain = system_prompt | primary_llm | JsonOutputParser()
extraction = chain.invoke({"care_plan": care_plan})
print(extraction)

# save entities to patient records table in the database
# start_time ='12:00'
# user_id = 1
# for med in extraction["medications"]:
#     save_careplan.insert_med_record(
#         user_id, 
#         med["medication_name"], 
#         med["dosage"], 
#         med["schedule_type_med"], 
#         med["interval_hours_med"], 
#         start_time
#     )

# # Save vitals
# for vital in extraction["vitals"]:
#     save_careplan.insert_vitals_record(
#         user_id, 
#         vital["vital_name"], 
#         vital["schedule_type_vitals"], 
#         vital["interval_hours_vitals"], 
#         start_time
#     )