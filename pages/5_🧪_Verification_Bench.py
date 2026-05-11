import streamlit as st
from core.agents import tb_chain, explainer_chain

st.set_page_config(page_title="Verification Bench", page_icon="🧪", layout="wide")

st.image("PragyanAI_Transperent.png")
st.title(" PragyanAI Verification Bench")
st.caption("Generate Self-Checking Testbenches & Test Case Rationales")

# 1. Retrieve Data from previous steps
if "final_golden_rtl" not in st.session_state:
    st.warning("⚠️ No RTL Code found. Please generate or refine code on the 'RTL Generator' page first.")
    st.stop()

rtl_code = st.session_state.final_golden_rtl
rds_context = st.session_state.get("final_rds", "No RDS provided.")
hdl_lang = st.session_state.get("hdl_language", "Verilog") # Defaulting if not set

# 2. UI Layout
col_code, col_plan = st.columns([3, 2])

with col_code:
    st.subheader("Source RTL Code")
    st.code(rtl_code, language=hdl_lang.lower())

with col_plan:
    st.subheader("Verification Strategy")
    if st.button("🚀 Generate Testbench & Analysis"):
        with st.spinner("Synthesizing Testbench..."):
            # Run parallel chains
            st.session_state.testbench = tb_chain.invoke({
                "language": hdl_lang,
                "code": rtl_code,
                "rds_content": rds_context
            })
            st.session_state.explanation = explainer_chain.invoke({
                "language": hdl_lang,
                "code": rtl_code
            })

# 3. Display Results
if "testbench" in st.session_state:
    st.divider()
    
    # Explain the 'Why'
    st.subheader("🧐 Test Case Rationale")
    st.info(st.session_state.explanation)
    
    # The Code
    st.subheader(f"📑 Self-Checking {hdl_lang} Testbench")
    st.code(st.session_state.testbench, language=hdl_lang.lower())
    
    # Download
    ext = ".v" if hdl_lang == "Verilog" else ".vhd"
    st.download_button(
        label=f"📥 Download {hdl_lang} Testbench",
        data=st.session_state.testbench,
        file_name=f"tb_pragyan_design{ext}",
        mime="text/plain"
    )
  
