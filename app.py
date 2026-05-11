import streamlit as st
import os
from core.graph import get_graph_image # Import the visualization helper
# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PragyanAI: Multi-Agent VLSI Suite",
    page_icon="🛡️",
    layout="wide"
)
# Professional Engineering UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e3b4e; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL SESSION STATE INITIALIZATION ---
# This ensures that data persists as the user moves between pages
if "final_rds" not in st.session_state:
    st.session_state.final_rds = None
if "final_golden_rtl" not in st.session_state:
    st.session_state.final_golden_rtl = None
if "hdl_language" not in st.session_state:
    st.session_state.hdl_language = "Verilog"
if "testbench_code" not in st.session_state:
    st.session_state.testbench_code = None

# --- 3. UI: HERO SECTION ---
st.image("PragyanAI_Transperent.png")
st.title("🛡️ PragyanAI: Multi-Agent VLSI Design Suite")

st.subheader("Autonomous Chip Design Framework with RAG, RTL Gen & HITL")

st.markdown("""
Welcome to **MAGE** (Multi-Agentic General Engine) tailored for VLSI Front-End Design. 
This platform automates the entire lifecycle—from **RTL Design Specifications (RDS)** to 
**Synthesizable Code** and **Self-Checking Testbenches**—by leveraging specialized AI agents 
and your local technical library.
""")

st.info("👈 **Select a page from the sidebar to begin your design journey.**")

# Define the image path
logo_path = "PragyanAI_Transperent.png"

# Only show the image if the file actually exists
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.warning("Logo file missing")
    
st.divider()

# --- 4. THE AGENTIC WORKFLOW DESCRIPTION ---
st.header("⚡ The Full Agentic Workflow")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1. Knowledge Base
    Upload your PDF standards (AXI, PCIe, RISC-V, etc.). The **RAG Engine** indexes these locally using 
    HuggingFace embeddings for precise technical grounding.

    ### 2. Spec Designer
    Enter a problem statement. The **Architect** drafts the RDS, the **Critic** audits for CDC/Protocol errors, 
    and you provide **Human-in-the-Loop** refinements to create the "Golden Spec".

    ### 3. Spec Chat
    Interact with your generated specification. Ask questions about design choices or protocol nuances 
    found in your uploaded documents.
    """)

with col2:
    st.markdown("""
    ### 4. RTL Generator
    Translate your RDS into production-ready **Verilog** or **VHDL**. Includes an automated **Linting Agent** to catch "design killer" bugs like unintentional latches.

    ### 5. Verification Bench
    Generate a **Self-Checking Testbench**. This phase includes a **DV Lead Agent** that explains the 
    rationale behind every test case (Corner cases, Reset, and Stress tests).
    """)

with col3:
    # Display the Graph Visualization
    with st.expander("🔍 View MAGE Architecture Logic", expanded=True):
        graph_img = get_graph_image()
        if graph_img:
            st.image(graph_img, caption="PragyanAI MAGE: Multi-Agent Directed Acyclic Graph (DAG)")
        else:
            st.info("Graph visualization is currently being synthesized...")

    st.markdown("""
    The diagram above represents the **MAGE** state machine. Each node is a specialized agent 
    (Architect, Critic, Master, RTL, Verify) that passes design tokens through a centralized 
    shared state, stopping only at **Human-in-the-Loop** checkpoints.
    """)

st.divider()


# --- 5. SYSTEM STATUS & FOOTER ---
st.subheader("System Status")
st.success("✅ PragyanAI MAGE Framework v3.0 Core Online")
st.caption("Developed for PragyanAI Educational Initiatives | Bridging the gap between academic theory and industry-standard engineering.")


