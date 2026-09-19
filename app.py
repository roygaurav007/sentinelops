"""
app.py
SentinelOps — System Health & AI-Powered Log Monitor.

Streamlit dashboard with three views:
  1. Live System Metrics  — CPU / memory / disk, with threshold alerts
  2. Log Analyzer         — upload or use sample logs, see error trends
  3. AI Assistant         — Groq-powered root-cause explanation
  4. Alert History        — everything that's tripped a threshold

Run locally:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from alerts import check_log_spikes, check_metric_thresholds
from ai_summarizer import explain_error
from db import clear_alerts, get_alerts, init_db
from log_analyzer import get_level_counts, get_top_errors, parse_log_text
from monitor import get_system_metrics

SAMPLE_LOG_PATH = Path(__file__).parent / "sample_logs" / "app.log"

st.set_page_config(page_title="SentinelOps", page_icon="🛰️", layout="wide")
init_db()

if "metric_history" not in st.session_state:
    st.session_state.metric_history = []

# ---------------------------------------------------------------- sidebar
st.sidebar.title("🛰️ SentinelOps")
page = st.sidebar.radio(
    "Navigate",
    ["Live System Metrics", "Log Analyzer", "AI Assistant", "Alert History"],
)
st.sidebar.divider()
groq_key_input = st.sidebar.text_input(
    "Groq API key (optional)",
    type="password",
    help="Only needed for the AI Assistant page. Falls back to the "
    "GROQ_API_KEY environment variable / Streamlit secret if left blank.",
)
st.sidebar.caption(
    "AI-powered support monitoring tool built with Python, Streamlit and "
    "the Groq API."
)

# ------------------------------------------------------- Live System Metrics
if page == "Live System Metrics":
    st.title("Live System Metrics")

    col1, col2 = st.columns([1, 4])
    with col1:
        refresh = st.button("🔄 Refresh now")
    with col2:
        cpu_thresh = st.slider("CPU alert threshold (%)", 50, 100, 80)

    if refresh or not st.session_state.metric_history:
        metrics = get_system_metrics()
        st.session_state.metric_history.append(metrics)
        st.session_state.metric_history = st.session_state.metric_history[-30:]
        triggered = check_metric_thresholds(metrics, cpu_threshold=cpu_thresh)
        for alert in triggered:
            st.warning(f"⚠️ {alert['severity']}: {alert['message']}")

    if st.session_state.metric_history:
        latest = st.session_state.metric_history[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CPU", f"{latest['cpu_percent']}%")
        c2.metric("Memory", f"{latest['memory_percent']}%",
                  f"{latest['memory_used_gb']} / {latest['memory_total_gb']} GB")
        c3.metric("Disk", f"{latest['disk_percent']}%",
                  f"{latest['disk_used_gb']} / {latest['disk_total_gb']} GB")
        c4.metric("Uptime", latest["uptime"])

        hist_df = pd.DataFrame(st.session_state.metric_history)
        fig = px.line(
            hist_df, x="timestamp", y=["cpu_percent", "memory_percent"],
            labels={"value": "%", "timestamp": "Time", "variable": "Metric"},
            title="CPU & Memory over recent refreshes",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click 'Refresh now' to take the first reading.")

# --------------------------------------------------------------- Log Analyzer
elif page == "Log Analyzer":
    st.title("Log Analyzer")
    st.caption("Upload a .log/.txt file, or analyze the bundled sample log.")

    uploaded = st.file_uploader("Upload a log file", type=["log", "txt"])
    error_thresh = st.slider("Flag as alert if an error repeats at least N times", 2, 20, 5)

    if uploaded is not None:
        text = uploaded.read().decode("utf-8", errors="replace")
        source_label = uploaded.name
    elif SAMPLE_LOG_PATH.exists():
        text = SAMPLE_LOG_PATH.read_text(encoding="utf-8", errors="replace")
        source_label = "sample_logs/app.log (bundled demo data)"
        st.info(f"No file uploaded — showing {source_label}. Upload your own above anytime.")
    else:
        text = ""
        source_label = None
        st.warning("No log file available. Upload one, or run generate_sample_logs.py locally.")

    if text:
        df = parse_log_text(text)
        st.subheader(f"Parsed {len(df)} lines from {source_label}")

        level_counts = get_level_counts(df)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(level_counts, x="level", y="count", color="level",
                         title="Log volume by severity")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            top_errors = get_top_errors(df)
            if not top_errors.empty:
                st.write("**Most frequent errors**")
                st.dataframe(top_errors, use_container_width=True, hide_index=True)
            else:
                st.success("No recurring errors found in this log.")

        triggered = check_log_spikes(level_counts, error_threshold=error_thresh)
        for alert in triggered:
            st.error(f"🚨 {alert['severity']}: {alert['message']}")

        st.write("**Full parsed log**")
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
        st.session_state["last_parsed_df"] = df

# --------------------------------------------------------------- AI Assistant
elif page == "AI Assistant":
    st.title("AI Assistant")
    st.caption("Pick an error from the last analyzed log and get a root-cause explanation.")

    df = st.session_state.get("last_parsed_df")
    if df is None or df.empty:
        st.info("Visit the Log Analyzer page first so there's something to explain.")
    else:
        problem_msgs = sorted(df[df["level"].isin(["ERROR", "CRITICAL"])]["message"].unique())
        if not problem_msgs:
            st.success("No ERROR/CRITICAL lines in the last analyzed log — nothing to explain.")
        else:
            selected = st.selectbox("Select an error message", problem_msgs)
            if st.button("Explain with AI"):
                with st.spinner("Asking the model..."):
                    explanation = explain_error(selected, api_key=groq_key_input or None)
                st.markdown(explanation)

# --------------------------------------------------------------- Alert History
elif page == "Alert History":
    st.title("Alert History")
    alerts = get_alerts()
    if not alerts:
        st.info("No alerts recorded yet. Trigger some from the other pages.")
    else:
        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)
        if st.button("Clear history"):
            clear_alerts()
            st.rerun()
