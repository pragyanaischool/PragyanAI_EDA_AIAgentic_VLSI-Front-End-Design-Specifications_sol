import streamlit as st

# --- 1. GLOBAL PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PragyanAI VLSI Master",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
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

# --- 2. LANDING PAGE CONTENT ---
st.image("PragyanAI_Transperent.png")
st.title("🛡️ PragyanAI: Multi-Agent VLSI Spec Engine")
st.subheader("Autonomous Hardware Specification Framework with RAG & HITL")

st.markdown("""
Welcome to **MAGE** (Multi-Agentic General Engine) tailored for VLSI Front-End Design. 
This platform automates the creation of high-fidelity **RTL Design Specifications (RDS)** by leveraging specialized AI agents and your local technical library[cite: 1].
""")

st.info("👈 **Select a page from the sidebar to begin your design journey.**")

# --- 3. ARCHITECTURE OVERVIEW ---[cite: 1]
st.divider()
st.header("⚡ The Agentic Workflow")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📚 1. Knowledge Base")
    st.write("""
    Upload your PDF standards (AXI, PCIe, etc.). 
    The **RAG Engine** indexes these locally using HuggingFace embeddings for precise grounding[cite: 1].
    """)

with col2:
    st.markdown("### 🏗️ 2. Spec Designer")
    st.write("""
    Enter a problem statement. The **Architect** drafts the spec, the **Critic** audits for CDC/Protocol errors, 
    and you provide **Human-in-the-Loop** refinements[cite: 1].
    """)

with col3:
    st.markdown("### 💬 3. Spec Chat")
    st.write("""
    Interact with your generated specification. Ask questions about design choices 
    or protocol nuances found in your uploaded documents[cite: 1].
    """)

# --- 4. QUICK START GUIDE ---[cite: 1]
st.divider()
with st.expander("🛠️ System Requirements & Setup"):
    st.markdown("""
    1. **API Keys**: Ensure your `.env` file contains a valid `GROQ_API_KEY`[cite: 1].
    2. **Local RAG**: Upload documents in the **Knowledge Base** page before starting a design[cite: 1].
    3. **Models**:
        * **Architect**: Llama-3.3-70b (Reasoning)[cite: 1]
        * **Critic**: Llama-3.1-70b (Deterministic Audit)[cite: 1]
        * **Master**: Llama-3.3-70b (Synthesis)[cite: 1]
    """)

st.caption("Developed for PragyanAI Educational Initiatives | MAGE Framework v2.0")
      
