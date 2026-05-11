import streamlit as st
import os
from core.agents import rtl_chain, lint_chain, refiner_chain

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PragyanAI RTL Code Generator",
    page_icon="🛠️",
    layout="wide"
)
st.image("PragyanAI_Transperent.png")
st.title(" PragyanAI RTL Code Generator")
st.caption("Generate Synthesizable Verilog/VHDL from RTL Design Specifications (RDS)")

# --- 2. SESSION STATE INITIALIZATION ---
if "current_rtl" not in st.session_state:
    st.session_state.current_rtl = None
if "rtl_audit" not in st.session_state:
    st.session_state.rtl_audit = None
if "final_golden_rtl" not in st.session_state:
    st.session_state.final_golden_rtl = None

# --- 3. INPUT SECTION (Settings & File Upload) ---
with st.container():
    col_settings, col_input = st.columns([1, 3])
    
    with col_settings:
        st.subheader("Settings")
        hdl_language = st.radio(
            "Target Language:",
            ["Verilog", "VHDL"],
            help="Select the hardware description language for generation."
        )
        
        st.divider()
        st.info("💡 **Tip:** Ensure your RDS includes a clear Port List and Clock/Reset strategy for best results.")

    with col_input:
        st.subheader("Source Specification (RDS)")
        
        # New Feature: .MD File Upload
        uploaded_file = st.file_uploader("Upload RDS Specification (.md)", type=["md"])
        
        # Logic to handle either Upload or Paste
        if uploaded_file is not None:
            # Read content from uploaded file
            rds_content = uploaded_file.getvalue().decode("utf-8")
            st.success(f"Loaded: {uploaded_file.name}")
        else:
            # Fallback to manual paste or session state from Spec Designer
            default_rds = st.session_state.get("final_rds", "")
            rds_content = st.text_area(
                "Paste RDS Content Here:",
                value=default_rds,
                height=250,
                placeholder="Paste the markdown specification here..."
            )

# --- 4. GENERATION PIPELINE ---
if st.button("🚀 Generate RTL Code"):
    if not rds_content.strip():
        st.error("Please provide an RDS document by uploading a file or pasting text.")
    else:
        with st.status("🛠️ Architecting RTL...", expanded=True) as status:
            # Step A: Architect Agent Generates Code
            st.write("Agent 1: Architecting logic structure...")
            initial_code = rtl_chain.invoke({
                "language": hdl_language, 
                "rds_content": rds_content
            })
            st.session_state.current_rtl = initial_code
            
            # Step B: Critic Agent Audits Code
            st.write("Agent 2: Running static analysis (Linting)...")
            audit_report = lint_chain.invoke({
                "language": hdl_language, 
                "code": initial_code
            })
            st.session_state.rtl_audit = audit_report
            
            status.update(label="RTL Generation & Audit Complete!", state="complete")
            st.rerun()

# --- 5. REVIEW & REFINEMENT SECTION ---
if st.session_state.current_rtl:
    st.divider()
    
    view_col, audit_col = st.columns(2)
    
    with view_col:
        st.subheader(f"📑 Generated {hdl_language}")
        st.code(st.session_state.current_rtl, language=hdl_language.lower())
        
    with audit_col:
        st.subheader("🧐 Design Audit Report")
        if "CRITICAL" in st.session_state.rtl_audit:
            st.error(st.session_state.rtl_audit)
        else:
            st.info(st.session_state.rtl_audit)

    # Human-in-the-Loop Refinement
    st.divider()
    st.subheader("🙋 Human-in-the-Loop Refinement")
    st.write("Address audit concerns or request architectural changes:")
    
    human_refinement = st.text_input("Enter suggestions (e.g., 'Use a behavioral 32-bit adder instead'):")
    
    if st.button("🪄 Apply Refinements & Finalize"):
        with st.spinner("Refining code with Master Agent..."):
            final_code = refiner_chain.invoke({
                "language": hdl_language,
                "code": st.session_state.current_rtl,
                "critique": st.session_state.rtl_audit,
                "feedback": human_refinement if human_refinement else "Finalize code."
            })
            st.session_state.final_golden_rtl = final_code
            st.success("Golden RTL Generated!")

# --- 6. FINAL OUTPUT & DOWNLOAD ---
if st.session_state.final_golden_rtl:
    st.divider()
    st.subheader("🏆 Golden RTL Code")
    st.code(st.session_state.final_golden_rtl, language=hdl_language.lower())
    
    ext = ".v" if hdl_language == "Verilog" else ".vhd"
    st.download_button(
        label=f"📥 Download {hdl_language} Source",
        data=st.session_state.final_golden_rtl,
        file_name=f"pragyan_design_final{ext}",
        mime="text/plain"
    )

    if st.button("🔄 Start New Design"):
        st.session_state.current_rtl = None
        st.session_state.rtl_audit = None
        st.session_state.final_golden_rtl = None
        st.rerun()
