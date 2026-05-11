import operator
from typing import Annotated, Dict, List, TypedDict, Union

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import specialized chains from agents.py
from core.agents import architect_chain, critic_chain, master_chain

# --- 1. DEFINE THE SHARED STATE ---
class AgentState(TypedDict):
    user_input: str        # Initial design requirement
    rag_context: str       # Technical context from local vector store
    draft: str             # Current version of the RTL Design Specification[cite: 1]
    critique: str          # Current technical audit/critique[cite: 1]
    human_feedback: str    # Overrides or questions from the user[cite: 1]
    revision_count: int    # Tracking iterations to prevent infinite loops[cite: 1]

# --- 2. DEFINE NODE FUNCTIONS ---[cite: 1]

def architect_node(state: AgentState):
    """Generates the initial RTL Design Specification draft."""[cite: 1]
    draft = architect_chain.invoke({
        "user_input": state["user_input"],
        "rag_context": state["rag_context"]
    })
    return {
        "draft": draft, 
        "revision_count": state.get("revision_count", 0) + 1
    }

def critic_node(state: AgentState):
    """Performs a rigorous technical audit on the current draft."""[cite: 1]
    critique = critic_chain.invoke({"draft": state["draft"]})
    return {"critique": critique}

def master_node(state: AgentState):
    """Finalizes the 'Golden RDS' by merging draft, audit, and human input."""[cite: 1]
    final_rds = master_chain.invoke({
        "draft": state["draft"],
        "critique": state["critique"],
        "human_input": state.get("human_feedback", "No specific overrides provided.")
    })
    return {"draft": final_rds}

# --- 3. DEFINE THE GRAPH LOGIC ---[cite: 1]

workflow = StateGraph(AgentState)

# Add functional nodes to the graph[cite: 1]
workflow.add_node("architect", architect_node)
workflow.add_node("critic", critic_node)
workflow.add_node("master", master_node)

# Define the entry point and linear edges[cite: 1]
workflow.set_entry_point("architect")
workflow.add_edge("architect", "critic")

# --- 4. DEFINE CONDITIONAL ROUTING ---[cite: 1]

def router(state: AgentState):
    """
    Determines if the flow should pause for Human-in-the-Loop 
    or proceed to the Master consolidation.[cite: 1]
    """
    # Route to Human if a 'Design Killer' is flagged or for the first review[cite: 1]
    if "CRITICAL MISSING" in state["critique"] or state["revision_count"] < 2:
        return "human_pause" 
    
    return "finalize"

workflow.add_conditional_edges(
    "critic",
    router,
    {
        "human_pause": END,   # Pauses execution and returns state to the UI[cite: 1]
        "finalize": "master"  # Proceeds to the Master Agent[cite: 1]
    }
)

# After the Master Agent runs, the workflow is complete[cite: 1]
workflow.add_edge("master", END)

# --- 5. COMPILE WITH PERSISTENCE ---[cite: 1]

# MemorySaver allows for 'checkpointing' so agents remember previous design iterations[cite: 1]
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)
