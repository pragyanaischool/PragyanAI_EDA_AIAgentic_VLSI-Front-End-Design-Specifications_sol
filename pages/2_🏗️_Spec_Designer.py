import streamlit as st
import uuid
from core.graph import app_graph
from core.rag import get_context

st.set_page_config(page_title="Spec Designer", layout="wide")
st.image("PragyanAI_Transperent.png")
st.title(" PragyanAI RTL Design Specification Generator")

# 1. SESSION STATE SETUP
if "thread_id" not in st.session_state: 
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_state" not in st.session_state: 
    st.session_state.graph_state = None
if "final_rds" not in st.session_state:
    st.session_state.final_rds = None

# 2. INPUT PHASE: ARCHITECT & CRITIC
if st.session_state.graph_state is None:
    user_intent = st.text_area("Describe your hardware problem statement:", 
                               placeholder="e.g., A 32-bit pipelined multiplier with AXI-Lite interface...",
                               height=150)
    
    if st.button("🚀 Run Multi-Agent Pipeline"):
        if not user_intent.strip():
            st.warning("Please enter a hardware requirement.")
        else:
            with st.spinner("Searching Knowledge Base & Generating Design..."):
                # Use the cached RAG engine from core.rag
                context = get_context(user_intent)
                
                initial_input = {
                    "user_input": user_intent, 
                    "rag_context": context, 
                    "revision_count": 0
                }
                
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                # The graph runs Architect -> Critic and then pauses (END)
                st.session_state.graph_state = app_graph.invoke(initial_input, config=config)
                st.rerun()

# 3. REVIEW PHASE: HUMAN-IN-THE-LOOP
else:
    state = st.session_state.graph_state
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🏗️ Architect's Draft")
        st.markdown(state.get("draft", "No draft generated."))
    
    with col2:
        st.subheader("🧐 Critic's Audit")
        critique = state.get("critique", "No critique available.")
        if "CRITICAL" in critique:
            st.error(critique)
        else:
            st.info(critique)

    st.divider()
    
    # 4. FINALIZATION PHASE: MASTER AGENT
    st.subheader("🙋 Human-in-the-Loop: Refine Details")
    q_logic = st.text_input("Manual Overrides (e.g., 'Change reset to active-high', 'Add a 16-deep FIFO'):")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🪄 Finalize Golden RDS"):
            with st.spinner("Synthesizing Golden Specification..."):
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                # Resumes graph from checkpoint and runs the 'master_node'
                # This combines Draft + Critique + Your Feedback
                updated_state = app_graph.invoke(
                    {"human_feedback": q_logic}, 
                    config=config
                )
                
                st.session_state.graph_state = updated_state
                st.session_state.final_rds = updated_state["draft"]
                st.success("Golden RDS Finalized! You can now generate RTL Code on Page 4.")

    with col_btn2:
        if st.session_state.final_rds:
            st.download_button(
                label="📥 Download RDS (.md)",
                data=st.session_state.final_rds,
                file_name="Master_RDS.md",
                mime="text/markdown"
            )

    if st.button("🔄 Start New Design"):
        st.session_state.graph_state = None
        st.session_state.final_rds = None
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
