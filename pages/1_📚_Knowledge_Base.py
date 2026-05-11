import streamlit as st
import os
import subprocess

st.set_page_config(page_title="Knowledge Base", layout="wide")
st.title("📚 VLSI Knowledge Base Manager")

uploaded_files = st.file_uploader("Upload VLSI Standards (PDF)", type="pdf", accept_multiple_files=True)[cite: 1]

if st.button("📁 Process & Index Documents"):
    if uploaded_files:
        if not os.path.exists("./data"): os.makedirs("./data")[cite: 1]
        
        new_files = 0
        for uploaded_file in uploaded_files:
            file_path = os.path.join("./data", uploaded_file.name)
            if not os.path.exists(file_path):[cite: 1]
                with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                new_files += 1
        
        if new_files > 0:
            with st.spinner(f"Indexing {new_files} new files..."):
                subprocess.run(["python", "ingest_all.py"], check=True)[cite: 1]
                st.success("Knowledge base updated!")
        else:
            st.info("All files are already indexed.")[cite: 1]
          
