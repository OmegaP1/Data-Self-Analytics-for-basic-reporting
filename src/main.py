# src/main.py

import sqlite3
import pandas as pd
from pathlib import Path
from preprocessing.cleaner import CSVCleaner

def get_project_root() -> Path:
    """Returns the project root folder."""
    return Path(__file__).parent.parent

def main():
    """
    Main function to run the data processing pipeline.
    """
    # --- Configuration ---
    # Use pathlib to build robust paths relative to the project root
    ROOT_DIR = get_project_root()
    INPUT_CSV_PATH = ROOT_DIR / 'data' / 'raw' / 'data.csv'
    DB_OUTPUT_PATH = ROOT_DIR / 'data' / 'processed' / 'analytics.db'
    
    TABLE_NAME = 'analytics_data'
    CHUNK_SIZE = 100000  # Process 100,000 rows at a time

    # --- Ensure output directory exists ---
    DB_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # --- Database Setup ---
    try:
        conn = sqlite3.connect(DB_OUTPUT_PATH)
        print(f"Successfully connected to SQLite database: {DB_OUTPUT_PATH}")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return

    # --- Process the CSV in Chunks ---
    print(f"Starting the processing of {INPUT_CSV_PATH.name}...")
    first_chunk = True
    try:
        for chunk in pd.read_csv(INPUT_CSV_PATH, chunksize=CHUNK_SIZE):
            # Preprocess the Chunk
            cleaner = CSVCleaner(chunk)
            cleaned_df = cleaner.clean_data()

            # Load to SQLite
            if_exists_strategy = 'replace' if first_chunk else 'append'
            cleaned_df.to_sql(TABLE_NAME, conn, if_exists=if_exists_strategy, index=False)
            
            print(f"Processed and loaded a chunk into '{TABLE_NAME}'.")
            first_chunk = False

    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_CSV_PATH}")
        return
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return
    finally:
        print("\nProcessing complete!")

    # --- Verification (Optional) ---
    print("\nVerifying the data in the database...")
    try:
        df_from_db = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} LIMIT 5", conn)
        print(f"First 5 rows from the '{TABLE_NAME}' table:")
        print(df_from_db)

        count_query = f"SELECT COUNT(*) FROM {TABLE_NAME}"
        total_rows = pd.read_sql_query(count_query, conn).iloc[0, 0]
        print(f"\nTotal rows in '{TABLE_NAME}': {total_rows}")

    except sqlite3.Error as e:
        print(f"An error occurred during verification: {e}")
    finally:
        # --- Close Connection ---
        conn.close()
        print("\nDatabase connection closed.")


if __name__ == '__main__':
    main()