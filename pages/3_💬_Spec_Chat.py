import streamlit as st
from langchain_groq import ChatGroq
from core.rag import get_context

st.set_page_config(page_title="Spec Chat", layout="wide")
st.title("💬 VLSI Design Assistant")

if "chat_history" not in st.session_state: st.session_state.chat_history = []

# Chatbot initialization using Llama 3.3 70B
chat_llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.5)[cite: 1]

query = st.chat_input("Ask about the specification or protocols...")

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # RAG Context for chat
    context = get_context(query)[cite: 1]
    full_prompt = f"Context: {context}\n\nQuestion: {query}"
    
    response = chat_llm.invoke(full_prompt).content[cite: 1]
    st.session_state.chat_history.append({"role": "assistant", "content": response})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.write(msg["content"])
      
