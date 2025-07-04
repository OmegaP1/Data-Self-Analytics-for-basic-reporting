import warnings
import os
import io
import sys
import json
from pathlib import Path

# --- Load environment variables from .env file ---
from dotenv import load_dotenv

load_dotenv()
print("Attempting to load environment variables from .env file...")

import pandas as pd
import vertexai
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext
from pydantic import BaseModel, Field

# --- Configuration & Initialization ---
warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)
print("Loading data analytics agent (Definitive Final Version)...")

# --- Path Configuration ---
PROJECT_ROOT = Path.cwd().parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "data.csv"

if not CSV_PATH.exists():
    sys.exit(f"FATAL ERROR: CSV file not found at the expected path: {CSV_PATH}")
else:
    print(f"Successfully found data file at: {CSV_PATH}")

# --- Initialize Vertex AI ---
try:
    resolved_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    resolved_location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not resolved_project or not resolved_location:
        sys.exit(
            "FATAL ERROR: GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set in your .env file."
        )
    vertexai.init(
        project=resolved_project, location=resolved_location, api_transport="rest"
    )
    print(
        f"Vertex AI initialized for project '{resolved_project}' in location '{resolved_location}'."
    )
except Exception as e:
    sys.exit(f"Error initializing Vertex AI: {e}")


# --- Tool Definitions ---
def inspect_csv_schema(tool_context: ToolContext) -> str:
    """
    Use this tool FIRST to understand the CSV file's structure, columns, and data types before writing any code.
    """
    print(f"  [Tool Call] inspect_csv_schema triggered.")
    try:
        df = pd.read_csv(CSV_PATH, low_memory=False)
        return f"The dataframe has {len(df)} rows and the following columns (with their data types):\n{str(df.dtypes.to_dict())}"
    except Exception as e:
        return f'{{"error": "Failed to inspect CSV schema: {e}"}}'


def execute_pandas_query(query_code: str) -> str:
    """
    Executes a string of Python pandas code to query the data. The pandas DataFrame is available as `df`. The code MUST assign its result to a variable named `result`.
    """
    print(f"  [Tool Call] execute_pandas_query with code:\n---\n{query_code}\n---")
    try:
        df = pd.read_csv(CSV_PATH, low_memory=False)
        local_vars = {"pd": pd, "df": df}
        exec(query_code, globals(), local_vars)
        query_result = local_vars.get("result")

        if isinstance(query_result, (pd.DataFrame, pd.Series)):
            return query_result.to_json(orient="records")
        elif query_result is not None:
            return json.dumps({"result": query_result})
        else:
            return json.dumps({"result": "Query executed, but no result was assigned."})
    except Exception as e:
        return json.dumps({"error": str(e)})


schema_inspector_tool = FunctionTool(func=inspect_csv_schema)
query_executor_tool = FunctionTool(func=execute_pandas_query)

root_agent = LlmAgent(
    name="CsvAnalyticsAssistant",
    model=os.getenv("AGENT_MODEL", "gemini-1.5-pro-001"),
    tools=[
        schema_inspector_tool,
        query_executor_tool,
    ],
    instruction="""You are an expert Data Analytics AI. Your purpose is to answer user questions about a dataset by inspecting its schema, writing Python pandas code, executing it, and summarizing the result. You must be methodical and follow the process perfectly.

    **REASONING PROCESS:**

    1.  **ANALYZE THE USER'S REQUEST:** Determine if the user is asking a question that requires data analysis. If they are just making small talk (e.g., "hello", "thank you"), respond conversationally without using any tools.

    2.  **MANDATORY SCHEMA INSPECTION:** For any data-related question, your absolute first action MUST be to call the `inspect_csv_schema` tool with no arguments. This is how you learn the column names.

    3.  **CODE GENERATION & EXECUTION (SECOND ACTION):** After you have the schema from the previous step, your next action MUST be to call the `execute_pandas_query` tool. To do this, you must generate the Python code for its `query_code` argument.
        - The code you generate must use the column names from the schema.
        - The code MUST assign its final answer to a variable named `result`.
        - The code must NOT use `print()`.

    4.  **FINAL RESPONSE (THIRD ACTION):** After receiving the JSON data from `execute_pandas_query`, your final response MUST be a single, user-friendly natural language sentence summarizing the result. Do not output code or raw JSON in your final answer.

    **EXAMPLE OF A PERFECT TOOL-CALLING SEQUENCE:**

    * **USER ASKS:** "How many employees are in France?"
    * **YOUR 1st THOUGHT:** "I need to answer a question about the data. First, I must inspect the schema."
    * **YOUR 1st ACTION (Tool Call):** `inspect_csv_schema()`
    * **YOUR 2nd THOUGHT (after getting the schema):** "Okay, the schema has a 'Country' column. I will now write the code to count the rows for France and call the execution tool."
    * **YOUR 2nd ACTION (Tool Call):** `execute_pandas_query(query_code="result = len(df[df['Country'] == 'France'])")`
    * **YOUR 3rd THOUGHT (after getting the JSON result `{"result": 50}`):** "The query was successful. The result is 50. I will now formulate the final answer."
    * **YOUR FINAL ANSWER (Text):** "There are 50 employees in the 'France' country."
    """,
)

print("Analytics agent (Definitive Version) loaded successfully and ready to run.")
