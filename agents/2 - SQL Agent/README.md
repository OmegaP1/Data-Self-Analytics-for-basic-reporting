# Data Self Analytics Agent v2 - SQLite Edition

This is an advanced version of the analytics agent that queries a pre-processed SQLite database (`analytics.db`). This approach is significantly faster and more scalable for large datasets compared to reading a raw CSV file for every query.

## Core Features

- **High Performance:** Queries a structured SQLite database for fast results.
- **Natural Language Queries:** Ask questions in plain English.
- **SQL Generation:** The agent writes and executes **SQL** queries on the fly.
- **Database Schema Awareness:** Automatically inspects the database to find tables and columns.

## Prerequisites

This agent **requires** the `analytics.db` file to exist. You must first run the preprocessing pipeline (`main.py` and `preprocess.py`) to convert the raw CSV into the SQLite database.

## Project Structure
your-project-root/
├── agents/
│   └── data_self_analytics__db_query_v2/  <-- The ADK App folder for v2
│       ├── agent.py
│       └── .env
└── data/
└── processed/
└── analytics.db  <-- The database file v2 queries

## Setup & Running

1.  **Generate Database:** Make sure `analytics.db` exists in the `data/processed/` directory.

2.  **Environment File:** Create a `.env` file inside the `.../data_self_analytics__db_query_v2/` folder with your GCP credentials (same as v1).

3.  **Install Dependencies:** Ensure you have the required packages installed (`pandas`, `python-dotenv`, `google-adk`, etc.).

4.  **Run the Agent:** From the `.../agents/` directory, run the ADK web server. It will now show both v1 and v2 agents.

    ```bash
    adk web
    ```
    Select the `data_self_analytics__db_query_v2` agent from the web UI.

## 10 Example Questions

The user experience is identical to v1. You can ask the same questions, but the agent will be much faster and more efficient behind the scenes.

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
