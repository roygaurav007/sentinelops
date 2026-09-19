# SentinelOps — System Health & AI-Powered Log Monitor

A Python monitoring dashboard that watches live system health, parses
application logs to surface recurring errors, and uses an LLM (via Groq)
to suggest a probable root cause for a selected error — the kind of
day-to-day "software detective" work an application support engineer does.

**[Live Demo](#)** — link added after deployment

## Tech Stack
Python, Streamlit, Pandas, psutil, Plotly, Groq API (Llama 3.3), SQLite

## Features
- **Live system metrics** — CPU, memory, disk and uptime, with a rolling
  chart and configurable alert thresholds.
- **Log analyzer** — parses `.log`/`.txt` files with regex, tolerates
  malformed lines instead of crashing, and surfaces the most frequently
  recurring errors and severity breakdown.
- **AI root-cause assistant** — select any parsed error and get a short,
  structured explanation (likely cause, component, next debugging step,
  severity) from an LLM.
- **Alert history** — every threshold breach (system or log-based) is
  persisted to SQLite and viewable/clearable from the UI.
- Ships with a synthetic sample log (`sample_logs/app.log`) so the demo
  is meaningful even with no real production traffic behind it.

## Project Structure
```
app.py                  Streamlit UI and page routing
monitor.py              psutil-based system metrics
log_analyzer.py         Regex log parsing + error frequency analysis
alerts.py               Threshold checks -> alert records
ai_summarizer.py        Groq API call for root-cause explanations
db.py                   SQLite persistence for alert history
generate_sample_logs.py Synthetic log generator for demos/testing
sample_logs/app.log     Bundled demo log
```

## Run Locally
```
pip install -r requirements.txt
python generate_sample_logs.py   # optional, regenerates the sample log
streamlit run app.py
```

The AI Assistant page needs a Groq API key (free tier available at
console.groq.com). Paste it into the sidebar field, or set it as an
environment variable before launching:
```
export GROQ_API_KEY=your_key_here   # PowerShell: $env:GROQ_API_KEY="your_key_here"
```

## Deployment
Deployed on Streamlit Community Cloud directly from this GitHub repo.
See the deployment guide for exact steps.

## Why this project
Maps directly to core application-support responsibilities: monitoring
system performance, diagnosing issues from logs, documenting findings,
and (optionally) using generative AI to accelerate root-cause analysis.
