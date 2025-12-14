"""Streamlit UI for ReqGuard prototype."""

import streamlit as st
from main import run_analysis, approve_and_continue, reject_and_refine

st.set_page_config(
    page_title="ReqGuard - Requirements Validator",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 ReqGuard - Mortgage Requirements Validator")
st.markdown("*AI-powered requirements analysis with adversarial validation*")

# Session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Input section
st.header("📝 Submit Requirements")

requirements = st.text_area(
    "Paste your BRD, User Story, or Requirements Document",
    height=200,
    placeholder="Example: We need to build an FHA loan origination module..."
)

if st.button("🔍 Analyze Requirements", type="primary"):
    if requirements:
        with st.spinner("Running Author → Critic analysis..."):
            result = run_analysis(requirements)
            st.session_state.analysis_result = result
            st.session_state.thread_id = result["thread_id"]
    else:
        st.warning("Please enter requirements to analyze")

# Results section
if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    st.header("📊 Analysis Results")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        loan_type = result["loan_type"].get("primary_type", "Unknown")
        st.metric("Loan Type", loan_type)

    with col2:
        confidence = result["confidence"]
        st.metric("Confidence", f"{confidence:.0%}")

    with col3:
        outcome = result["outcome"]
        outcome_emoji = {"complete": "✅", "partial": "⚠️", "clarify": "❓"}.get(outcome, "❓")
        st.metric("Outcome", f"{outcome_emoji} {outcome.title()}")

    with col4:
        gap_count = len(result["gaps"])
        st.metric("Gaps Found", gap_count)

    # Outcome explanation
    if result["outcome"] == "complete":
        st.success("✅ Requirements are complete! Ready to forward to Architecture.")
    elif result["outcome"] == "partial":
        st.warning("⚠️ Requirements are partially complete. Review gaps before proceeding.")
    else:
        st.error("❓ Requirements need clarification. Please answer the questions below.")

    # Two columns for details
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🔍 Gaps Detected")
        if result["gaps"]:
            for gap in result["gaps"]:
                severity_color = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(gap["severity"], "⚪")

                with st.expander(f"{severity_color} {gap['description']}"):
                    st.write(f"**Category:** {gap['category']}")
                    st.write(f"**Severity:** {gap['severity']}")
                    st.write(f"**Question:** {gap['question']}")
        else:
            st.success("No gaps detected!")

    with right_col:
        st.subheader("❓ Questions for BSA")
        if result["questions"]:
            for i, q in enumerate(result["questions"], 1):
                severity_badge = {
                    "critical": "🔴 Critical",
                    "high": "🟠 High",
                    "medium": "🟡 Medium"
                }.get(q["severity"], "")

                st.markdown(f"**{i}. {q['question']}**")
                st.caption(f"{severity_badge} | Category: {q['category']}")
                st.divider()
        else:
            st.success("No clarifying questions needed!")

    # Structured requirements
    with st.expander("📄 Structured Requirements (Author Output)"):
        st.markdown(result["structured_requirements"])

    # Critic analysis
    with st.expander("🔎 Critic Analysis"):
        st.markdown(result["critique"])

    # Action buttons
    st.header("🎯 BSA Action")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("✅ Approve & Forward to Architecture", type="primary"):
            with st.spinner("Forwarding..."):
                approve_and_continue(st.session_state.thread_id)
            st.success("Forwarded to ArchGuard!")
            st.balloons()

    with action_col2:
        feedback = st.text_area("Provide feedback for refinement:")
        if st.button("🔄 Request Refinement"):
            if feedback:
                with st.spinner("Refining with feedback..."):
                    new_result = reject_and_refine(st.session_state.thread_id, feedback)
                    st.session_state.analysis_result = new_result
                st.rerun()
            else:
                st.warning("Please provide feedback for refinement")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About ReqGuard")
    st.markdown("""
    **ReqGuard** uses an adversarial AI pattern:

    1. **Author** extracts requirements
    2. **Critic** attacks and finds gaps
    3. **Gate** decides outcome
    4. **Human** makes final decision

    ---

    **Outcomes:**
    - ✅ **Complete** (≥95%): Auto-forward
    - ⚠️ **Partial** (70-94%): Continue with warning
    - ❓ **Clarify** (<70%): Human input needed

    ---

    **Confidence Calculation:**
    - Critical gap: -15%
    - High gap: -8%
    - Medium gap: -3%
    """)

    st.header("🔧 Settings")
    st.slider("Complete Threshold", 0.8, 1.0, 0.95)
    st.slider("Partial Threshold", 0.5, 0.9, 0.70)
