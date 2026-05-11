import operator
from typing import Annotated, Dict, List, TypedDict, Union

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import all specialized chains from agents.py
from core.agents import (
    architect_chain, critic_chain, master_chain,
    rtl_chain, lint_chain, refiner_chain
)

# --- 1. ENHANCED SHARED STATE ---
class AgentState(TypedDict):
    # Specification Phase Fields
    user_input: str        # Initial requirement
    rag_context: str       # Knowledge Base context
    draft: str             # The evolving RDS
    critique: str          # RDS audit from Critic
    human_feedback: str    # Feedback for RDS or RTL code
    revision_count: int    # Iteration tracker
    
    # RTL Generation Phase Fields
    language: str          # Target HDL (Verilog/VHDL)
    generated_code: str    # Initial HDL draft
    code_audit: str        # Linting report from RTL Critic
    final_rtl: str         # Finalized synthesizable code

# --- 2. SPECIFICATION NODE FUNCTIONS (RDS PHASE) ---

def architect_node(state: AgentState):
    """Generates the initial technical draft or updates it based on state."""
    draft = architect_chain.invoke({
        "user_input": state["user_input"],
        "rag_context": state["rag_context"]
    })
    return {
        "draft": draft, 
        "revision_count": state.get("revision_count", 0) + 1
    }

def critic_node(state: AgentState):
    """Performs a rigorous DV-style audit of the current draft."""
    critique = critic_chain.invoke({"draft": state["draft"]})
    return {"critique": critique}

def master_node(state: AgentState):
    """Synthesizes RDS inputs into the final 'Golden' RDS."""
    final_rds = master_chain.invoke({
        "draft": state["draft"],
        "critique": state["critique"],
        "human_input": state.get("human_feedback", "Finalize based on design audit.")
    })
    return {"draft": final_rds}

# --- 3. RTL GENERATION NODE FUNCTIONS (HDL PHASE) ---

def rtl_architect_node(state: AgentState):
    """Translates the RDS into synthesizable Verilog or VHDL code."""
    code = rtl_chain.invoke({
        "language": state.get("language", "Verilog"),
        "rds_content": state["draft"]
    })
    return {"generated_code": code}

def rtl_lint_node(state: AgentState):
    """Performs static analysis (linting) on the generated RTL code."""
    audit = lint_chain.invoke({
        "language": state.get("language", "Verilog"),
        "code": state["generated_code"]
    })
    return {"code_audit": audit}

def rtl_refiner_node(state: AgentState):
    """Refines code based on human suggestions and lint reports."""
    final_code = refiner_chain.invoke({
        "language": state.get("language", "Verilog"),
        "code": state["generated_code"],
        "critique": state["code_audit"],
        "feedback": state.get("human_feedback", "Optimize for synthesis.")
    })
    return {"final_rtl": final_code}

# --- 4. GRAPH ORCHESTRATION ---

workflow = StateGraph(AgentState)

# Add all nodes to the state machine
workflow.add_node("architect", architect_node)
workflow.add_node("critic", critic_node)
workflow.add_node("master", master_node)
workflow.add_node("rtl_architect", rtl_architect_node)
workflow.add_node("rtl_lint", rtl_lint_node)
workflow.add_node("rtl_refiner", rtl_refiner_node)

# --- 5. LOGIC CONTROL & ROUTING ---

# Start Phase: RDS Generation
workflow.set_entry_point("architect")
workflow.add_edge("architect", "critic")

def route_rds(state: AgentState):
    """Decides if RDS is ready for RTL generation or needs human review."""
    if "CRITICAL MISSING" in state["critique"] or state["revision_count"] < 1:
        return "human_checkpoint"
    return "generate_code"

workflow.add_conditional_edges(
    "critic",
    route_rds,
    {
        "human_checkpoint": END,  # Pauses for Page 2 feedback
        "generate_code": "master" 
    }
)

# Transition: RDS to RTL
workflow.add_edge("master", "rtl_architect")
workflow.add_edge("rtl_architect", "rtl_lint")

def route_rtl(state: AgentState):
    """Decides if RTL code needs human intervention based on Lint audit."""
    if "CRITICAL" in state.get("code_audit", ""):
        return "rtl_human_fix"
    return "rtl_finalize"

workflow.add_conditional_edges(
    "rtl_lint",
    route_rtl,
    {
        "rtl_human_fix": END,      # Pauses for Page 4 feedback
        "rtl_finalize": "rtl_refiner"
    }
)

# Finalization
workflow.add_edge("rtl_refiner", END)

# --- 6. COMPILATION ---
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)
