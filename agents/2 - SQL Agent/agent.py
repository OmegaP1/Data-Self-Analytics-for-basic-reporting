import warnings
import os
import io
import sys
import json
import certifix
import sqlite3
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
print("Loading data analytics agent v2 (Final Architecture)...")

# --- Path Configuration ---
PROJECT_ROOT = Path.cwd().parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "analytics.db"

if not DB_PATH.exists():
    sys.exit(f"FATAL ERROR: Database file not found at: {DB_PATH}")
else:
    print(f"Successfully found database file at: {DB_PATH}")

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


# --- Tool Definitions for SQLite ---
def inspect_db_schema(tool_context: ToolContext) -> str:
    """
    Use this tool FIRST to understand the database schema, including all table names and their columns, before writing a query.
    """
    print("  [Tool Call] inspect_db_schema triggered.")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            return "No tables found in the database."
        schema_info = "The database contains the following tables:\n"
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            schema_info += f"- Table '{table_name}' with columns: "
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            schema_info += f"({', '.join(column_names)})\n"
        conn.close()
        return schema_info
    except Exception as e:
        return f'{{"error": "Failed to inspect database schema: {e}"}}'


def execute_sql_query(sql_query: str) -> str:
    """
    Use this tool to execute a valid SQLite query against the database. Returns the query result as a JSON string.
    """
    print(f"  [Tool Call] execute_sql_query with query:\n---\n{sql_query}\n---")
    try:
        conn = sqlite3.connect(DB_PATH)
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return result_df.to_json(orient="records")
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Final Agent Definition ---

# Define tools using the minimalist API syntax that works for your ADK version
schema_inspector_tool = FunctionTool(func=inspect_db_schema)
query_executor_tool = FunctionTool(func=execute_sql_query)

# Define the single, powerful agent that handles the entire workflow
root_agent = LlmAgent(
    name="SqlAnalyticsAssistant",
    model=os.getenv("AGENT_MODEL", "gemini-1.5-pro-001"),
    tools=[
        schema_inspector_tool,
        query_executor_tool,
    ],
    # The final, bulletproof prompt tailored for SQL
    instruction="""You are an expert SQL Database Analyst. Your purpose is to answer user questions by inspecting a database schema, writing SQLite queries, executing them, and summarizing the result. You must be methodical and follow the process perfectly.

    **REASONING PROCESS:**

    1.  **ANALYZE THE USER'S REQUEST:** Determine if the user is asking a question that requires data analysis. If they are just making small talk (e.g., "hello", "thank you"), respond conversationally without using any tools.

    2.  **MANDATORY SCHEMA INSPECTION:** For any data-related question, your absolute first action MUST be to call the `inspect_db_schema` tool with no arguments. This is how you learn the table and column names.

    3.  **SQL GENERATION & EXECUTION (SECOND ACTION):** After you have the schema from the previous step, your next action MUST be to call the `execute_sql_query` tool. To do this, you must generate the SQL code for its `sql_query` argument.
        - The SQL you generate must use the table and column names from the schema.
        - The SQL must be valid for SQLite.

    4.  **FINAL RESPONSE (THIRD ACTION):** After receiving the JSON data from `execute_sql_query`, your final response MUST be a single, user-friendly natural language answer. Do not output SQL or raw JSON in your final answer.
        - If the JSON result contains an 'error' key, explain the error politely.
        - If the JSON result contains a single value, state the answer in a full sentence.
        - If the JSON result is a list of records (a table), you MUST format it for readability. Announce the result and present a summary of each record on a new line.

    **EXAMPLE OF A PERFECT TOOL-CALLING SEQUENCE:**

    * **USER ASKS:** "How many employees are in France?"
    * **YOUR 1st THOUGHT:** "I need to answer a question about the data. First, I must inspect the database schema."
    * **YOUR 1st ACTION (Tool Call):** `inspect_db_schema()`
    * **YOUR 2nd THOUGHT (after getting the schema):** "Okay, the schema has a table named 'analytics_data' with a 'Country' column. I will now write the SQL to count the rows for France and call the execution tool."
    * **YOUR 2nd ACTION (Tool Call):** `execute_sql_query(sql_query="SELECT COUNT(*) FROM analytics_data WHERE Country = 'France';")`
    * **YOUR 3rd THOUGHT (after getting the JSON result `[{"COUNT(*)": 50}]`):** "The query was successful. The result is 50. I will now formulate the final answer."
    * **YOUR FINAL ANSWER (Text):** "There are 50 employees in the 'France' country."
    """,
)

print(
    "Analytics agent v2 (Definitive Final Version) loaded successfully and ready to run."
)
