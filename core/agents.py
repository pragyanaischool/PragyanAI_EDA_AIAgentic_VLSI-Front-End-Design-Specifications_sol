import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables for GROQ_API_KEY
load_dotenv()

# Initialize the Groq Llama 3 70B model
# High temperature is avoided (0.1) to ensure technical precision for VLSI specs
llm = ChatGroq(
    model_name="llama3-70b-8192", 
    temperature=0.1,
    max_tokens=4096
)

# --- 1. ARCHITECT AGENT ---
# Responsible for the initial draft based on RAG context
architect_system_prompt = """You are a Lead VLSI Front-End Architect. 
Your task is to generate a detailed RTL Design Specification (RDS).
Use the provided RAG context to ensure protocol compliance (AXI, AHB, etc.).

Strictly include these sections:
1. Functional Overview
2. Interface Control Document (Port Table: Name, Dir, Width, Description)
3. Clock, Reset, and Power (CRP) Scheme
4. Micro-Architecture (Pipeline stages, FIFO depths, logic flow)
5. Register Map (Address offsets and bit-field definitions)
6. Timing & Performance (Target latency/throughput)
7. Verification Scenarios

Context: {rag_context}"""

architect_prompt = ChatPromptTemplate.from_messages([
    ("system", architect_system_prompt),
    ("user", "Design Intent: {user_input}")
])

# --- 2. SPECIFICATION CRITIC AGENT ---
# Responsible for finding technical gaps and CDC issues
critic_system_prompt = """You are a Principal Design Verification (DV) Engineer. 
Analyze the provided RDS for technical flaws. Look specifically for:
- Missing reset states or asynchronous reset issues.
- Clock Domain Crossing (CDC) ambiguities.
- FIFO overflow/underflow handling.
- Protocol violations based on industry standards.

Provide a concise, numbered list of critical gaps."""

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", critic_system_prompt),
    ("user", "Draft Specification for Review:\n\n{draft}")
])

# --- 3. MASTER SPECIFICATION AGENT ---
# The final consolidator that merges draft, critique, and human feedback
master_system_prompt = """You are the VLSI Specification Master. 
Your goal is to synthesize the initial draft, the critic's feedback, and the human operator's instructions into a single, authoritative RTL Design Specification (RDS).

Instructions:
- Resolve all technical gaps identified by the critic.
- Prioritize Human Feedback above all else.
- Ensure all tables (Ports, Registers) are perfectly formatted in Markdown.
- Maintain a professional, implementation-ready engineering tone."""

master_prompt = ChatPromptTemplate.from_messages([
    ("system", master_system_prompt),
    ("user", "ARCHITECT DRAFT: {draft}\n\nCRITIC FEEDBACK: {critique}\n\nHUMAN OVERRIDES: {human_input}")
])

# --- LCEL CHAINS (The Newer Way) ---
# Syntax: Prompt | Model | OutputParser
architect_chain = architect_prompt | llm | StrOutputParser()
critic_chain = critic_prompt | llm | StrOutputParser()
master_chain = master_prompt | llm | StrOutputParser()

# --- HELPER FUNCTIONS FOR STREAMLIT ---
def generate_initial_spec(user_input, rag_context):
    """Triggers the Architect and Critic agents in sequence."""
    draft = architect_chain.invoke({
        "user_input": user_input, 
        "rag_context": rag_context
    })
    
    critique = critic_chain.invoke({
        "draft": draft
    })
    
    return draft, critique

def finalize_spec(draft, critique, human_input):
    """Triggers the Master agent to consolidate the final document."""
    return master_chain.invoke({
        "draft": draft,
        "critique": critique,
        "human_input": human_input
    })
