# 🛡️ OT Threat Intelligence Agent

**Autonomous AI Agent for Real-time Monitoring of OT/ICS Vulnerabilities**

An intelligent cybersecurity agent that monitors the National Vulnerability Database (NVD) for new CVEs, filters for OT/ICS-relevant threats using Qwen LLM, and displays them on a live Streamlit dashboard.
---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Sample Output](#sample-output)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## ✨ Features

- **Real-time CVE Monitoring**: Fetches latest vulnerabilities from NVD API every 10 minutes
- **AI-Powered Filtering**: Uses Qwen LLM to intelligently filter OT/ICS-relevant threats
- **Automated Impact Analysis**: Generates factory/industrial impact assessments for each threat
- **Live Dashboard**: Streamlit-based web interface with real-time updates
- **Structured JSON Reports**: Machine-readable output for integration with other tools
- **Smart Caching**: Avoids processing duplicate CVEs
- **Severity Classification**: Automatic CVSS-based severity categorization

---

## 🏗️ Architecture

```
┌─────────────────┐
│   NVD API       │  ← Fetch latest CVEs
│  (NIST/MITRE)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Pipeline  │  ← Phase 1: Extract CVE data
│  (Python)       │     (ID, CVSS, Description)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │  ← Phase 2: Filter OT/ICS threats
│  (Qwen LLM)     │     Keywords: SCADA, PLC, HMI, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Report Generator│  ← Phase 3: Generate JSON report
│  (Structured)   │     with AI insights
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │  ← Phase 4: Visualize threats
│  (Streamlit)    │     Live web interface
└─────────────────┘
```

### Technology Stack

- **Python 3.9+**: Core programming language
- **NVD API**: CVE data source (NIST National Vulnerability Database)
- **Qwen LLM** (via Ollama): Free, locally-run AI model for filtering
- **Streamlit**: Dashboard framework
- **Pandas**: Data processing
- **Schedule**: Task automation

---

## 📦 Prerequisites

### Required Software

1. **Python 3.9 or higher**
   ```bash
   python --version
   ```

2. **Ollama** (for running Qwen LLM locally)
   ```bash
   # Linux/Mac
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows
   # Download from https://ollama.com/download
   ```

3. **NVD API Key** (free)
   - Register at: https://nvd.nist.gov/developers/request-an-api-key
   - Provides higher rate limits (50 requests/30 seconds vs 5 requests/30 seconds)

### System Requirements

- **RAM**: 8GB minimum (16GB recommended for Qwen model)
- **Disk Space**: 5GB for Qwen model
- **Internet**: Stable connection for NVD API calls

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ArksherX/ot-threat-intelligence-agent.git
cd ot-threat-intelligence-agent
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and Setup Qwen Model

```bash
# Pull Qwen model (this may take a few minutes)
ollama pull qwen2.5:latest

# Verify installation
ollama list
```

---

## ⚙️ Configuration

### Create `.env` File

Create a `.env` file in the project root:

```bash
# NVD API Configuration
NVD_API_KEY=your_api_key_here

# Qwen Model Configuration
QWEN_MODEL=qwen2.5:latest

# Agent Configuration
FETCH_INTERVAL_MINUTES=10
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `NVD_API_KEY` | Your NVD API key | None (optional but recommended) |
| `QWEN_MODEL` | Qwen model version | qwen2.5:latest |
| `FETCH_INTERVAL_MINUTES` | Check frequency | 10 |

---

## 🎯 Usage

### Run Once (Test Mode)

Fetch and analyze CVEs from the last 2 days:

```bash
python run_agent.py --fallback
```

### Run Once (Real-time Mode)

Fetch CVEs from the last 10 minutes:

```bash
python run_agent.py
```

### Run Continuously

Monitor CVEs every 10 minutes:

```bash
python run_agent.py --continuous
```

### Custom Interval

Run with custom interval (e.g., every 15 minutes):

```bash
python run_agent.py --continuous --interval 15
```

### Launch Dashboard

In a **separate terminal**:

```bash
streamlit run src/dashboard.py
```

Dashboard will be available at: **http://localhost:8501**

### Command-Line Options

```
usage: run_agent.py [-h] [--continuous] [--interval INTERVAL] 
                    [--fallback] [--model MODEL]

OT Threat Intelligence Agent

optional arguments:
  -h, --help           show this help message
  --continuous         Run continuously (default: run once)
  --interval INTERVAL  Interval in minutes for continuous mode (default: 10)
  --fallback           Use fallback mode (fetch last 2 days for testing)
  --model MODEL        Qwen model to use (default: qwen2.5:latest)
```

---

## 📁 Project Structure

```
ot-threat-intelligence-agent/
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py      # Phase 1: CVE fetching from NVD
│   ├── ai_agent.py            # Phase 2: AI filtering with Qwen
│   ├── report_generator.py    # Phase 3: JSON report generation
│   └── dashboard.py           # Phase 4: Streamlit dashboard
├── data/
│   ├── output_sample.json     # Generated threat report
│   └── cve_cache.json         # Cache of processed CVEs
├── logs/
│   └── agent.log              # Application logs
├── config/
│   └── config.yaml            # Configuration (optional)
├── tests/
│   └── test_agent.py          # Unit tests (optional)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration (optional)
├── docker-compose.yml         # Docker Compose setup (optional)
├── .env                       # Environment variables (create this)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── run_agent.py               # Main entry point
```

---

## 🔍 How It Works

### Phase 1: Data Pipeline

**File**: `src/data_pipeline.py`

1. Connects to NVD API with optional API key
2. Fetches CVEs published in the last 10 minutes
3. Extracts: CVE ID, CVSS score, description, references
4. Caches processed CVEs to avoid duplicates
5. Returns structured CVE data

**Key Features**:
- Respects NVD API rate limits (6-second delay between requests)
- Supports both real-time and fallback modes
- Handles API errors gracefully

### Phase 2: AI Agent

**File**: `src/ai_agent.py`

1. **Keyword Pre-screening**: Quick check for OT/ICS keywords
   - SCADA, PLC, HMI, ICS, Siemens, Rockwell, Modbus, etc.

2. **LLM Confirmation**: Uses Qwen to verify OT relevance
   - Analyzes full CVE description
   - Binary classification: OT-relevant or IT-only

3. **Impact Analysis**: Generates factory/industrial impact assessment
   - Explains operational risks
   - Considers severity level (CVSS score)

**AI Prompt Strategy**:

```
You are a cybersecurity expert specializing in Operational Technology (OT) 
and Industrial Control Systems (ICS).

Analyze the following CVE description and determine if it is relevant to 
OT/ICS environments such as factories, power plants, or critical infrastructure.

OT/ICS indicators include:
- Industrial control systems: SCADA, PLC, HMI, DCS, RTU
- Industrial vendors: Siemens, Rockwell Automation, Schneider Electric...
- Industrial protocols: Modbus, DNP3, OPC, Profinet...

CVE Description: [...]

Answer with ONLY 'YES' if this CVE affects OT/ICS systems, 
or 'NO' if it only affects standard IT systems.
```

### Phase 3: Report Generation

**File**: `src/report_generator.py`

1. Structures filtered CVEs into JSON format
2. Calculates severity levels from CVSS scores:
   - CRITICAL: 9.0-10.0
   - HIGH: 7.0-8.9
   - MEDIUM: 4.0-6.9
   - LOW: 0.1-3.9

3. Generates severity statistics
4. Saves to `data/output_sample.json`

### Phase 4: Dashboard

**File**: `src/dashboard.py`

1. Loads threat data from JSON report
2. Displays metrics: Total threats, severity breakdown
3. Shows detailed threat cards with:
   - CVE ID and severity badge
   - CVSS score
   - Description
   - AI-generated impact analysis
   - References
4. Features:
   - Manual refresh button
   - Auto-refresh option (configurable interval)
   - Severity filtering
   - CVSS score filtering
   - Table and card view modes
   - JSON download

---

## 📊 Sample Output

### JSON Report (`data/output_sample.json`)

```json
{
  "generated_at": "2026-01-26T10:30:00.000000Z",
  "report_version": "1.0",
  "total_threats": 2,
  "severity_breakdown": {
    "critical": 1,
    "high": 1,
    "medium": 0,
    "low": 0
  },
  "threats": [
    {
      "cve_id": "CVE-2026-12345",
      "cvss_score": 9.8,
      "severity": "CRITICAL",
      "description": "A critical vulnerability in Siemens SIMATIC S7-1200 PLC allows remote code execution through the Profinet protocol...",
      "ai_insight": "This vulnerability poses severe risk to manufacturing facilities using Siemens PLCs. Attackers could gain complete control of production line controllers, potentially causing equipment damage, production shutdowns, or safety incidents. Immediate patching is critical for any facility running affected S7-1200 controllers.",
      "published_date": "2026-01-26T08:15:00.000",
      "last_modified": "2026-01-26T08:15:00.000",
      "references": [
        "https://cert-portal.siemens.com/..."
      ]
    },
    {
      "cve_id": "CVE-2026-67890",
      "cvss_score": 7.5,
      "severity": "HIGH",
      "description": "Authentication bypass in Rockwell Automation FactoryTalk View HMI software...",
      "ai_insight": "This HMI vulnerability could allow unauthorized operators to access and manipulate critical process controls. In industrial environments, this could lead to incorrect parameter settings, unauthorized equipment operation, or disabled safety interlocks, risking both production integrity and worker safety.",
      "published_date": "2026-01-26T09:45:00.000",
      "last_modified": "2026-01-26T09:45:00.000",
      "references": []
    }
  ]
}
```

### Console Output

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          OT THREAT INTELLIGENCE AGENT v1.0                    ║
║          Automated CVE Monitoring for ICS/OT                  ║
║                                                               ║
║          Powered by NVD API + Qwen AI                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

2026-01-26 10:30:00 - INFO - Initializing OT Threat Intelligence Agent...
2026-01-26 10:30:01 - INFO - Ollama verified with model: qwen2.5:latest
2026-01-26 10:30:01 - INFO - Agent initialized successfully

======================================================================
Starting agent cycle...
======================================================================

[PHASE 1] Fetching latest CVEs from NVD...
2026-01-26 10:30:02 - INFO - Fetched 15 new CVEs

[PHASE 2] Filtering for OT/ICS relevance using Qwen AI...
2026-01-26 10:30:05 - INFO - [1/15] Analyzing CVE-2026-12345...
2026-01-26 10:30:10 - INFO -   ✓ OT-RELEVANT: CVE-2026-12345
2026-01-26 10:30:15 - INFO - [2/15] Analyzing CVE-2026-67890...
2026-01-26 10:30:20 - INFO -   ✓ OT-RELEVANT: CVE-2026-67890
...
2026-01-26 10:32:00 - INFO - Identified 2 OT-relevant threats

[PHASE 3] Generating threat intelligence report...
2026-01-26 10:32:01 - INFO - Report saved to data/output_sample.json

======================================================================
CYCLE COMPLETE
======================================================================
Total OT Threats: 2
Report saved to: data/output_sample.json
Critical: 1, High: 1, Medium: 0, Low: 0
======================================================================
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Ollama not found**

```
Error: Ollama is not installed
```

**Solution**: Install Ollama from https://ollama.com

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:latest
```

#### 2. **NVD API Rate Limiting**

```
HTTP Error 429: Too Many Requests
```

**Solution**: 
- Get an API key from NVD (increases limit to 50 req/30s)
- Add to `.env` file: `NVD_API_KEY=your_key_here`

#### 3. **No CVEs Found**

```
No new CVEs found in this cycle
```

**Solution**: This is normal if no CVEs were published recently. Use fallback mode for testing:

```bash
python run_agent.py --fallback
```

#### 4. **Qwen Model Timeout**

```
Error querying Qwen: timeout
```

**Solution**:
- Ensure you have enough RAM (8GB minimum)
- Try a smaller model: `ollama pull qwen2.5:7b`
- Update `.env`: `QWEN_MODEL=qwen2.5:7b`

#### 5. **Dashboard Not Loading**

```
streamlit: command not found
```

**Solution**: Ensure virtual environment is activated and dependencies installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/dashboard.py
```

---

## 🚀 Future Enhancements

### Planned Features

1. **Email/Slack Notifications**: Alert on critical threats
2. **Historical Trending**: Track vulnerability trends over time
3. **Custom Keyword Lists**: User-defined OT vendor/protocol lists
4. **Multi-Source Integration**: CISA ICS alerts, vendor advisories
5. **Threat Prioritization**: Risk scoring based on asset inventory
6. **Remediation Recommendations**: Automated mitigation suggestions
7. **API Endpoint**: RESTful API for integration with SIEM/SOAR
8. **Docker Deployment**: Containerized deployment option

### Extensibility

The agent is designed to be modular and extensible:

- **Custom Data Sources**: Add new CVE sources in `data_pipeline.py`
- **Alternative LLMs**: Swap Qwen for OpenAI/Claude in `ai_agent.py`
- **Enhanced Filtering**: Modify filtering logic in `ai_agent.py`
- **Custom Reports**: Extend `report_generator.py` for different formats

---
## Contributing

Contributions are welcome. Please follow the process below to keep the codebase clean and reviewable.

### Getting Started

1. Fork the repository and clone your fork locally
2. Create a virtual environment and install dependencies: `pip install -r requirements.txt`
3. Pull the Qwen model before running: `ollama pull qwen2.5:latest`
4. Run the agent in fallback mode to verify your setup: `python run_agent.py --fallback`

### Submitting Changes

1. Create a feature branch from main: `git checkout -b feature/your-change-name`
2. Make your changes with clear, descriptive commit messages
3. Test your changes locally before pushing: `python run_agent.py --fallback`
4. Push your branch and open a pull request against main
5. Describe what you changed, why, and how you tested it in the PR description

### Reporting Issues

Open a GitHub issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behaviour
- Your Python version and OS

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to all new functions
- Keep functions focused — one responsibility per function
- Add comments for non-obvious logic, especially in the AI filtering pipeline

### Areas Welcoming Contributions

- Additional OT/ICS keyword coverage in `src/ai_agent.py`
- New CVE data sources beyond NVD in `src/data_pipeline.py`
- Dashboard improvements in `src/dashboard.py`
- Test coverage in `tests/test_agent.py`
- Docker and deployment improvements

For questions, open an issue or reach out via owolabimiracle@gmail.com

## 📝 License

This project is created for the ControlPoint AI & Data Internship Challenge.

---

## 👤 Author

**Your Name**  
- GitHub: Arksher(https://github.com/ArksherX)
- Email: miracle@artonexa.com

---

## 🙏 Acknowledgments

- **NIST NVD**: For providing comprehensive CVE data
- **Ollama Team**: For making LLMs accessible locally
- **Qwen Team**: For the excellent open-source model
- **Streamlit**: For the amazing dashboard framework

---

## 📚 References

- [NVD API Documentation](https://nvd.nist.gov/developers)
- [Qwen Model Card](https://ollama.com/library/qwen2.5)
- [Ollama Documentation](https://ollama.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [CVSS Specification](https://www.first.org/cvss/)

---

**Built with ❤️ for securing critical infrastructure**
