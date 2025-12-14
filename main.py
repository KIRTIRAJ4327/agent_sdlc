"""LangGraph workflow for ReqGuard prototype."""

import os
import streamlit as st
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from agents import (
    ReqGuardAuthor,
    ReqGuardCritic,
    calculate_confidence,
    determine_outcome,
    generate_questions
)

load_dotenv()

# Helper to get API key from env or streamlit secrets
def get_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass
    return api_key

# State definition
class ReqGuardState(TypedDict):
    raw_requirements: str
    author_output: dict
    critic_output: dict
    confidence: float
    outcome: str  # complete, partial, clarify
    questions: list
    human_feedback: str
    iteration: int
    approved: bool

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", 
    temperature=0,
    google_api_key=get_api_key()
)
author = ReqGuardAuthor(llm)
critic = ReqGuardCritic(llm)

# Node functions
def author_node(state: ReqGuardState) -> dict:
    """Author extracts and structures requirements."""
    result = author.extract(state["raw_requirements"])
    return {"author_output": result}

def critic_node(state: ReqGuardState) -> dict:
    """Critic finds gaps and issues."""
    # Check against checklist
    gaps = critic.check_against_checklist(state["author_output"])

    # LLM critique
    critique = critic.critique(state["author_output"], gaps)

    # Calculate confidence
    confidence = calculate_confidence(gaps, critique["llm_critique"])
    outcome = determine_outcome(confidence)
    questions = generate_questions(gaps)

    return {
        "critic_output": critique,
        "confidence": confidence,
        "outcome": outcome,
        "questions": questions,
        "iteration": state.get("iteration", 0) + 1
    }

def gate_node(state: ReqGuardState) -> dict:
    """Gate decision based on outcome."""
    # This is where human review happens (via interrupt)
    return {}

def should_continue(state: ReqGuardState) -> str:
    """Determine next step based on outcome and iterations."""
    if state.get("approved", False):
        return "end"

    if state.get("iteration", 0) >= 3:
        return "escalate"

    outcome = state.get("outcome", "clarify")
    if outcome == "complete":
        return "end"
    elif outcome == "partial":
        return "gate"  # Continue but show warning
    else:
        return "gate"  # Need human input

# Build workflow
def create_reqguard_workflow():
    workflow = StateGraph(ReqGuardState)

    # Add nodes
    workflow.add_node("author", author_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("gate", gate_node)

    # Set entry point
    workflow.set_entry_point("author")

    # Add edges
    workflow.add_edge("author", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "gate": "gate",
            "end": END,
            "escalate": END  # In production, route to human escalation
        }
    )

    # Gate can loop back or end
    workflow.add_conditional_edges(
        "gate",
        lambda s: "end" if s.get("approved") else "author",
        {
            "author": "author",
            "end": END
        }
    )

    # Compile with memory and interrupt
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["gate"]  # Pause for human review
    )

# Create the app
app = create_reqguard_workflow()

def run_analysis(requirements: str) -> dict:
    """Run ReqGuard analysis on requirements."""
    thread_id = "demo-" + str(hash(requirements))[:8]

    result = app.invoke(
        {"raw_requirements": requirements, "iteration": 0},
        config={"configurable": {"thread_id": thread_id}}
    )

    return {
        "thread_id": thread_id,
        "loan_type": result.get("author_output", {}).get("loan_classification", {}),
        "confidence": result.get("confidence", 0),
        "outcome": result.get("outcome", "unknown"),
        "questions": result.get("questions", []),
        "gaps": result.get("critic_output", {}).get("checklist_gaps", []),
        "structured_requirements": result.get("author_output", {}).get("structured_requirements", ""),
        "critique": result.get("critic_output", {}).get("llm_critique", "")
    }

def approve_and_continue(thread_id: str, feedback: str = "") -> dict:
    """Approve at gate and continue."""
    result = app.invoke(
        {"approved": True, "human_feedback": feedback},
        config={"configurable": {"thread_id": thread_id}}
    )
    return result

def reject_and_refine(thread_id: str, feedback: str) -> dict:
    """Reject and send back for refinement with feedback."""
    # Append feedback to requirements
    state = app.get_state({"configurable": {"thread_id": thread_id}})
    updated_requirements = state.values.get("raw_requirements", "") + f"\n\nAdditional context: {feedback}"

    result = app.invoke(
        {"raw_requirements": updated_requirements, "approved": False},
        config={"configurable": {"thread_id": thread_id}}
    )
    return result


if __name__ == "__main__":
    # Quick test
    test_req = """
    We need to build an FHA loan origination module for first-time homebuyers.
    The system should support loans up to $500,000 with standard FHA guidelines.
    Integration with our existing LOS is required.
    """

    result = run_analysis(test_req)
    print(f"Loan Type: {result['loan_type']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Outcome: {result['outcome']}")
    print(f"Questions: {len(result['questions'])}")
    for q in result['questions']:
        print(f"  - [{q['severity']}] {q['question']}")
