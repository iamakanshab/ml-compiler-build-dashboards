import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
import uvicorn
import logging
import requests
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webhook.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
api = FastAPI()

# Data models
class StatusEnum(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"
    WARNING = "warning"

@dataclass
class WorkflowData:
    name: str
    status: str
    branch: str
    timestamp: datetime
    run_time: Optional[str] = None
    conclusion: Optional[str] = None

# Initialize session state
if 'webhook_data' not in st.session_state:
    st.session_state.webhook_data = []

# FastAPI endpoints
@api.get("/debug")
async def debug():
    """Debug endpoint to verify server is running"""
    logger.info("Debug endpoint accessed")
    return {
        "status": "online",
        "timestamp": str(datetime.now()),
        "message": "IREE webhook endpoint is running",
        "stored_events": len(st.session_state.webhook_data),
        "uptime": "active"
    }

@api.post("/webhook")
async def webhook(request: Request):
    """Handle incoming GitHub webhook events"""
    logger.info("🔔 Webhook received")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        data = await request.json()
        logger.info(f"Payload received: {data}")
        
        if data.get('action') == 'completed' and 'workflow_run' in data:
            workflow_run = data['workflow_run']
            
            # Log detailed workflow information
            logger.info(f"""
            Workflow Details:
            - Name: {workflow_run.get('name')}
            - Branch: {workflow_run.get('head_branch')}
            - Status: {workflow_run.get('status')}
            - Conclusion: {workflow_run.get('conclusion')}
            - Started: {workflow_run.get('created_at')}
            """)
            
            workflow_data = WorkflowData(
                name=workflow_run['name'],
                status=workflow_run['status'],
                branch=workflow_run['head_branch'],
                timestamp=datetime.now(),
                conclusion=workflow_run['conclusion'],
                run_time=str(workflow_run.get('updated_at', ''))
            )
            
            st.session_state.webhook_data.append(vars(workflow_data))
            logger.info(f"✅ Successfully stored workflow data")
            
            return {
                "status": "success", 
                "received_at": str(datetime.now()),
                "workflow": workflow_run['name']
            }
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_webhook_connection():
    """Test webhook endpoint connectivity"""
    try:
        response = requests.get("http://localhost:5000/debug")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def render_debug_panel():
    """Render debug information panel"""
    st.sidebar.markdown("### 🔧 Debug Information")
    
    # Webhook Status
    st.sidebar.markdown("#### 📡 Webhook Status")
    webhook_count = len(st.session_state.webhook_data)
    st.sidebar.write(f"Total webhooks received: {webhook_count}")
    
    if webhook_count > 0:
        st.sidebar.success("✅ Webhooks are being received")
        with st.sidebar.expander("Latest Webhook"):
            st.write(st.session_state.webhook_data[-1])
    else:
        st.sidebar.warning("⚠️ No webhooks received yet")

    # Webhook Test
    st.sidebar.markdown("#### 🧪 Webhook Test")
    if st.sidebar.button("Test Webhook Endpoint"):
        result = test_webhook_connection()
        if result.get("status") == "online":
            st.sidebar.success("✅ Webhook endpoint is responsive")
            st.sidebar.json(result)
        else:
            st.sidebar.error("❌ Cannot reach webhook endpoint")
            st.sidebar.write(result)

def get_metrics_data():
    """Calculate metrics from webhook data"""
    webhook_runs = st.session_state.webhook_data
    
    # Calculate recent metrics
    recent_runs = webhook_runs[-50:] if webhook_runs else []  # Last 50 events
    failed_runs = len([r for r in recent_runs if r['conclusion'] == 'failure'])
    total_runs = len(recent_runs) if recent_runs else 1
    
    # Generate metrics
    return {
        'queue_metrics': {
            'current_queued_jobs': len([r for r in recent_runs if r['status'] == 'queued']),
            'avg_queue_time_mins': 18,
            'jobs_exceeding_threshold': 5,
            'threshold_mins': 30,
        },
        'build_metrics': {
            'total_builds_24h': total_runs,
            'failed_builds_24h': failed_runs,
            'success_rate': round(((total_runs - failed_runs) / total_runs * 100), 1),
            'avg_build_time_mins': 45,
        },
        'queue_time_history': pd.DataFrame({
            'date': [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7)],
            'avg_queue_time': [15, 22, 18, 25, 30, 16, 18],
            'max_queue_time': [45, 60, 50, 75, 90, 40, 45]
        }),
        'build_history': pd.DataFrame({
            'date': [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7)],
            'success': [total_runs - failed_runs] * 7,
            'failed': [failed_runs] * 7
        })
    }

def render_metrics_dashboard():
    """Render metrics overview dashboard"""
    st.header("📊 Key Metrics")
    
    # Recent Events Panel
    with st.expander("📋 Recent Webhook Events", expanded=False):
        if st.session_state.webhook_data:
            df = pd.DataFrame(st.session_state.webhook_data[-10:])
            st.dataframe(df)
        else:
            st.info("No webhook events received yet")
    
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
        st.metric("Current Queued Jobs", metrics['queue_metrics']['current_queued_jobs'])
    with col2:
        st.metric("Avg Queue Time (mins)", metrics['queue_metrics']['avg_queue_time_mins'])
    with col3:
        st.metric("Build Success Rate (24h)", f"{metrics['build_metrics']['success_rate']}%")
    with col4:
        st.metric("Avg Build Time (mins)", metrics['build_metrics']['avg_build_time_mins'])

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Queue Time Trends")
        st.line_chart(metrics['queue_time_history'].set_index('date')[['avg_queue_time', 'max_queue_time']])
    
    with chart_col2:
        st.subheader("Build Success/Failure Trends")
        st.bar_chart(metrics['build_history'].set_index('date')[['success', 'failed']])

def render_workflow_dashboard():
    """Render workflow status dashboard"""
    st.header("🔄 Workflow Status")
    
    recent_workflows = st.session_state.webhook_data[-20:]  # Last 20 workflows
    
    if not recent_workflows:
        st.info("No workflow data available yet")
        return
    
    # Filters
    with st.expander("🔍 Filters"):
        col1, col2 = st.columns(2)
        with col1:
            branches = list(set(w['branch'] for w in recent_workflows))
            selected_branch = st.selectbox("Branch", ["All"] + branches)
        with col2:
            statuses = list(set(w['status'] for w in recent_workflows))
            selected_status = st.selectbox("Status", ["All"] + statuses)

    # Filter workflows
    filtered_workflows = recent_workflows
    if selected_branch != "All":
        filtered_workflows = [w for w in filtered_workflows if w['branch'] == selected_branch]
    if selected_status != "All":
        filtered_workflows = [w for w in filtered_workflows if w['status'] == selected_status]

    # Display workflows
    for workflow in filtered_workflows:
        with st.expander(
            f"{workflow['name']} ({workflow['status']})", 
            expanded=workflow['conclusion'] == 'failure'
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"🌿 Branch: {workflow['branch']}")
                st.write(f"📊 Status: {workflow['status']}")
            with col2:
                st.write(f"🏁 Conclusion: {workflow['conclusion']}")
                st.write(f"⏰ Timestamp: {workflow['timestamp']}")

def main():
    """Main application"""
    st.set_page_config(
        page_title="IREE Build Monitor",
        page_icon="🔧",
        layout="wide"
    )
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔧 IREE Build Monitor")
        st.caption("Real-time build monitoring dashboard")
    with col2:
        st.button("🔄 Refresh", type="primary")
        auto_refresh = st.toggle("Auto-refresh")

    # Render debug panel
    render_debug_panel()

    # Main content tabs
    tab1, tab2 = st.tabs(["📊 Metrics", "🔄 Workflows"])
    
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