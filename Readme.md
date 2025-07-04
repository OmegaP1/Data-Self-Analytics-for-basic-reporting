# Data Self Analytics - Multi-Agent System

A comprehensive analytics platform featuring four specialized AI agents that provide natural language interfaces for data exploration, visualization, and report generation. Built with Google Vertex AI and the Google ADK (Agent Development Kit).

## 🎯 Overview

This project transforms raw CSV data into actionable insights through a progressive agent architecture:

- **Agent 1 (CSV)**: Direct CSV querying with pandas
- **Agent 2 (SQL)**: High-performance SQLite database queries  
- **Agent 3 (Graphics)**: Data visualization and chart generation
- **Agent 4 (Reports)**: Automated multi-part report creation

## 🏗️ Architecture

```
data-self-analytics/
├── agents/
│   ├── 1 - CSV Agent/           # Direct CSV analysis
│   ├── 2 - SQL Agent/           # SQLite database queries
│   ├── 3 - Graphics Agent/      # Data visualization
│   └── 4 - Reports Agent/       # Automated report generation
├── data/
│   ├── raw/                     # Original CSV files
│   └── processed/               # SQLite database
├── src/
│   ├── main.py                  # Data processing pipeline
│   └── preprocessing/
│       └── cleaner.py           # Data cleaning utilities
├── requirements.txt
├── environment.yaml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Project with Vertex AI enabled
- Google ADK installed (`pip install google-adk`)

### 1. Environment Setup

Create `.env` files in each agent directory:

```ini
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=your-gcp-region
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# Agent Configuration
AGENT_MODEL=gemini-2.5-pro
BUCKET_NAME=your-bucket-name
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using conda:

```bash
conda env create -f environment.yaml
conda activate data_self_analytics_for_basic_reporting_agent
```

### 3. Data Preparation

Place your CSV file at `data/raw/data.csv`, then run the preprocessing pipeline:

```bash
python src/main.py
```

This generates the optimized SQLite database at `data/processed/analytics.db`.

### 4. Launch Agents

```bash
cd agents/
adk web
```

Access the web interface at `http://localhost:8000` and select your desired agent.

## 🤖 Agent Capabilities

### Agent 1: CSV Direct Analysis
**Best for**: Initial data exploration, small datasets

- Direct pandas operations on CSV files
- Schema inspection and data type analysis
- Natural language to Python code generation
- Real-time query execution


### Agent 2: SQL Database Queries  
**Best for**: Large datasets, complex queries, production use

- High-performance SQLite queries
- Automatic schema discovery
- SQL generation from natural language
- Optimized for speed and scalability

### Agent 3: Data Visualization
**Best for**: Charts, graphs, visual insights

- Matplotlib and Seaborn integration
- Professional chart styling
- Multiple visualization types (bar, line, pie, heatmap)
- Automatic image saving and management

### Agent 4: Report Generation
**Best for**: Comprehensive analysis, executive summaries

- Multi-step report planning and execution
- Combines data tables with visualizations
- Markdown report generation
- Organized file management


## 📊 Data Processing Pipeline

### Raw Data → Clean Data → SQLite Database

1. **Input**: CSV files in `data/raw/`
2. **Processing**: `src/main.py` orchestrates the pipeline
3. **Cleaning**: `src/preprocessing/cleaner.py` handles data preprocessing
4. **Output**: Optimized SQLite database in `data/processed/`

### Customizing Data Cleaning

Edit `src/preprocessing/cleaner.py` to match your data schema:

```python
# Example customizations
column_mapping = {
    'old_column_name': 'new_column_name',
    # Add your mappings
}

# Handle missing values
for col in ['numeric_columns']:
    if col in self.df.columns:
        self.df[col].fillna(self.df[col].median(), inplace=True)
```

## 🛠️ Technical Details

### Key Dependencies

- **google-adk**: Agent Development Kit
- **google-cloud-aiplatform**: Vertex AI integration
- **pandas**: Data manipulation
- **matplotlib/seaborn**: Visualization
- **sqlite3**: Database operations

### Model Configuration

All agents use Gemini 2.5 Pro by default. Modify in `.env`:

```ini
AGENT_MODEL=gemini-1.5-pro-001  # Alternative model
```

### Performance Considerations

- **Agent 1**: Limited by CSV file size and memory
- **Agent 2-4**: Optimized for large datasets via SQLite
- **Chunked Processing**: Handles files larger than memory
- **Efficient Indexing**: SQLite provides fast query performance

## 🔧 Configuration

### Directory Structure Requirements

Agents expect this exact structure:

```
project-root/
├── agents/           # Agent implementations
├── data/
│   ├── raw/         # Original CSV files
│   └── processed/   # Generated SQLite database
```

### Google Cloud Setup

1. Enable Vertex AI API in your GCP project
2. Set up authentication (service account or gcloud auth)
3. Configure project ID and region in `.env` files

## 📈 Example Use Cases

### Business Intelligence
- Employee headcount analysis
- Geographic distribution reports
- Organizational structure insights
- Performance metrics tracking

### Data Exploration
- Quick dataset overview
- Column distribution analysis
- Missing value assessment
- Data quality checks

### Executive Reporting
- Multi-page analytical reports
- Combined data tables and charts
- Professional formatting
- Automated generation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Database not found**: Ensure you've run `python src/main.py` to generate `analytics.db`

**Authentication errors**: Verify your Google Cloud credentials and project settings

**Import errors**: Install all dependencies with `pip install -r requirements.txt`

### Getting Help

1. Check agent-specific README files in each agent directory
2. Review the `.env` configuration examples
3. Ensure your data follows the expected schema
4. Verify Google Cloud project permissions
