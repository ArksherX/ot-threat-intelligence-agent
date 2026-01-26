# 🏗️ Architecture & Technical Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OT THREAT INTELLIGENCE AGENT                    │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│   NVD API        │          │   Qwen LLM       │
│   (NIST)         │          │   (via Ollama)   │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         │ REST API                    │ Local CLI
         │ (JSON)                      │ (Subprocess)
         │                             │
         ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENT CORE                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│  │   Phase 1   │──▶│   Phase 2   │──▶│   Phase 3   │              │
│  │    Data     │   │     AI      │   │   Report    │              │
│  │  Pipeline   │   │   Agent     │   │  Generator  │              │
│  └─────────────┘   └─────────────┘   └──────┬──────┘              │
│         │                                    │                     │
│         ▼                                    ▼                     │
│  ┌─────────────┐                    ┌─────────────┐               │
│  │ CVE Cache   │                    │  JSON       │               │
│  │ (Local)     │                    │  Report     │               │
│  └─────────────┘                    └──────┬──────┘               │
└────────────────────────────────────────────┼──────────────────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │   Phase 4       │
                                     │   Dashboard     │
                                     │   (Streamlit)   │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │   Web Browser   │
                                     │   (localhost)   │
                                     └─────────────────┘
```

---

## Component Details

### 1. Data Pipeline (`data_pipeline.py`)

**Responsibility**: Fetch and extract CVE data from NVD

**Key Functions**:
- `fetch_latest_cves(minutes_ago)`: Query NVD API for recent CVEs
- `fetch_recent_cves_fallback(days)`: Fallback method for testing
- `load_cache()` / `save_cache()`: Prevent duplicate processing

**Data Flow**:
```
NVD API Request → JSON Response → Parse CVEs → Extract Metadata → Cache Check → Return New CVEs
```

**API Integration**:
```python
GET https://services.nvd.nist.gov/rest/json/cves/2.0
Parameters:
  - pubStartDate: ISO 8601 timestamp
  - pubEndDate: ISO 8601 timestamp
  - resultsPerPage: 20 (default)

Headers:
  - apiKey: [your-key] (optional, increases rate limit)
```

**Rate Limiting**:
- Without API key: 5 requests / 30 seconds
- With API key: 50 requests / 30 seconds
- Implementation: 6-second delay between requests

**Extracted Fields**:
```json
{
  "cve_id": "CVE-YYYY-NNNNN",
  "cvss_score": 9.8,
  "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "description": "...",
  "published_date": "2026-01-26T08:15:00.000",
  "last_modified": "2026-01-26T08:15:00.000",
  "references": ["url1", "url2"]
}
```

---

### 2. AI Agent (`ai_agent.py`)

**Responsibility**: Filter CVEs for OT/ICS relevance using AI

**Architecture**:
```
CVE Description
      │
      ▼
┌─────────────────┐
│ Keyword Check   │  ← Fast pre-filter
│ (String Match)  │
└────────┬────────┘
         │ Match found
         ▼
┌─────────────────┐
│  LLM Analysis   │  ← Deep analysis with Qwen
│  (Qwen 2.5)     │
└────────┬────────┘
         │ OT-relevant?
         ▼
┌─────────────────┐
│ Impact Analysis │  ← Generate factory impact
│  (Qwen 2.5)     │
└────────┬────────┘
         │
         ▼
    OT CVE with AI Insight
```

**OT/ICS Keywords**:
```python
keywords = [
    'SCADA', 'PLC', 'HMI', 'ICS', 'OT',
    'Siemens', 'Rockwell', 'Schneider', 'Allen-Bradley',
    'Modbus', 'DNP3', 'OPC', 'Profinet', 'EtherNet/IP',
    'RTU', 'DCS', 'Industrial Control', 'SIMATIC',
    'ControlLogix', 'CompactLogix', 'Modicon'
]
```

**LLM Prompt Templates**:

*Filtering Prompt*:
```
You are a cybersecurity expert specializing in OT/ICS.

Analyze this CVE and determine if it affects OT/ICS environments.

OT/ICS indicators:
- Industrial control systems: SCADA, PLC, HMI, DCS
- Industrial vendors: Siemens, Rockwell, Schneider
- Industrial protocols: Modbus, DNP3, OPC

CVE Description: [...]

Answer ONLY 'YES' or 'NO'.
```

*Impact Analysis Prompt*:
```
Explain in 2-3 sentences why this vulnerability is dangerous 
for industrial facilities.

Focus on:
- Production shutdowns or equipment damage
- Safety hazards to workers
- Loss of process control

CVE: [...]
CVSS: [...]
```

**Qwen Integration**:
```python
# Execute via Ollama CLI
subprocess.run([
    'ollama', 'run', 'qwen2.5:latest',
    prompt
])
```

---

### 3. Report Generator (`report_generator.py`)

**Responsibility**: Structure and persist threat intelligence

**Output Format**:
```json
{
  "generated_at": "ISO 8601 timestamp",
  "report_version": "1.0",
  "total_threats": 3,
  "severity_breakdown": {
    "critical": 1,
    "high": 1,
    "medium": 1,
    "low": 0
  },
  "threats": [
    {
      "cve_id": "CVE-YYYY-NNNNN",
      "cvss_score": 9.8,
      "severity": "CRITICAL",
      "description": "...",
      "ai_insight": "...",
      "published_date": "...",
      "last_modified": "...",
      "references": []
    }
  ]
}
```

**Severity Mapping**:
```
CVSS 9.0 - 10.0  → CRITICAL
CVSS 7.0 - 8.9   → HIGH
CVSS 4.0 - 6.9   → MEDIUM
CVSS 0.1 - 3.9   → LOW
CVSS 0.0         → NONE
```

---

### 4. Dashboard (`dashboard.py`)

**Technology**: Streamlit (Python web framework)

**UI Components**:
```
┌─────────────────────────────────────────────────┐
│  🛡️ OT Threat Intelligence Dashboard           │
├─────────────────────────────────────────────────┤
│  [🔄 Refresh] [☑️ Auto-refresh (30s)]           │
├─────────────────────────────────────────────────┤
│  📊 Metrics:                                    │
│  [Total: 3] [🔴 Critical: 1] [🟠 High: 1]      │
├─────────────────────────────────────────────────┤
│  🎯 Threat Cards:                               │
│  ┌─────────────────────────────────────────┐   │
│  │ 🔴 CVE-2026-12345 - CRITICAL            │   │
│  │ CVSS: 9.8                               │   │
│  │ Description: ...                        │   │
│  │ 🤖 AI Insight: ...                      │   │
│  └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  🔍 Filters: [Severity] [Min CVSS]             │
└─────────────────────────────────────────────────┘
```

**Features**:
- Real-time data loading from JSON
- Auto-refresh with configurable interval
- Severity and CVSS filtering
- Detailed and table view modes
- JSON export functionality

**Refresh Mechanism**:
```python
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()  # Reload dashboard
```

---

## Data Flow Diagram

```
┌─────────────┐
│  Run Agent  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  PHASE 1: Data Pipeline                  │
│  ┌────────────────────────────────────┐  │
│  │ 1. Query NVD API                   │  │
│  │ 2. Parse JSON response             │  │
│  │ 3. Extract CVE metadata            │  │
│  │ 4. Check cache (skip duplicates)   │  │
│  │ 5. Return new CVEs                 │  │
│  └────────────────────────────────────┘  │
└──────┬───────────────────────────────────┘
       │ List[CVE]
       ▼
┌──────────────────────────────────────────┐
│  PHASE 2: AI Agent                       │
│  ┌────────────────────────────────────┐  │
│  │ For each CVE:                      │  │
│  │ 1. Keyword pre-filter              │  │
│  │ 2. LLM relevance check (Qwen)     │  │
│  │ 3. If OT: Generate impact (Qwen)  │  │
│  │ 4. Add AI insight to CVE          │  │
│  └────────────────────────────────────┘  │
└──────┬───────────────────────────────────┘
       │ List[OT_CVE]
       ▼
┌──────────────────────────────────────────┐
│  PHASE 3: Report Generator               │
│  ┌────────────────────────────────────┐  │
│  │ 1. Sort by CVSS score              │  │
│  │ 2. Map to severity levels          │  │
│  │ 3. Calculate statistics            │  │
│  │ 4. Structure as JSON               │  │
│  │ 5. Save to file                    │  │
│  └────────────────────────────────────┘  │
└──────┬───────────────────────────────────┘
       │ JSON File
       ▼
┌──────────────────────────────────────────┐
│  PHASE 4: Dashboard                      │
│  ┌────────────────────────────────────┐  │
│  │ 1. Load JSON report                │  │
│  │ 2. Parse threat data               │  │
│  │ 3. Apply filters                   │  │
│  │ 4. Render UI components            │  │
│  │ 5. Handle user interactions        │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## Deployment Architecture

### Local Deployment
```
┌─────────────────────────────────────┐
│  Developer Machine                  │
│  ┌───────────────────────────────┐  │
│  │  Python Virtual Environment   │  │
│  │  ├─ Agent Process             │  │
│  │  └─ Streamlit Server          │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  Ollama Service               │  │
│  │  └─ Qwen Model                │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Docker Deployment
```
┌─────────────────────────────────────────────┐
│  Docker Host                                │
│  ┌─────────────┐  ┌──────────────────────┐ │
│  │  ollama     │  │  agent               │ │
│  │  container  │◀─┤  container           │ │
│  │  (Qwen LLM) │  │  (Python script)     │ │
│  └─────────────┘  └──────────────────────┘ │
│                   ┌──────────────────────┐ │
│                   │  dashboard           │ │
│                   │  container           │ │
│                   │  (Streamlit)         │ │
│                   └──────┬───────────────┘ │
└──────────────────────────┼─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Port 8501   │
                    │  (Browser)   │
                    └──────────────┘
```

---

## Security Considerations

### API Key Management
- ✅ Store in `.env` file (never commit)
- ✅ Load via `python-dotenv`
- ✅ Optional (agent works without it, with reduced rate limits)

### LLM Security
- ✅ Local execution (Qwen via Ollama)
- ✅ No data sent to external APIs
- ✅ Prompt injection safeguards (simple yes/no outputs)

### Network Security
- ✅ HTTPS for NVD API calls
- ✅ Dashboard on localhost (not exposed by default)
- ✅ No persistence of sensitive data

---

## Performance Optimization

### Caching Strategy
```python
# Processed CVEs cached to avoid re-analysis
cve_cache.json = ["CVE-2026-12345", "CVE-2026-67890", ...]

# Check before processing
if cve_id in processed_cves:
    skip()
```

### Rate Limiting
```python
# Respect NVD API limits
time.sleep(6)  # 6 seconds between requests

# With API key: ~8 requests/minute
# Without key: ~1 request/minute
```

### LLM Optimization
```python
# Pre-filter with keywords (fast)
if not keyword_match:
    skip_llm()  # Save ~10 seconds per CVE

# Only use LLM for promising candidates
# Typical: 5-10 seconds per LLM call
```

---

## Error Handling

```
┌─────────────┐
│  API Error  │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Retry 3x     │
└──────┬───────┘
       │ Fail
       ▼
┌──────────────┐
│ Log Error    │
│ Continue     │
└──────────────┘
```

All errors logged to `logs/agent.log` with full stack traces.

---

## Monitoring & Logging

**Log Levels**:
- `INFO`: Normal operations, CVE counts, phase transitions
- `WARNING`: API rate limits, empty results
- `ERROR`: API failures, LLM timeouts, file I/O errors
- `DEBUG`: Detailed flow, LLM responses (disabled by default)

**Log Format**:
```
2026-01-26 10:30:00 - data_pipeline - INFO - Fetched 15 new CVEs
2026-01-26 10:30:05 - ai_agent - INFO - [1/15] Analyzing CVE-2026-12345
2026-01-26 10:30:10 - ai_agent - INFO -   ✓ OT-RELEVANT
```

---

## Scalability Considerations

### Current Limitations
- Single-threaded processing (sequential CVE analysis)
- Local LLM (CPU/RAM bound)
- No distributed architecture

### Future Enhancements
```
┌────────────────┐
│  Load Balancer │
└────┬───────────┘
     │
     ├───▶ Agent Instance 1 ──▶ Ollama 1
     ├───▶ Agent Instance 2 ──▶ Ollama 2
     └───▶ Agent Instance 3 ──▶ Ollama 3
              │
              ▼
       ┌──────────────┐
       │  Shared DB   │
       │  (PostgreSQL)│
       └──────────────┘
```

---

## Technology Choices Rationale

| Component | Technology | Why? |
|-----------|-----------|------|
| **Language** | Python 3.9+ | Rich ecosystem, NVD API support, AI/ML libraries |
| **LLM** | Qwen 2.5 | Free, local, good reasoning, moderate size |
| **LLM Runner** | Ollama | Easy CLI interface, model management |
| **Dashboard** | Streamlit | Rapid development, built-in components |
| **Data Format** | JSON | Universal, machine-readable, easy integration |
| **API** | NVD/NIST | Authoritative CVE source, well-documented |

---

This architecture provides a solid foundation for real-time OT/ICS threat intelligence while maintaining simplicity, security, and extensibility.
