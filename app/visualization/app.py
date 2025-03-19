import streamlit as st
from dotenv import load_dotenv
import os
import json
import pandas as pd
import numpy as np
import tempfile
import sys

# Add the project root to the Python path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_path)

# Load environment variables at the start
load_dotenv()

from app.visualization.planner_viz import PlanVisualizer
from app.planning.system import PlanningSystem
from app.llm.openai_client import OpenAILLMClient
from app.planning.htn import HTNPlanningStrategy
from app.core.models import Plan
from app.visualization.examples import EXAMPLE_PROMPTS


def add_custom_css():
    # Read CSS file
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def show_example_buttons():
    st.write("### 🎯 Try these example prompts:")

    # Add some space and a divider
    st.markdown("<br>", unsafe_allow_html=True)

    # Create three columns for the example buttons
    cols = st.columns(3)

    for col, (title, prompt) in zip(cols, EXAMPLE_PROMPTS.items()):
        with col:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 20px; min-height: 190px; background-color: #242424;
                border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 100%; margin-bottom: 20px'>
                <h4>{title}</h4>
                <p style='font-size: 0.9em; color: #666; margin-bottom: 15px;'>
                {prompt[:100]}...</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Use this example ✨", key=f"example_{title}", use_container_width=True
            ):
                return prompt
    return None


def main():
    st.set_page_config(
        page_title="Modern HTN Planner",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    add_custom_css()
    st.title("📊 HTN Planner Visualization")

    # Initialize session state
    if "request" not in st.session_state:
        st.session_state.request = ""
    if "plan_generated" not in st.session_state:
        st.session_state.plan_generated = False

    # Create a container for example buttons
    example_container = st.empty()

    # Show example buttons only if plan is not generated
    if not st.session_state.plan_generated:
        with example_container.container():
            example_prompt = show_example_buttons()
            if example_prompt:
                st.session_state.request = example_prompt

    with st.sidebar:
        st.header("Planning Parameters")

        with st.container():
            # Use session state for the text area
            request = st.text_area(
                "Enter your planning request:",
                value=st.session_state.request,
                height=120,
                key="request_input",
            )

            col1, col2 = st.columns(2)
            with col1:
                weight_threshold = st.slider("Weight Threshold", 1, 100, 70)
            with col2:
                max_depth = st.slider("Max Depth", 1, 5, 2)

            generate_button = st.button("Generate Plan 🚀", use_container_width=True)

    # Move the plan generation logic outside the if-else block
    if generate_button and request:
        # Clear the example buttons container
        example_container.empty()
        st.session_state.plan_generated = True

        with st.spinner("Generating plan...it may take a few seconds..."):
            # Normal API flow
            llm_client = OpenAILLMClient()
            strategy = HTNPlanningStrategy(llm_client, weight_threshold, max_depth)
            planning_system = PlanningSystem(strategy)
            plan = planning_system.process_request(request)

            # Display success message
            st.success("Plan generated successfully!")

            # Create tabs for different views
            tab1, tab2 = st.tabs(["📈 Interactive Visualization", "📝 Plan Details"])

            with tab1:
                st.subheader("Interactive Plan Visualization")
                st.markdown(
                    "Interact with the visualization: zoom, drag, and hover over nodes for task description."
                )

                # Modern visualization
                visualizer = PlanVisualizer()
                html_path = visualizer.visualize_plan(plan)

                # HTML 파일 읽기 및 표시
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # HTML 컨텐츠를 직접 표시
                with st.container():
                    st.components.v1.html(html_content, height=700, scrolling=False)

                # 임시 파일 삭제
                os.remove(html_path)

            with tab2:
                # Display statistics and markdown in rows
                display_plan_statistics(plan.to_dict(), weight_threshold)  # weight_threshold 전달
                st.markdown("---")
                display_plan_markdown(plan, planning_system)

                    
    else:

        st.info("Enter your planning request and click 'Generate Plan' to start.")

        # st.image("https://via.placeholder.com/800x400.png?text=HTN+Planner+Visualization+Example",
        #          caption="Sample visualization of a hierarchical task network",
        #          use_container_width=True)


def display_plan_statistics(plan_dict, weight_threshold):
    node_dict = plan_dict["plan"]
    
    # 먼저 노드 계산을 수행
    def count_nodes(node_dict):
        count = 1
        weight_sum = node_dict.get("weight", 0)
        depth = 0

        if "children" in node_dict:
            for child in node_dict["children"]:
                child_count, child_weight_sum, child_depth = count_nodes(child)
                count += child_count
                weight_sum += child_weight_sum
                depth = max(depth, child_depth)

        return count, weight_sum, depth + 1

    # 계산된 값들을 저장
    total_nodes, total_weight, max_plan_depth = count_nodes(node_dict)
    avg_weight = total_weight / total_nodes if total_nodes > 0 else 0

    # 가중치 수집
    weights = []
    def collect_weights(node_dict):
        weight = node_dict.get("weight")
        if weight is not None:
            weights.append(float(weight))
        if "children" in node_dict and node_dict["children"]:
            for child in node_dict["children"]:
                collect_weights(child)

    collect_weights(node_dict)

    # 이제 UI 표시
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Plan Statistics")
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric("Total Steps", total_nodes)
        with metric_cols[1]:
            st.metric("Average Complexity", f"{avg_weight:.1f}%")

        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric("Max Depth", max_plan_depth - 1)
        with metric_cols[1]:
            st.metric("Weight Threshold", f"{weight_threshold}%")

    with col2:
        if weights:
            st.subheader("Complexity Distribution")
            bins = [0, 20, 40, 60, 80, 100]
            labels = [
                "Very Low (0-20%)", 
                "Low (21-40%)", 
                "Medium (41-60%)", 
                "High (61-80%)", 
                "Very High (81-100%)"
            ]
            
            hist_data = pd.DataFrame({"weight": weights})
            hist_data["complexity"] = pd.cut(
                hist_data["weight"],
                bins=bins,
                labels=labels,
                include_lowest=True,
            )
            
            complexity_counts = (
                hist_data["complexity"]
                .value_counts()
                .reindex(labels, fill_value=0)
            )
            
            chart_data = pd.DataFrame({
                "Complexity": complexity_counts.index,
                "Count": complexity_counts.values,
            })
            
            st.bar_chart(
                chart_data.set_index("Complexity"),
                height=300
            )
        else:
            st.warning("No complexity data available")

def display_plan_markdown(plan, planning_system):
    st.subheader("Plan in Markdown")
    st.download_button(
        label="Download Plan as Markdown",
        data=planning_system.export_plan(plan, format="md"),
        file_name="plan.md",
        mime="text/markdown",
    )
    st.markdown(planning_system.export_plan(plan, format="md"))


if __name__ == "__main__":
    main()
