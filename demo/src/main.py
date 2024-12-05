import streamlit as st
# Set page config at the very beginning
st.set_page_config(
    page_title="Build Dashboard",
    page_icon="🔥",
    layout="wide"
)

import pandas as pd
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
sys.path.append(str(Path(__file__).parent))
from models import StatusEnum
from schema import get_sample_workflows

# Styling helpers
def get_status_color(status: StatusEnum) -> str:
    colors = {
        StatusEnum.SUCCESS: "success",
        StatusEnum.FAILED: "error",
        StatusEnum.RUNNING: "info",
        StatusEnum.PENDING: "secondary",
        StatusEnum.WARNING: "warning"
    }
    return colors.get(status, "secondary")

def format_time(dt) -> str:
    return dt.strftime("%H:%M:%S")

def style_status(val):
    color = get_status_color(StatusEnum(val))
    return f'color: {color};'

def get_metrics_data():
    # Last 7 days of data
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7)]
    dates.reverse()
    
    return {
        'queue_metrics': {
            'current_queued_jobs': 23,
            'avg_queue_time_mins': 18,
            'jobs_exceeding_threshold': 5,
            'threshold_mins': 30,
        },
        'build_metrics': {
            'total_builds_24h': 156,
            'failed_builds_24h': 12,
            'success_rate': 92.3,
            'avg_build_time_mins': 45,
        },
        'queue_time_history': pd.DataFrame({
            'date': dates,
            'avg_queue_time': [15, 22, 18, 25, 30, 16, 18],
            'max_queue_time': [45, 60, 50, 75, 90, 40, 45]
        }),
        'build_history': pd.DataFrame({
            'date': dates,
            'success': [120, 115, 125, 118, 122, 130, 144],
            'failed': [10, 15, 8, 12, 8, 10, 12]
        })
    }

def render_metrics_dashboard():
    st.header("📊 Key Metrics")
    
    # Get metrics data
    metrics = get_metrics_data()
    
    # Alert section
    alert_col1, alert_col2 = st.columns(2)
    with alert_col1:
        if metrics['queue_metrics']['jobs_exceeding_threshold'] > 0:
            st.error(f"⚠️ {metrics['queue_metrics']['jobs_exceeding_threshold']} jobs exceeding {metrics['queue_metrics']['threshold_mins']} min queue threshold")
    with alert_col2:
        if metrics['build_metrics']['failed_builds_24h'] > 10:
            st.error(f"⚠️ High number of failed builds in last 24h: {metrics['build_metrics']['failed_builds_24h']}")

    # Metrics Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Current Queued Jobs",
            metrics['queue_metrics']['current_queued_jobs']
        )
    with col2:
        st.metric(
            "Avg Queue Time (mins)",
            metrics['queue_metrics']['avg_queue_time_mins']
        )
    with col3:
        st.metric(
            "Build Success Rate (24h)",
            f"{metrics['build_metrics']['success_rate']}%"
        )
    with col4:
        st.metric(
            "Avg Build Time (mins)",
            metrics['build_metrics']['avg_build_time_mins']
        )

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Queue Time Trends")
        queue_df = metrics['queue_time_history']
        st.line_chart(
            queue_df.set_index('date')[['avg_queue_time', 'max_queue_time']],
            use_container_width=True
        )

    with chart_col2:
        st.subheader("Build Success/Failure Trends")
        build_df = metrics['build_history']
        st.bar_chart(
            build_df.set_index('date')[['success', 'failed']],
            use_container_width=True
        )

def render_workflow_dashboard():
    # Filters
    with st.expander("Filters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.selectbox("Branch", ["All", "main", "nightly"])
        with col2:
            st.selectbox("Status", ["All"] + [s.value for s in StatusEnum])
        with col3:
            st.selectbox("Author", ["All", "pytorch-bot", "contributor"])

    # Workflows
    workflows = get_sample_workflows()
    for workflow in workflows:
        with st.container():
            # Main workflow card
            with st.expander(
                f"{workflow.name} ({workflow.status.value})",
                expanded=workflow.status in [StatusEnum.RUNNING, StatusEnum.FAILED]
            ):
                # Workflow header
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.caption(f"Branch: {workflow.branch}")
                    st.caption(f"Commit: {workflow.commit}")
                with col2:
                    st.caption(f"Author: {workflow.author}")
                    st.caption(f"Started: {format_time(workflow.start_time)}")
                with col3:
                    st.caption(f"Duration: {workflow.duration}")
                    st.markdown(
                        f"<span style='color: {get_status_color(workflow.status)};'>"
                        f"●</span> {workflow.status.value.title()}",
                        unsafe_allow_html=True
                    )

                # Jobs table
                jobs_data = [
                    {
                        "Job": job.name,
                        "Status": job.status.value,
                        "Duration": job.duration,
                        "Error": job.error or ""
                    }
                    for job in workflow.jobs
                ]
                df = pd.DataFrame(jobs_data)
                
                styled_df = df.style.applymap(
                    style_status, 
                    subset=['Status']
                )
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True
                )

        st.markdown("---")

def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔥 Build Dashboard")
        st.caption("Real-time monitoring dashboard")
    with col2:
        st.button("🔄 Refresh", type="primary")
        auto_refresh = st.toggle("Auto-refresh")

    # Tab-based navigation
    tab1, tab2 = st.tabs(["📊 Metrics Overview", "🔄 Workflow Status"])
    
    with tab1:
        render_metrics_dashboard()
    
    with tab2:
        render_workflow_dashboard()

    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()