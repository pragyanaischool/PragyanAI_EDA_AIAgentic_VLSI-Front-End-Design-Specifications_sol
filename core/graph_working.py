import operator
from typing import Annotated, Dict, List, TypedDict, Union

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import the specialized chains and models from agents.py
from core.agents import architect_chain, critic_chain, master_chain

# --- 1. DEFINE THE SHARED STATE ---
# This dictionary is passed between nodes and updated by each agent.
class AgentState(TypedDict):
    user_input: str        # Initial hardware requirement from the user
    rag_context: str       # Technical context retrieved from the Knowledge Base
    draft: str             # The evolving RTL Design Specification (RDS)
    critique: str          # Technical audit provided by the Critic agent
    human_feedback: str    # Manual overrides or clarifications from the user
    revision_count: int    # Tracking iterations to ensure the flow remains efficient

# --- 2. NODE FUNCTIONS ---
# Each function represents a specialized agent in the VLSI pipeline.

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
    """Synthesizes all inputs into the final 'Golden' RDS."""
    final_rds = master_chain.invoke({
        "draft": state["draft"],
        "critique": state["critique"],
        "human_input": state.get("human_feedback", "No manual overrides provided.")
    })
    return {"draft": final_rds}

# --- 3. GRAPH ORCHESTRATION ---

workflow = StateGraph(AgentState)

# Add functional nodes to the state machine
workflow.add_node("architect", architect_node)
workflow.add_node("critic", critic_node)
workflow.add_node("master", master_node)

# Define the sequence: Start with Architect, then pass to Critic
workflow.set_entry_point("architect")
workflow.add_edge("architect", "critic")

# --- 4. CONDITIONAL ROUTING (Logic Control) ---

def should_finalize(state: AgentState):
    """
    Determines if the specification is ready for consolidation 
    or requires human intervention.
    """
    # Force human intervention if the Critic identifies major flaws
    # or if this is the first iteration of the design.
    if "CRITICAL MISSING" in state["critique"] or state["revision_count"] < 2:
        return "human_checkpoint"
    
    return "finalize"

workflow.add_conditional_edges(
    "critic",
    should_finalize,
    {
        "human_checkpoint": END,  # Pauses execution to wait for user input in Streamlit
        "finalize": "master"      # Proceeds to the Master consolidation agent
    }
)

# After the Master Agent finalizes the document, the flow terminates.
workflow.add_edge("master", END)

# --- 5. COMPILATION WITH PERSISTENCE ---
# MemorySaver allows for 'checkpointing' so you can leave the page 
# and return without losing the agent's progress or the design history.
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)

