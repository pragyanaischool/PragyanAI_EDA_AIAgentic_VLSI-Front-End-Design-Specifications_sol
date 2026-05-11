import streamlit as st
import uuid
from core.graph import app_graph
from core.rag import get_context

st.set_page_config(page_title="Spec Designer", layout="wide")

if "thread_id" not in st.session_state: st.session_state.thread_id = str(uuid.uuid4())
if "graph_state" not in st.session_state: st.session_state.graph_state = None

st.title(" PragyanAI RTL Design Specification Generator")

if st.session_state.graph_state is None:
    user_intent = st.text_area("Describe your hardware problem statement:", height=150)
    if st.button(" Run Multi-Agent Pipeline"):
        context = get_context(user_intent)
        initial_input = {"user_input": user_intent, "rag_context": context, "revision_count": 0}
        
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        st.session_state.graph_state = app_graph.invoke(initial_input, config=config)
        st.rerun()
else:
    state = st.session_state.graph_state
    col1, col2 = st.columns(2)
    col1.markdown(state["draft"])
    col2.info(state["critique"])

    st.subheader("🙋 Human-in-the-Loop: Refine Details")
    q_logic = st.text_input("Refine Logic (e.g., reset polarity, FIFO thresholds):")
    
    if st.button("🛠️ Finalize & Download"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_state = app_graph.invoke({"human_feedback": q_logic}, config=config)
        st.session_state.final_rds = final_state["draft"]
        
        st.markdown(st.session_state.final_rds)
        st.download_button("📥 Download RDS (.md)", st.session_state.final_rds, "Master_RDS.md")
      
