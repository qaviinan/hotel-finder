import pandas as pd
import re
from .. import chat_config

def load_original():
    df = pd.read_csv('./clean/dataset_airbnb-scraper_2024-04-26_08-50-51-029.csv')
    
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

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def easy_variable_names(query):
    def extract_variable_names(query):
        pattern = r"\['([^']+?)'\]"
        matches = re.findall(pattern, query)
        return matches

    variable_names = extract_variable_names(query)
    return [chat_config.EASY_NAME_MAP[varname] for varname in variable_names] 