import json
import os
from psycopg2.extras import Json, execute_batch
from collections import Counter
from psycopg2.extras import Json
from datetime import datetime
import psycopg2
import glob
import re
import pandas as pd
import numpy as np
import pandas as pd
import os
import pickle


def clean_key(key):
    # Remove numbers from the key
    key = re.sub(r"\d+", "", key)

    # If the key contains 'additional_data', remove numbers and Arabic letters
    if "additional_data" in key:
        key = re.sub(r"[\d\u0600-\u06FF]+", "", key)
    # Split the key into parts
    parts = key.split("_")

    # Keep the first part if it's 'specifications' or 'additional_data'
    first_part = parts[0]

    # Clean the last part
    key = re.sub(r"-+", "-", key)
    key = re.sub(r"\s+", "_", key)
    key = re.sub(r"[/\\]", "_", key)
    key = re.sub(r"['\"]+", "", key)
    key = re.sub(r"[\(\)\{\}\[\]]", "", key)
    key = re.sub(r"[!@#$%^&*+~;,.]", "", key)
    key = re.sub(r"[:-]", "_", key)

    # Truncate to PostgreSQL's column name length limit (63 bytes)
    last_part = key[-30:].replace(f"{first_part}_", "") if len(parts) > 1 else ""

    # Combine parts
    if first_part and last_part:
        cleaned_key = f"{first_part}_{last_part}"
    elif first_part:
        cleaned_key = first_part
    else:
        cleaned_key = last_part

    # Ensure the key doesn't start with a number
    if cleaned_key and cleaned_key[0].isdigit():
        cleaned_key = "col_" + cleaned_key

    # Remove any trailing underscores
    cleaned_key = cleaned_key.rstrip("_")
    if "age" in cleaned_key:
        pause = 1

    return cleaned_key


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + "_")
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, name + str(i) + "_")
        else:
            clean_name = clean_key(name[:-1])
            out[clean_name] = x

    flatten(y)
    return out


def get_all_keys(directory, num_files=50):
    all_col_names_path = r"G:\My Drive\Personal\Work\offline\Jupyter\Git\s_locator\storage\postgres\all_col_names.json"
    if os.path.exists(all_col_names_path):
        with open(all_col_names_path, "r", encoding="utf-8") as file:
            all_keys = json.load(file)
            return all_keys["all_col_names"]
    all_keys = set()
    json_files = glob.glob(os.path.join(directory, "*_response_data.json"))

    for file_path in json_files[:num_files]:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for listing_data in data.values():
            flattened = flatten_json(listing_data)
            all_keys.update(flattened.keys())

    list_all_keys = list(all_keys)
    list_all_keys.sort(reverse=True)
    list_all_keys.remove("")

    output_data = {"all_col_names": all_keys}
    with open(all_col_names_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to: {all_col_names_path}")
    return list_all_keys


def move_to_front(lst, items_to_move):
    front_items = [item for item in items_to_move if item in lst]
    remaining_items = [item for item in lst if item not in items_to_move]
    return front_items + remaining_items


def generate_insert_sql(url, flattened_data, all_keys):
    items_to_move = ["price",
                     "additional__WebListing_uri___location_lat", 
                     "additional__WebListing_uri___location_lng"]
    all_keys = move_to_front(all_keys, items_to_move)
    columns = (
        ["url"]
        + all_keys
    )
    all_keys.remove("original_specifications")
    all_keys.remove("original_additional_data")
    values = [url]
    values.extend([flattened_data.get(key, None) for key in all_keys])
    values.extend(
        [
            Json(flattened_data.get("specifications", {})),
            Json(flattened_data.get("additional_data", {})),
        ]
    )

    placeholders = ", ".join(["%s"] * len(columns))
    column_names = ", ".join(f'{col.lower()}' for col in columns)

    sql = f"""
    INSERT INTO riyadh_villa_allrooms ({column_names})
    VALUES ({placeholders})
    ON CONFLICT (url) DO UPDATE
    SET {', '.join([f'{col.lower()} = EXCLUDED.{col.lower()}' for col in columns])};
    """

    return sql, tuple(values)


def process_and_insert_data(directory, cursor, all_keys, limit=3):
    json_files = glob.glob(os.path.join(directory, "*_response_data.json"))
    processed_files = set()
    sql_log_dir = "G:\\My Drive\\Personal\\Work\\offline\\Jupyter\\Git\\s_locator\\storage\\postgres\\sql_logs"
    os.makedirs(sql_log_dir, exist_ok=True)

    files_processed = 0

    for file_path in json_files:
        if files_processed >= limit:
            break

        file_number = re.search(r"(\d+)_response_data\.json", file_path)
        if not file_number:
            print(f"Skipping file with invalid name format: {file_path}")
            continue

        file_number = file_number.group(1)
        log_file = os.path.join(sql_log_dir, f"{file_number}.sql")

        if os.path.exists(log_file):
            print(f"Skipping already processed file: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        sql_statements = []
        for url, listing_data in data.items():
            # Skip empty listings or listings with empty string values
            if not listing_data or all(v == "" for v in listing_data.values()):
                continue

            flattened = flatten_json(listing_data)
            sql, values = generate_insert_sql(url, flattened, [col for col in all_keys if col !="url"])
            sql_statements.append((sql, values))

        if not sql_statements:
            print(f"Skipping file with no valid data: {file_path}")
            continue

        # Execute SQL statements
        for sql, values in sql_statements:
            cursor.execute(sql, values)

        # Save SQL statements to log file
        with open(log_file, "w", encoding="utf-8") as log:
            for sql, values in sql_statements:
                log.write(f"{sql}\n{values}\n\n")

        processed_files.add(file_path)
        print(f"Processed file: {file_path}")

        files_processed += 1

    return processed_files


def contains_arabic(text):
    arabic_pattern = re.compile("[\u0600-\u06FF]")
    return bool(arabic_pattern.search(str(text)))


def is_boolean_or_binary(series):
    unique_values = set(series.dropna().unique())
    return unique_values.issubset(
        {True, False, 0, 1, "0", "1", "True", "False", "true", "false"}
    )




def process_and_filter_data(directory, all_keys, num_files=350):
    all_col_names_path = r"G:\My Drive\Personal\Work\offline\Jupyter\Git\s_locator\storage\postgres\process_and_filter_data.json"
    if os.path.exists(all_col_names_path):
        with open(all_col_names_path, "r", encoding="utf-8") as file:
            json_obj = json.load(file)
            return json_obj["sorted_new_keep_cols"]
    # Define the path for the saved DataFrame
    df_save_path = os.path.join(directory, 'processed_dataframe.pkl')

    # Check if the processed DataFrame already exists
    if os.path.exists(df_save_path):
        print("Loading existing processed DataFrame...")
        with open(df_save_path, 'rb') as f:
            df = pickle.load(f)
    else:
        print("Processing data and creating new DataFrame...")
        json_files = glob.glob(os.path.join(directory, "*_response_data.json"))
        data = []

        for file_path in json_files[:num_files]:
            with open(file_path, "r", encoding="utf-8") as file:
                file_data = json.load(file)
                for url, listing_data in file_data.items():
                    flattened = flatten_json(listing_data)
                    flattened["url"] = url
                    data.append(flattened)

        df = pd.DataFrame(data)

        # Save the DataFrame
        with open(df_save_path, 'wb') as f:
            pickle.dump(df, f)
        print(f"DataFrame saved to {df_save_path}")

    if len(df.columns)>len(all_keys):
        all_keys.extend(df.columns)
        all_keys = list(set(all_keys))

    # Choose specific columns and drop others
    print("Dropping unnecessary columns...")
    columns_to_drop = [
        "additional_rops_path_listing_location_lat",
        "additional_lasticWebListing__location_lat",
        "additional_ended_details_national_address_latitude",
        "additional_rops_path_listing_location_lng",
        "additional_lasticWebListing__location_lng",
        "additional_ended_details_national_address_longitude",
    ]

    
    spec_cols =  [col for col in all_keys if "specifications" in col]
    non_spec_cols= [col for col in all_keys if col not in spec_cols ]
    df = df.drop(columns=[col for col in columns_to_drop if col in non_spec_cols])

    print("Selecting columns to keep...")
    value_counts = df.nunique() / len(df)
    columns_to_keep = [
        col
        for col in df.columns
        if value_counts[col] >= 0.00015
        or is_boolean_or_binary(df[col])
    ]
    columns_to_keep.extend([
        "additional__WebListing_uri___location_lat",
        "additional__WebListing_uri___location_lng",
    ])

    df = df[columns_to_keep]

    # Drop columns with 'video' or 'img' in the name
    print("Dropping columns with 'video' or 'img' in the name...")
    df = df.drop(columns=[col for col in df.columns if "video" in col.lower()])
    df = df.drop(columns=[col for col in df.columns if "img" in col.lower()])


    # Drop columns where more than 50% of values contain more than 3 '/' or '\'
    print("Dropping columns with excessive slashes...")
    slash_mask = np.vectorize(lambda x: str(x).count('/') + str(x).count('\\') > 3)(df.values)
    slash_cols = df.columns[np.mean(slash_mask, axis=0) > 0.5]
    https_mask = np.vectorize(lambda x: str(x).startswith('https:'))(df[slash_cols].values)
    slash_cols = slash_cols[~np.any(https_mask, axis=0)]
    df = df.drop(columns=slash_cols)
    if "additional_rops_pageProps_path_listing_id" in df.columns:
        print("Dropping columns related to 'additional_rops_pageProps_path_listing_id'...")
        listing_id_col = df["additional_rops_pageProps_path_listing_id"].astype(str)
        id_mask = np.vectorize(lambda x: str(x) in listing_id_col.values)(df.values)
        id_cols = df.columns[np.mean(id_mask, axis=0) > 0.5]
        df = df.drop(columns=[col for col in id_cols if col != "additional_rops_pageProps_path_listing_id"])


    # Keep only the columns that are in all_keys plus 'url'
    print("Keeping only the required columns...")
    df = df[["url", "price"] + [col for col in all_keys if col in df.columns]]
    new_keep_cols = df.columns.tolist()

    # Sort the columns
    print("Sorting the columns...")

    arabic_cols = [col for col in new_keep_cols if "specifications" in col]
    non_arabic_cols = [col for col in new_keep_cols if col not in arabic_cols]
    # Combine the sorted lists, with Arabic columns first
    sorted_new_keep_cols = arabic_cols+ spec_cols + non_arabic_cols
    re_spec_cols = list(set([col for col in sorted_new_keep_cols if "specifications" in col]))
    re_nonspec_cols = list(set([col for col in sorted_new_keep_cols if "specifications" not in col]))
    re_nonspec_cols.remove("url")
    re_nonspec_cols.remove("price")
    sorted_new_keep_cols = ["url","price"] + re_spec_cols + re_nonspec_cols

    output_data = {"sorted_new_keep_cols": sorted_new_keep_cols}
    with open(all_col_names_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to: {all_col_names_path}")

    return sorted_new_keep_cols


def main():
    try:
        conn = psycopg2.connect(
            dbname="",
            user="",
            password="",
            host="",
            port="",
        )

        cursor = conn.cursor()

        directory = "G:\\My Drive\\Personal\\Work\\offline\\Jupyter\\Git\\testwebscraping\\riyadh_villa_allrooms"

        # Get all keys from the first 50 files
        all_keys = get_all_keys(directory)

        # Process and filter data
        columns = process_and_filter_data(directory, all_keys)
        columns.extend(["original_specifications", "original_additional_data"])

        # Use the filtered DataFrame to create the table
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS riyadh_villa_allrooms (
            url TEXT PRIMARY KEY,
            {', '.join([f'{col.lower()} TEXT' for col in columns if col != 'url'])},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_sql)

        # Process and insert data
        processed_files = process_and_insert_data(directory, cursor, columns, limit=100)

        conn.commit()
        print(
            f"Data processing and insertion completed successfully. Processed {len(processed_files)} files."
        )

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
