# Place this code in: .../agents/data_self_analytics_report_v4/agent.py

import warnings
import os
import io
import sys
import json
import certifix
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

# Matplotlib setup
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# --- Configuration & Initialization ---
warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)
print("Loading data analytics agent v4 (Report Generation)...")

# --- Path Configuration ---
AGENT_DIR = Path(__file__).parent
PROJECT_ROOT = AGENT_DIR.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "analytics.db"
REPORTS_DIR = AGENT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)
print(f"Reports will be saved in: {REPORTS_DIR}")

if not DB_PATH.exists():
    sys.exit(f"FATAL ERROR: Database file not found at: {DB_PATH}")

# --- Initialize Vertex AI ---
try:
    resolved_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    resolved_location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not resolved_project or not resolved_location:
        sys.exit("FATAL ERROR: GCP Project and Location must be set in .env file.")
    vertexai.init(
        project=resolved_project, location=resolved_location, api_transport="rest"
    )
    print(f"Vertex AI initialized for project '{resolved_project}'.")
except Exception as e:
    sys.exit(f"Error initializing Vertex AI: {e}")

# --- V4 Tool Definitions ---


def create_report_folder(tool_context: ToolContext) -> str:
    """Use this tool FIRST to create a unique workspace folder for a new report."""
    print("  [Tool Call] create_report_folder triggered.")
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = REPORTS_DIR / f"report_{timestamp}"
        report_path.mkdir(exist_ok=True)
        print(f"Created report folder: {report_path}")
        return json.dumps(
            {"status": "success", "report_folder_path": str(report_path.resolve())}
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to create report folder: {e}"})


def execute_sql_query(sql_query: str) -> str:
    """Executes a SQLite query to retrieve data for the report."""
    print(f"  [Tool Call] execute_sql_query with query:\n---\n{sql_query}\n---")
    try:
        conn = sqlite3.connect(DB_PATH)
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        # Return data as a JSON string for the agent to process
        return result_df.to_json(orient="split")
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_plotting_code(python_code: str, report_folder_path: str) -> str:
    """Executes Python code to generate a plot and saves it into the specified report folder."""
    print(
        f"  [Tool Call] execute_plotting_code triggered for folder: {report_folder_path}"
    )
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

        # The plotting code is expected to save the figure itself.
        # We just need to confirm it ran. The agent will know the filename it chose.
        return json.dumps({"status": "success", "message": "Plotting code executed."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def write_markdown_report(report_content: str, report_folder_path: str) -> str:
    """Writes the final, complete Markdown string to a report.md file in the specified report folder."""
    print(
        f"  [Tool Call] write_markdown_report triggered for folder: {report_folder_path}"
    )
    try:
        report_file_path = Path(report_folder_path) / "report.md"
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report successfully saved to {report_file_path}")
        return json.dumps(
            {"status": "success", "final_report_path": str(report_file_path.resolve())}
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to write report file: {e}"})


# --- V4 Agent Definition ---

root_agent = LlmAgent(
    name="ReportGenerationAssistant",
    model=os.getenv("AGENT_MODEL", "gemini-1.5-pro-001"),
    tools=[
        FunctionTool(func=create_report_folder),
        FunctionTool(func=execute_sql_query),
        FunctionTool(func=execute_plotting_code),
        FunctionTool(func=write_markdown_report),
    ],
    instruction="""You are an elite research analyst AI. Your purpose is to create comprehensive, multi-part reports in Markdown format by planning and executing a sequence of data retrieval and visualization steps.

    **YOUR METHODICAL PROCESS:**

    1.  **ACKNOWLEDGE AND PLAN:** When the user asks for a report, acknowledge the request. Then, formulate a step-by-step plan in your thoughts. Your absolute first action in the plan MUST be to call `create_report_folder` to create a workspace.

    2.  **EXECUTE THE PLAN STEP-BY-STEP:** Execute your plan by calling one tool at a time.
        - Use `execute_sql_query` to get data tables.
        - Use `execute_plotting_code` to generate and save charts. **You must tell the tool where to save the chart by passing the `report_folder_path`**. You must also invent a unique filename for each plot (e.g., `country_breakdown.png`).
        - **Crucially, after each tool call, you must remember the result (the data, or the path to the chart) to assemble the final report.**

    3.  **ASSEMBLE THE REPORT:** Once all data is gathered and all charts are created, formulate a complete Markdown string for the final report. This string should include titles, summaries of the data, and embedded images using **relative paths** to the filenames you chose (e.g., `![Employee Distribution by Country](country_breakdown.png)`).

    4.  **WRITE THE FINAL REPORT:** Your final action MUST be to call the `write_markdown_report` tool, passing the complete Markdown string as `report_content` and the correct `report_folder_path`.

    5.  **FINAL RESPONSE:** After the report is written, inform the user of the success and provide the final path to the `report.md` file.

    **EXAMPLE OF A PERFECT REPORT GENERATION FLOW:**
    * **USER:** "Create a report on the workforce in France, showing a count of employees and a chart of employees by Division."
    * **AGENT's 1st ACTION:** `create_report_folder()` -> gets back a path like `.../report_123`.
    * **AGENT's 2nd ACTION:** `execute_sql_query(sql_query="SELECT COUNT(*) FROM analytics_data WHERE Country = 'France'")` -> gets back the count.
    * **AGENT's 3rd ACTION:** `execute_plotting_code(report_folder_path='.../report_123', python_code="...sns.countplot(data=df[df['Country']=='France'], y='Division')... plt.savefig('.../report_123/france_divisions.png') ...")` -> saves the chart.
    * **AGENT's 4th ACTION:** `write_markdown_report(report_folder_path='.../report_12_3', report_content='# Report on French Workforce\\n\\nThe total number of employees is 50.\\n\\nHere is the breakdown by division:\\n\\n![Divisions in France](france_divisions.png)')` -> saves the .md file.
    * **AGENT's FINAL ANSWER (Text):** "I have successfully created the report. It is saved at: C:\\...\\report_123\\report.md"
    """,
)


# Use Plotly isntead mathplotlib and seaborn
