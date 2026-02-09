from flask import Flask, request
from flask_cors import CORS
import json
from dotenv import load_dotenv
import os
import chat_config
import pandas as pd
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = Flask(__name__)
load_dotenv()

cors_origins = os.getenv("CORS_ORIGINS")
if cors_origins:
    CORS(app, origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()])
else:
    CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "clean", "dataset_airbnb-scraper_2024-04-26_08-50-51-029.csv")
DEFAULT_MODEL = "llama-3.1-8b-instant"
LLM_PROMPT_TEMPLATE = (
    chat_config.HOTEL_QUERY_PROMPT.replace("$context", "{context}").replace("$query", "{query}")
)
query_chain = None


def get_query_chain():
    global query_chain
    if query_chain is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required for /chat queries other than firstcall.")
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", DEFAULT_MODEL),
            api_key=api_key,
            max_tokens=1000,
            temperature=0,
        )
        prompt = ChatPromptTemplate.from_messages([("human", LLM_PROMPT_TEMPLATE)])
        query_chain = prompt | llm | StrOutputParser()
        app.logger.info("Created LangChain query generator")
    return query_chain

def load_original():
    df = pd.read_csv(DATASET_PATH)

    # List of columns expected to be numeric
    numeric_columns = [
        'bathroom_count',
        'bed_count',
        'bedroom_count',
        'guestControls/personCapacity',
        'idStr',
        'maxNights',
        'minNights',
        'numberOfGuests',
        'pricing/rate/amount'
    ]

    # Convert specified columns to numeric types
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def strip_code_fences(text):
    cleaned_text = text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:python)?\s*", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
    return cleaned_text.strip()

def generate_dataframe_query(user_query):
    generated = get_query_chain().invoke({"context": "", "query": user_query})
    return strip_code_fences(generated)

def build_chat_response(filters, listings, error=None):
    payload = {"filters": filters, "listings": listings}
    if error:
        payload["error"] = error
    return json.dumps(payload, ensure_ascii=False)

def easy_variable_names(query):
    def extract_variable_names(query):
        # Regex pattern to match content within [' and ']
        pattern = r"\['([^']+?)'\]"
        matches = re.findall(pattern, query)
        return matches

    variable_names = extract_variable_names(query)
    easy_variable_names = [chat_config.EASY_NAME_MAP.get(varname, varname) for varname in variable_names]
    return easy_variable_names

@app.route('/chat', methods=['POST'])
def chat():
    request_json = request.get_json(silent=True) or {}
    query = request_json.get('query')
    if not query:
        return (
            build_chat_response([], [], {"type": "validation_error", "message": "Missing required field: query"}),
            400,
            {"Content-Type": "application/json; charset=utf-8"},
        )

    if query=="firstcall":
        print('LOADING THE INITIAL TABLE')
        filtered_df = load_original()
        easy_filters = []
    else:
        try:
            dataframe_query = generate_dataframe_query(query)
            app.logger.warning(dataframe_query)
        except Exception as exc:
            app.logger.exception("Failed to generate dataframe query from LLM")
            return (
                build_chat_response([], [], {"type": "llm_error", "message": str(exc)}),
                502,
                {"Content-Type": "application/json; charset=utf-8"},
            )

        try:
            df = load_original()
            local_vars = {'df': df}
            # Execute the code
            exec_string = "mydf=" + dataframe_query
            exec(exec_string, globals(), local_vars)
            # Get easy variable names for frontend filters
            easy_filters = easy_variable_names(dataframe_query)
            app.logger.warning('Executed QUERY')
            filtered_df = local_vars['mydf']
        except Exception as exc:
            app.logger.exception("Failed to execute dataframe query")
            return (
                build_chat_response([], [], {"type": "query_execution_error", "message": str(exc)}),
                400,
                {"Content-Type": "application/json; charset=utf-8"},
            )
    # rtype = 'text'
    try:
        filter_df = filtered_df[
            [
                'idStr',
                'name',
                'sectionedDescription/summary',
                'url',
                'photos/0/thumbnailUrl',
                'pricing/rate/amount',
                'stars',
                'reviewDetailsInterface/reviewCount',
                'Accuracy',
                'Communication',
                'Cleanliness',
                'Location',
                'Check-in',
                'Value',
                'bedroom_count',
                'bathroom_count',
                'bed_count',
                'guestControls/personCapacity',
                'roomType',
                'city',
            ]
        ].rename(columns={
        "photos/0/thumbnailUrl" : "image_url",
        "pricing/rate/amount" : "price",
        "sectionedDescription/summary" : "description",
        'reviewDetailsInterface/reviewCount' : "review_count",
        'Check-in' : "checkIn",
        'guestControls/personCapacity': "guest_capacity",
        'roomType': "room_type",
        })
    except Exception as exc:
        app.logger.exception("Failed to build response payload")
        return (
            build_chat_response([], [], {"type": "response_build_error", "message": str(exc)}),
            500,
            {"Content-Type": "application/json; charset=utf-8"},
        )

    filter_df.index.name = "index"
    print("Returning:", filtered_df.shape)
    return (
        build_chat_response(easy_filters, filter_df.fillna("").to_dict('records')),
        200,
        {"Content-Type": "application/json; charset=utf-8"},
    )

@app.route('/test', methods=['GET', 'POST'])
def test_data():
    if request.method == 'POST':
        chat_text = request.json['query']
        # session_id = request.json['session_id']
        session_id = 1
        # process the chat_text
        rtype = "table"
        if rtype=="text":
            dummy_text = f"""
            Robert Deniro's film the deer hunter is a film in two parts. The first half is an honest account of the lives of young army drafts in America, as they
            hurry to live their lives before their name is called on the warbus to vietnam. The second half recounts the horror experienced by POWs at the hands
            of Vietnamese fighters. Captured from war, these prisoners are forced to play russian roulette with each other relentlessly, until the bullet lands.

            Your query: {chat_text}
            Your session: {session_id}
            """
            response = json.dumps([{"type" : rtype, "content" : dummy_text}], ensure_ascii=False)
        elif rtype=="table":
            sample_path = './clean/bangkok-supabase-sample.csv'
            if os.path.exists(sample_path):
                df = pd.read_csv(sample_path, index_col=0)
            else:
                # Fallback keeps /test functional even when sample artifact is missing.
                df = load_original()
            filter_df = df[['idStr', 'name', 'url', 'photos/0/thumbnailUrl',  'pricing/rate/amount']].head(10).rename(columns={
            "photos/0/thumbnailUrl" : "image_url", "pricing/rate/amount" : "price"})
            response = json.dumps(filter_df.to_dict('records'), ensure_ascii=False)
        elif rtype=="plot":
            dummy_image = None
            #TODO
            response = None
        print('-----------MY RESPONSE:------------', response)
        return response
    else:    
        df=pd.DataFrame({"souls" : [3,3,4,5,6], "reapers" : [0, 1, 1, 0, 0]})
        df_name = "test_name"
        stat = df.to_dict('records')
        stat.insert(0, ({'df_name' : df_name}))
        return json.dumps(stat, ensure_ascii=False)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug=True)
