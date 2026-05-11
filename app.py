import streamlit as st
import uuid
from core.graph import app_graph
from core.rag import get_context

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MAGE VLSI Spec Engine", 
    page_icon="⚡", 
    layout="wide"
)

# Custom CSS for a professional engineering terminal feel
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stCodeBlock { border: 1px solid #ccd1d1; border-radius: 8px; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE INITIALIZATION ---
# thread_id is critical for LangGraph's MemorySaver to track design history
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph_state" not in st.session_state:
    st.session_state.graph_state = None

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🛡️ MAGE Control Center")
    st.info(f"**Session ID:** {st.session_state.thread_id}")
    if st.button("🗑️ Clear Session"):
        st.session_state.graph_state = None
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

st.title("⚡ MAGE: Multi-Agent VLSI Spec Engine")
st.caption("Autonomous RTL Design Specification (RDS) Generation with Human-in-the-Loop Verification")

# --- 4. STEP 1: INITIAL DESIGN ENTRY ---[cite: 1]
if st.session_state.graph_state is None:
    st.header("1. Define Module Requirements")
    user_intent = st.text_area(
        "Enter Design Specification (e.g., AXI4-Lite Slave for Internal SRAM Control):",
        height=150,
        placeholder="Describe protocols, clock domains, and FIFO depths..."
    )
    
    if st.button("🚀 Initiate Architect & Critic Agents"):
        if user_intent:
            with st.status("🔍 Retrieving VLSI Standards & Auditing...", expanded=True) as status:
                # Retrieve context from RAG[cite: 1]
                context = get_context(user_intent)
                
                # Initial State for LangGraph[cite: 1]
                initial_input = {
                    "user_input": user_intent,
                    "rag_context": context,
                    "revision_count": 0,
                    "human_feedback": ""
                }
                
                # Run graph until the 'human_pause' or 'END'[cite: 1]
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = app_graph.invoke(initial_input, config=config)
                
                st.session_state.graph_state = result
                status.update(label="Initial Audit Complete!", state="complete")
                st.rerun()
        else:
            st.error("Please provide design intent before starting.")

# --- 5. STEP 2: HUMAN-IN-THE-LOOP & REFINEMENT ---[cite: 1]
else:
    state = st.session_state.graph_state
    
    st.header("2. Technical Review & Human Intervention")
    
    col_draft, col_audit = st.columns(2)
    
    with col_draft:
        st.subheader("📑 Current RDS Draft")
        st.markdown(state.get("draft", "No draft generated."))
    
    with col_audit:
        st.subheader("🧐 Critic's Technical Audit")
        critique = state.get("critique", "No audit available.")
        if "CRITICAL MISSING" in critique:
            st.error(critique)
        else:
            st.warning(critique)

    st.divider()

    # Human interaction section for final overrides[cite: 1]
    st.subheader("🙋 Human-in-the-Loop Finalization")
    st.write("Address the Critic's concerns or add specific hardware overrides below:")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        q_ports = st.text_input("Review Port Mapping:", placeholder="e.g., Change data_in to 64-bit...")
    with col_q2:
        q_timing = st.text_input("Review Timing/CDC:", placeholder="e.g., Use active-high async reset...")

    if st.button("🛠️ Generate Final Golden RDS"):
        with st.spinner("Master Agent synthesizing final specification..."):
            feedback = f"Port Feedback: {q_ports}. Timing Feedback: {q_timing}"
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            # Resume graph by passing feedback to the Master Agent[cite: 1]
            final_state = app_graph.invoke(
                {"human_feedback": feedback}, 
                config=config
            )
            
            st.session_state.final_rds = final_state["draft"]
            st.session_state.step_complete = True
            st.success("Golden RDS Finalized Successfully!")
            
            st.markdown("---")
            st.subheader("🏆 Final Master Specification")
            st.markdown(st.session_state.final_rds)
            
            st.download_button(
                label="📥 Download Master RDS (.md)",
                data=st.session_state.final_rds,
                file_name="Master_VLSI_Spec.md",
                mime="text/markdown"
            )

    if st.button("🔄 Start New Design"):
        st.session_state.graph_state = None
        st.rerun()
      
