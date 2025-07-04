# Data Self Analytics Agent v1 - CSV Edition

This agent provides a natural language interface to query and retrieve information directly from the `WD Self Analytics Dataset.csv` file. It is designed to be a powerful tool for initial data exploration without needing to write any code.

## Core Features

- **Natural Language Queries:** Ask questions in plain English.
- **Dynamic Code Generation:** The agent writes and executes Python (Pandas) code on the fly to answer your questions.
- **Schema Awareness:** Automatically inspects the CSV to understand its columns and data types.
- **Interactive:** Engages in a conversational flow to provide answers.

## Project Structure

For the agent to function correctly, your project must follow this structure:

your-project-root/
├── agents/
│   └── data_self_analytics__basic_reporting_v1/  <-- The ADK App folder for v1
│       ├── agent.py
│       └── .env
└── data/
└── raw/
└── WD Self Analytics Dataset.csv

## Setup & Running

1.  **Place Data:** Ensure your `WD Self Analytics Dataset.csv` file is located in the `data/raw/` directory.

2.  **Environment File:** Create a `.env` file inside the `.../data_self_analytics__basic_reporting_v1/` folder with the following content:

    ```ini
    # .env
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., europe-west4
    AGENT_MODEL="gemini-1.5-flash-001"
    ```

3.  **Install Dependencies:** From your project's root folder (`.../agents/`), install the required Python packages:

    ```bash
    # You may need to create this requirements.txt file
    pip install pandas python-dotenv google-cloud-aiplatform google-adk
    ```

4.  **Run the Agent:** From the `.../agents/` directory, run the ADK web server:

    ```bash
    adk web
    ```
    You can then access the agent's web UI at `http://localhost:8000`.

## 10 Example Questions

*(These assume your dataset has columns like `Date`, `Region`, `CampaignID`, `MetricName`, `Value`, etc.)*

1.  How many employee records are in the dataset for the last 'Snapshot Month'?
2.  What is the total Full-Time Equivalent (FTE) across all divisions?
3.  Show me the number of employees for each Country.
4.  How many employees are in the 'France' Country and belong to the 'AWF' category?
5.  What are the top 5 Job Profiles with the most employees?
6.  List all the unique 'Division' names in the data.
7.  What is the total FTE for the 'Entity' with the ID '12345'?
8.  How many employees are in 'Band 5'?
9.  Show me the first 10 rows of the data so I can see the structure.
10. What is the average FTE for employees in the 'Germany' country?