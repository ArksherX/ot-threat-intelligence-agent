# 🚀 Quick Start Guide

Get the OT Threat Intelligence Agent running in 5 minutes!

---

## ⚡ Fast Setup (5 Steps)

### 1. Install Prerequisites

```bash
# Check Python version (need 3.9+)
python --version

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Qwen model (this downloads ~5GB, be patient)
ollama pull qwen2.5:latest
```

### 2. Clone & Setup Project

```bash
# Clone the repository
git clone https://github.com/yourusername/ot-threat-intelligence-agent.git
cd ot-threat-intelligence-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your NVD API key
# Get free key at: https://nvd.nist.gov/developers/request-an-api-key
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```
NVD_API_KEY=your-actual-api-key-here
QWEN_MODEL=qwen2.5:latest
FETCH_INTERVAL_MINUTES=10
```

### 4. Run the Agent (Test Mode)

```bash
# Fetch CVEs from last 2 days (good for testing)
python run_agent.py --fallback
```

Expected output:
```
╔═══════════════════════════════════════════════════════════════╗
║          OT THREAT INTELLIGENCE AGENT v1.0                    ║
╚═══════════════════════════════════════════════════════════════╝

[PHASE 1] Fetching latest CVEs from NVD...
Fetched 15 new CVEs

[PHASE 2] Filtering for OT/ICS relevance using Qwen AI...
[1/15] Analyzing CVE-2026-12345...
  ✓ OT-RELEVANT: CVE-2026-12345
...

Total OT Threats: 3
Report saved to: data/output_sample.json
```

### 5. Launch Dashboard

```bash
# Open new terminal, activate venv, then run:
streamlit run src/dashboard.py
```

Open browser: **http://localhost:8501**

---

## 🎯 Common Use Cases

### Testing the Agent

```bash
# Test with recent CVEs (last 2 days)
python run_agent.py --fallback
```

### Real-Time Monitoring

```bash
# Run once (checks last 10 minutes)
python run_agent.py

# Run continuously (checks every 10 minutes)
python run_agent.py --continuous

# Custom interval (every 15 minutes)
python run_agent.py --continuous --interval 15
```

### Dashboard Only

```bash
# Just launch the dashboard (reads existing data)
streamlit run src/dashboard.py
```

---

## 📊 What You'll See

### Terminal Output

```
2026-01-26 10:30:00 - INFO - Starting agent cycle...
2026-01-26 10:30:02 - INFO - Fetched 15 new CVEs
2026-01-26 10:30:05 - INFO - [1/15] Analyzing CVE-2026-12345...
2026-01-26 10:30:10 - INFO -   ✓ OT-RELEVANT
2026-01-26 10:32:00 - INFO - Identified 2 OT-relevant threats
2026-01-26 10:32:01 - INFO - Report saved to data/output_sample.json
```

### Dashboard

![Dashboard showing threat cards with severity badges, CVSS scores, and AI insights]

Key features:
- ✅ Real-time threat count and severity breakdown
- ✅ Detailed threat cards with AI impact analysis
- ✅ Filtering by severity and CVSS score
- ✅ Auto-refresh option
- ✅ JSON export

---

## 🔧 Troubleshooting

### Problem: "Ollama not found"

```bash
# Verify Ollama is installed
ollama --version

# If not, install it
curl -fsSL https://ollama.com/install.sh | sh
```

### Problem: "No CVEs found"

This is normal if:
- No CVEs were published in the last 10 minutes
- Use `--fallback` flag to test with recent CVEs

```bash
python run_agent.py --fallback
```

### Problem: "NVD API rate limit"

Get a free API key to increase limits:
1. Visit: https://nvd.nist.gov/developers/request-an-api-key
2. Register and get your key
3. Add to `.env` file

### Problem: "Qwen timeout"

Your system may need more RAM or a smaller model:

```bash
# Pull smaller model
ollama pull qwen2.5:7b

# Update .env
QWEN_MODEL=qwen2.5:7b
```

### Problem: "Dashboard not loading"

```bash
# Ensure streamlit is installed
pip install streamlit

# Check if port 8501 is available
# On Linux/Mac:
lsof -i :8501

# On Windows:
netstat -ano | findstr :8501
```

---

## 🐳 Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build and start all services
docker-compose up -d

# Pull Qwen model (one-time)
docker exec -it ot-agent-ollama ollama pull qwen2.5:latest

# View logs
docker-compose logs -f agent

# Access dashboard
# Open: http://localhost:8501
```

---

## 📁 File Locations

After first run, you'll see:

```
data/
├── output_sample.json  ← Your threat report
└── cve_cache.json      ← Processed CVE IDs

logs/
└── agent.log           ← Application logs
```

---

## 🎓 Next Steps

1. **Customize Keywords**: Edit OT keywords in `src/ai_agent.py`
2. **Adjust Intervals**: Change check frequency in `.env`
3. **Set Up Notifications**: Add email/Slack alerts (future feature)
4. **Schedule Production**: Use cron/systemd for continuous monitoring
5. **Integrate with SIEM**: Export JSON to your security tools

---

## 💡 Pro Tips

1. **Run in Background**:
   ```bash
   nohup python run_agent.py --continuous > agent.out 2>&1 &
   ```

2. **Auto-Start Dashboard**:
   ```bash
   # Add to ~/.bashrc or create systemd service
   alias ot-dashboard="cd ~/ot-threat-intelligence-agent && streamlit run src/dashboard.py"
   ```

3. **Monitor Logs**:
   ```bash
   tail -f logs/agent.log
   ```

4. **Regular Reports**:
   ```bash
   # Check data directory for timestamped reports
   ls -lh data/
   ```

---

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review logs in `logs/agent.log`
- Verify Ollama is running: `ollama list`
- Test NVD API: `curl "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=1"`

---

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Ollama installed and running
- [ ] Qwen model pulled (`ollama list` shows qwen2.5)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows streamlit, requests, etc.)
- [ ] .env file created with NVD_API_KEY
- [ ] Agent runs successfully (`python run_agent.py --fallback`)
- [ ] Dashboard displays threats (`streamlit run src/dashboard.py`)

---

**🎉 Congratulations! Your OT Threat Intelligence Agent is running!**
