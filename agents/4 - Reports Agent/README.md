# Data Self Analytics Agent v4 - Report Generation Edition

This is the most powerful version of the analytics agent. It acts as an automated research analyst, capable of generating complete, multi-part reports in Markdown format that include both data tables and custom visualizations.

## Core Features

-   **Automated Report Planning:** The agent devises a step-by-step plan to fulfill complex report requests.
-   **Multi-Artifact Output:** For each report, it creates a dedicated folder containing multiple files (PNG images, a final Markdown document).
-   **Stateful Execution:** The agent remembers the results from previous steps (like data lookups or file paths) to use them in later steps.
-   **Composite Document Generation:** It assembles all the generated text, data, and charts into a single, clean, and readable Markdown report.

## Project Structure

our-project-root/
├── agents/
│   └── data_self_analytics_report_v4/  <-- The ADK App folder for v4
│       ├── agent.py
│       ├── logs/ (For individual plot images, if not in a report folder)
│       └── reports/  <-- Each report gets its own sub-folder here
│           └── report_20250618_160000/
│               ├── some_chart.png
│               └── report.md
│       └── .env
└── data/
└── processed/
└── analytics.db

## Setup & Running

1.  **Prerequisites:** Ensure `analytics.db` exists and `matplotlib` and `seaborn` are installed.
2.  **Environment File:** Create a `.env` file inside the V4 agent folder.
3.  **Run the Agent:** From the `.../agents/` directory, run the ADK web server.

    ```bash
    adk web
    ```
    Select the `data_self_analytics_report_v4` agent from the web UI.

## Example Report-Generation Questions

1.  "Please create a full report on our workforce in France. I need to see the total employee count, the total FTE, and a bar chart showing the breakdown of employees by `Worker Category`."
2.  "Generate a summary report for the top 3 countries by employee headcount. For each of the three countries, please include their total FTE and create a pie chart showing the distribution of `Band`s."
3.  "I need a performance report. Please find the top 5 and bottom 5 `Job Profile`s by employee count and create two separate bar charts to visualize this."
