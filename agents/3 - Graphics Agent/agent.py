import warnings
import os
import io
import sys
import json
import sqlite3
from pathlib import Path
import datetime

# --- Load environment variables from .env file ---
from dotenv import load_dotenv

load_dotenv()

import pandas as pd
import vertexai
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext

# Matplotlib setup for a non-GUI environment
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# --- Configuration & Initialization ---
warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)
print("Loading data analytics agent v3 (Final Presentation)...")

# --- Path Configuration ---
AGENT_DIR = Path(__file__).parent
PROJECT_ROOT = AGENT_DIR.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "analytics.db"
LOGS_DIR = AGENT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
print(f"Log directory is: {LOGS_DIR}")

if not DB_PATH.exists():
    sys.exit(f"FATAL ERROR: Database file not found at: {DB_PATH}")
else:
    print(f"Successfully found database file at: {DB_PATH}")

# --- Initialize Vertex AI ---
try:
    resolved_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    resolved_location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not resolved_project or not resolved_location:
        sys.exit("FATAL ERROR: GCP Project and Location must be set in your .env file.")
    vertexai.init(
        project=resolved_project, location=resolved_location, api_transport="rest"
    )
    print(
        f"Vertex AI initialized for project '{resolved_project}' in location '{resolved_location}'."
    )
except Exception as e:
    sys.exit(f"Error initializing Vertex AI: {e}")


# --- Tool Definitions ---
def inspect_db_schema(tool_context: ToolContext) -> str:
    """Use this tool FIRST to understand the database schema, including all table names and their columns, before writing any query or plotting code."""
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
            columns = [col[1] for col in cursor.fetchall()]
            schema_info += f"({', '.join(columns)})\n"
        conn.close()
        return schema_info
    except Exception as e:
        return f'{{"error": "Failed to inspect schema: {e}"}}'


def execute_sql_query(sql_query: str) -> str:
    """Use this tool to execute a SQLite query to get data for a simple text-based answer."""
    print(f"  [Tool Call] execute_sql_query with query:\n---\n{sql_query}\n---")
    try:
        conn = sqlite3.connect(DB_PATH)
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return result_df.to_json(orient="records")
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_plotting_code(python_code: str) -> str:
    """Executes Python code to generate a plot, saves it to the logs folder, and returns a JSON object with the file path."""
    print(f"  [Tool Call] execute_plotting_code with code:\n---\n{python_code}\n---")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM analytics_data", conn)
        conn.close()

        execution_scope = {
            "pd": pd,
            "df": df,
            "plt": plt,
            "sns": sns,
            "io": io,
            "base64": base64,
        }

        exec(python_code, execution_scope)
        b64_image = execution_scope.get("result")

        if isinstance(b64_image, str):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = LOGS_DIR / f"plot_{timestamp}.png"
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(b64_image))
            print(f"Image successfully saved to {file_path}")

            return json.dumps(
                {"status": "success", "file_path": str(file_path.resolve())}
            )
        else:
            raise ValueError(
                "Plotting code did not assign a valid base64 string to the 'result' variable."
            )
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Final Agent Definition ---
root_agent = LlmAgent(
    name="VisualAnalyticsAssistant",
    model=os.getenv("AGENT_MODEL", "gemini-1.5-pro-001"),
    tools=[
        FunctionTool(func=inspect_db_schema),
        FunctionTool(func=execute_sql_query),
        FunctionTool(func=execute_plotting_code),
    ],
    instruction="""You are an expert-level Data Visualization and Analytics AI. Your purpose is to answer user questions by inspecting a database, generating code, and executing it.

    **REASONING PROCESS:**

    1.  **ANALYZE INTENT:** First, determine if the user wants a **data answer** (e.g., "how many", "what is") or a **visualization** (e.g., "show me a chart", "plot", "graph"). For simple greetings, respond conversationally.

    2.  **INSPECT SCHEMA (ALWAYS FIRST):** For any data or visualization request, your absolute first action MUST be to call the `inspect_db_schema` tool.

    3.  **ACT ON SCHEMA:** Based on the schema and the user's intent, take ONE of the following two paths:

        **PATH A: DATA QUERY**
        a. Call `execute_sql_query` with a valid SQLite query.
        b. After getting the JSON result, formulate a user-friendly, natural language answer. **Do not show the raw JSON.**

        **PATH B: VISUALIZATION**
        a. **Generate Plotting Code:** Call `execute_plotting_code`. The `python_code` argument must be a script that generates a plot.
            - **CRITICAL RULE: DO NOT WRITE `import` STATEMENTS.** The necessary libraries are pre-loaded.
            - The data is in a pandas DataFrame named `df`.
            - The code MUST assign the final base64-encoded PNG image string to a variable named `result`.
            - **AESTHETICS:** Use `sns.set_theme(style='whitegrid')` and a professional `palette` like `'viridis'` or `'mako'`. Ensure labels are legible and use `plt.tight_layout()`.
        b. **FINAL RESPONSE:** The `execute_plotting_code` tool will return a JSON object like `{"status": "success", "file_path": "C:\\path\\to\\plot.png"}`. Your final response MUST be a clear message informing the user of success and providing them with the full file path.

    **EXAMPLE OF A PERFECT VISUALIZATION FLOW:**

    * **USER:** "Show me a bar chart of employees per Country."
    * **AGENT's 1st ACTION (Tool Call):** `inspect_db_schema()`
    * **AGENT's 2nd ACTION (Tool Call):** `execute_plotting_code(python_code="sns.set_theme(style='whitegrid'); plt.figure(figsize=(12, 8)); sns.countplot(data=df, y='Country', order=df['Country'].value_counts().index, palette='viridis'); ... result = base64.b64encode(buffer.getvalue()).decode('utf-8'); plt.close();")`
    * **AGENT's FINAL ANSWER (Text):** "Success! I have generated the chart you requested. It has been saved to your computer at the following location: C:\\Users\\YourUser\\YourProject\\agents\\data_self_analytics__basic_reporting_v3\\logs\\plot_20250618_143000.png"
    """,
)