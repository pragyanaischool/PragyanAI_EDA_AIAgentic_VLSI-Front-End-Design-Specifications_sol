import operator
from typing import Annotated, Dict, List, TypedDict, Union

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import all specialized chains from agents.py
from core.agents import (
    architect_chain, critic_chain, master_chain,
    rtl_chain, lint_chain, refiner_chain, tb_chain
)

# --- 1. FULL SHARED STATE ---
class AgentState(TypedDict):
    # Phase 1: Specification (RDS)
    user_input: str        # Initial hardware requirement
    rag_context: str       # Technical context from Knowledge Base
    draft: str             # The evolving RDS document
    critique: str          # RDS audit from Critic
    human_feedback: str    # Manual overrides from user
    revision_count: int    # Iteration tracker
    
    # Phase 2: RTL Generation
    language: str          # Target HDL (Verilog/VHDL) from Page 4
    generated_code: str    # Initial HDL draft
    code_audit: str        # Linting report from RTL Critic
    final_rtl: str         # Finalized refined RTL
    
    # Phase 3: Verification
    testbench_code: str    # NEW: Self-checking testbench for Page 5

# --- 2. RDS PHASE NODES ---

def architect_node(state: AgentState):
    """Generates the initial RDS draft based on user intent."""
    draft = architect_chain.invoke({
        "user_input": state["user_input"],
        "rag_context": state["rag_context"]
    })
    return {"draft": draft, "revision_count": state.get("revision_count", 0) + 1}

def critic_node(state: AgentState):
    """Audits the RDS draft for technical gaps."""
    critique = critic_chain.invoke({"draft": state["draft"]})
    return {"critique": critique}

def master_node(state: AgentState):
    """Synthesizes RDS inputs into the 'Golden' document."""
    final_rds = master_chain.invoke({
        "draft": state["draft"],
        "critique": state["critique"],
        "human_input": state.get("human_feedback", "Finalize based on audit.")
    })
    return {"draft": final_rds}

# --- 3. RTL PHASE NODES ---

def rtl_architect_node(state: AgentState):
    """Translates the RDS into HDL code (Verilog/VHDL)."""
    code = rtl_chain.invoke({
        "language": state.get("language", "Verilog"),
        "rds_content": state["draft"]
    })
    return {"generated_code": code}

def rtl_lint_node(state: AgentState):
    """Runs static analysis on the generated RTL."""
    audit = lint_chain.invoke({
        "language": state.get("language", "Verilog"),
        "code": state["generated_code"]
    })
    return {"code_audit": audit}

def rtl_refiner_node(state: AgentState):
    """Incorporates human feedback into the RTL code."""
    final_code = refiner_chain.invoke({
        "language": state.get("language", "Verilog"),
        "code": state["generated_code"],
        "critique": state["code_audit"],
        "feedback": state.get("human_feedback", "Optimize for synthesis.")
    })
    return {"final_rtl": final_code}

# --- 4. VERIFICATION PHASE NODE ---

def rtl_verification_node(state: AgentState):
    """Generates a self-checking testbench for the final RTL."""
    tb_output = tb_chain.invoke({
        "language": state.get("language", "Verilog"),
        "code": state.get("final_rtl", state.get("generated_code")),
        "rds_content": state["draft"]
    })
    return {"testbench_code": tb_output}

# --- 5. GRAPH ORCHESTRATION ---

workflow = StateGraph(AgentState)

# Define all nodes
workflow.add_node("architect", architect_node)
workflow.add_node("critic", critic_node)
workflow.add_node("master", master_node)
workflow.add_node("rtl_architect", rtl_architect_node)
workflow.add_node("rtl_lint", rtl_lint_node)
workflow.add_node("rtl_refiner", rtl_refiner_node)
workflow.add_node("rtl_verify", rtl_verification_node)

# --- 6. ROUTING LOGIC ---

workflow.set_entry_point("architect")
workflow.add_edge("architect", "critic")

def route_rds(state: AgentState):
    """Pauses for human feedback at Page 2 if needed."""
    if "CRITICAL MISSING" in state["critique"] or state["revision_count"] < 1:
        return "human_checkpoint"
    return "finalize_rds"

workflow.add_conditional_edges("critic", route_rds, {
    "human_checkpoint": END, 
    "finalize_rds": "master"
})

workflow.add_edge("master", "rtl_architect")
workflow.add_edge("rtl_architect", "rtl_lint")

def route_rtl(state: AgentState):
    """Pauses for human linting review at Page 4."""
    if "CRITICAL" in state.get("code_audit", ""):
        return "rtl_human_fix"
    return "rtl_finalize"

workflow.add_conditional_edges("rtl_lint", route_rtl, {
    "rtl_human_fix": END,
    "rtl_finalize": "rtl_refiner"
})

workflow.add_edge("rtl_refiner", "rtl_verify")
workflow.add_edge("rtl_verify", END)

# --- 7. PERSISTENCE ---
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)
