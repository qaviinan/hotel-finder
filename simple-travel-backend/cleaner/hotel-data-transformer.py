import pandas as pd
import json
import os
from argparse import ArgumentParser
import chat_config

def reduce_columns(sdf):
    REMOVE_COLS = ['accessibilityModule', 'Host', 'PreviewAmenities', 'seeAllAmenitySections', 'structuredHouseRulesWithTips', 'highlights',
                   'Percentage',
                    'hometourRooms', 'listingExpectations', 'listingRooms', 'localizedListingExpectations', 'caption', 'priceDetails']
    remove_col_list = []
    for col in sdf.columns:
        for removable in REMOVE_COLS:
            if str.lower(removable) in str.lower(col):
                remove_col_list.append(col)
    df = sdf.drop(columns=remove_col_list)
    return df.dropna(axis='columns', how='all')

def shorten_amenities(df):
    # First, extract names for renaming 'isPresent' columns
    num_amenities = 100  # Adjust this based on the actual number of amenities
    for i in range(num_amenities):
        is_present_col = f'listingAmenities/{i}/isPresent'
        name_col = f'listingAmenities/{i}/name'
        
        # Check if the necessary columns are in the DataFrame
        if name_col in df.columns:
            if is_present_col in df.columns: 
                # Rename 'isPresent' column based on the 'name' column
                new_col_name = df[name_col].dropna().iloc[0]
                df.rename(columns={is_present_col: f'amenity_{new_col_name}'}, inplace=True)
            df.drop(columns=[name_col], inplace=True)            
    
        id_col = f'listingAmenities/{i}/id'
        if id_col in df.columns:
            df = df.drop(columns=[id_col])

        desc_col = f"listingAmenities/{i}/description"
        if desc_col in df.columns:
            df = df.drop(columns=[desc_col])
    return df

def shorten_reviews(df):
    num_reviews = 6
    for i in range(num_reviews):
        label_col = f'reviewDetailsInterface/reviewSummary/{i}/label'
        rating_col = f'reviewDetailsInterface/reviewSummary/{i}/localizedRating'
        value_col = f'reviewDetailsInterface/reviewSummary/{i}/value'
        if label_col in df.columns:
            new_col_name = df[label_col].dropna().iloc[0]
            df.rename(columns={rating_col: new_col_name}, inplace=True)
            df = df.drop(columns=[label_col, value_col])
    return df

def remove_too_many_photos(df, max_id=30):
    # Define a helper function to extract the photo ID from a column name
    def get_photo_id(column_name):
        parts = column_name.split('/')
        if len(parts) > 1 and parts[0] == 'photos':
            try:
                return int(parts[1])
            except ValueError:
                return None
        return 1
    # Use the helper function to filter out columns
    cols_to_keep = [col for col in df.columns if get_photo_id(col) <= max_id]
    return df[cols_to_keep]

def sanitize_column_name(col):
    return str("_").join(str("_").join(col.split(" ")).split("_"))

def lose_mostly_empty(df, threshold):
    for col in df.columns.unique():
        if isinstance(df[col] ,pd.DataFrame):
            hot_water = df[col].iloc[:, 0]
            df = df.drop(columns=[col])
            df[sanitize_column_name(col)] = hot_water
    null_percentage = df.isnull().mean()
    columns_to_drop = null_percentage[null_percentage > threshold].index
    df_cleaned = df.drop(columns=columns_to_drop)
    return df_cleaned


def numerize_string_series(input_series, remove_string):
    """
    Converts a series of strings containing numbers followed by a specified substring into a series of numbers.
    
    Parameters:
        input_series (pd.Series): Series of strings, each containing a number followed by a specified substring.
        remove_string (str): Substring to remove, typically a word like "beds" or "baths".
    
    Returns:
        pd.Series: Series containing only the numeric part of the original strings as integers.
    """
    # Use str.extract to pull out the numeric part before the specified string
    numeric_part = input_series.str.extract(f'(\d+)\s*(\w+)')
    # Convert the extracted strings to numeric type (integers)
    return pd.to_numeric(numeric_part[0], errors='coerce')

def save_booleans_as_ints(df):
    for col in df.columns:
        if ("amenity" in col) | ("allows" in col):
            df[col] = df[col].fillna(0).astype(int)
    return df

def process_csv(csv_path):
    sdf = pd.read_csv(csv_path)
    df = shorten_amenities(reduce_columns(sdf))
    df = shorten_reviews(df)
    df = remove_too_many_photos(df, max_id=30)
    df = lose_mostly_empty(df, 0.8)
    df = save_booleans_as_ints(df)
    df['bed_count'] = numerize_string_series(df['bedLabel'], "beds")
    df['bathroom_count'] = numerize_string_series(df['bathroomLabel'], "bath")
    df['bedroom_count'] = numerize_string_series(df['bedroomLabel'], "bedroom")
    valid_columns = [col for col in chat_config.FINAL_COLUMNS if col in df.columns]
    print(valid_columns)
    return df[valid_columns].sort_values(by=['reviewDetailsInterface/reviewCount'], ascending=False).fillna(" ")

def process_new_files(file_dir, clean_dir, processed_files_json):
   """
   Loops through files in a reference directory, checks for new files against a processed_files.json file,
   processes new files, and updates the processed_files.json file.

   Args:
       reference_dir (str): Path to the reference directory containing files to process.
       processed_files_json (str, optional): Path to the processed_files.json file. Defaults to "processed_files.json".
   """

   try:
       with open(processed_files_json, "r") as f:
           processed_files = set(json.load(f))
   except (FileNotFoundError, json.JSONDecodeError):
       processed_files = set()

   new_files = []
   for filename in os.listdir(file_dir):
        file_path = file_dir + "/" + filename
        if not os.path.isdir(file_path):
            if filename not in processed_files:
            # Process the new file here
                print(f"Processing new file: {filename}")
                if file_path.endswith(".csv"):
                    # Clean data and append to csv
                    df = process_csv(file_path)
                    print(df.info())
                    file_save_path = clean_dir + "/" + filename
                    df.to_csv(file_save_path)
                    new_files.append(filename)
            else:
                print(f'Already processed ------------------ {filename}')

   if new_files:
        with open(processed_files_json, "w") as f:
           json.dump(list(processed_files | set(new_files)), f)
        print('List of processed files:', list(new_files))

if __name__=="__main__":
    parser = ArgumentParser(description="Process references directory with options for subdirectories")
    parser.add_argument("--references", "-r", type=str, default="references/",
                        help="Path to the references directory (default: references/)")
    parser.add_argument("--clean", "-c", type=str, default="clean/",
                        help="Path to clean data directory")    
    args = parser.parse_args()

    # Construct directory paths
    references_directory = os.path.abspath(os.path.expanduser(args.references))
    clean_directory = os.path.abspath(os.path.expanduser(args.clean))
    processed_files_json_path = clean_directory + "/" + "processed_files.json"
    process_new_files(references_directory, clean_directory, processed_files_json_path)
