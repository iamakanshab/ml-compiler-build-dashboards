import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path
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

# Main app
def main():
    st.set_page_config(
        page_title="PyTorch HUD",
        page_icon="🔥",
        layout="wide"
    )

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔥 PyTorch HUD")
        st.caption("Showing recent workflow runs")
    with col2:
        st.button("🔄 Refresh", type="primary")
        auto_refresh = st.toggle("Auto-refresh")

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
                
                # Style the dataframe
                def style_status(val):
                    color = get_status_color(StatusEnum(val))
                    return f'color: {color};'
                
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

    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()