import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. SECURE KEY MANAGEMENT ---
# Fetching from Streamlit Secrets (for local: .streamlit/secrets.toml)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- 2. MODEL INITIALIZATIONS ---

# Architect: Lead reasoning for RTL Design
architect_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    api_key=GROQ_API_KEY,
    temperature=0.2,
    max_tokens=4096
)

# Critic: Specialized deterministic auditor
critic_llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    api_key=GROQ_API_KEY,
    temperature=0.0,
    max_tokens=2048
)

# Master: Final high-quality document synthesis
master_llm = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct", 
    api_key=GROQ_API_KEY,
    temperature=0.1,
    max_tokens=4096
)

# --- 3. SYSTEM PROMPTS ---

architect_system_prompt = """You are a Principal VLSI Architect. Generate an implementation-ready RTL Design Specification (RDS).
Your design must be synthesizable and follow synchronous design principles.

CONTEXT FROM STANDARDS:
{rag_context}

DOCUMENT STRUCTURE REQUIREMENTS:
1. Functional Overview: Purpose and SoC integration context.
2. Interface Control Document (ICD): Strict Markdown table [Name, Dir, Width, Desc, Protocol].
3. Clock & Reset: Specify domains, CDC strategy (e.g., 2-FF sync), and reset polarity.
4. Micro-Architecture: Data-path pipeline stages, FIFO depths/watermarks, and FSM descriptions.
5. Register Map: Absolute address offsets and bit-field access types (RW, RO, W1C).
6. Performance: Throughput targets and cycle-count latency.
7. Verification Plan: Specific corner cases for this module."""

critic_system_prompt = """You are a Senior Design Verification (DV) Engineer. 
Actively search for "design killers" in the provided RDS. Focus your critique on:
- CDC Hazards: Are there unsynchronized signals crossing clock boundaries?
- Reset Integrity: Is the reset de-assertion strategy defined?
- Protocol Violations: Does it break AXI/APB/AHB handshakes (e.g., Ready/Valid dependencies)?
- Resource Efficiency: Are there unnecessary pipeline stalls or oversized buffers?

Format your response as a rigorous technical audit. If a section is missing, flag it as 'CRITICAL MISSING'."""

master_system_prompt = """You are the VLSI Specification Master. 
Your role is to produce the 'Golden' version of the RDS by merging the Architect's design with the Critic's Audit and Human Feedback.

GOALS:
- Fix every technical gap identified by the Critic.
- Implement every Human Override exactly as requested.
- Ensure 'Self-Consistency' across all sections (Ports, Reg Map, Logic).
- Use professional IEEE/Standard formatting."""

# --- 4. LCEL CHAINS ---

architect_prompt = ChatPromptTemplate.from_messages([
    ("system", architect_system_prompt),
    ("user", "Design Requirement: {user_input}")
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", critic_system_prompt),
    ("user", "Audit this RDS Draft:\n\n{draft}")
])

master_prompt = ChatPromptTemplate.from_messages([
    ("system", master_system_prompt),
    ("user", "ARCHITECT DRAFT: {draft}\n\nCRITIC AUDIT: {critique}\n\nHUMAN OVERRIDES: {human_input}")
])

architect_chain = architect_prompt | architect_llm | StrOutputParser()
critic_chain = critic_prompt | critic_llm | StrOutputParser()
master_chain = master_prompt | master_llm | StrOutputParser()

# --- 5. HELPER FUNCTIONS ---

def generate_initial_spec(user_input, rag_context):
    """Triggers the Architect and Critic agents in sequence."""
    draft = architect_chain.invoke({
        "user_input": user_input, 
        "rag_context": rag_context
    })
    critique = critic_chain.invoke({"draft": draft})
    return draft, critique

def finalize_spec(draft, critique, human_input):
    """Triggers the Master agent to consolidate the final document."""
    return master_chain.invoke({
        "draft": draft,
        "critique": critique,
        "human_input": human_input
    })
    
# --- 6. ADDITIONAL MODELS FOR RTL GENERATION ---
# Using Mixtral and Llama 3.1 for diverse architectural perspectives

# RTL Architect: Uses Mixtral for high-throughput code structure
rtl_architect_llm = ChatGroq(
    model_name="mixtral-8x7b-32768",
    api_key=GROQ_API_KEY,
    temperature=0.1,
    max_tokens=8192
)

# RTL Critic: Uses Llama 3.1 70B for rigorous logic auditing
rtl_critic_llm = ChatGroq(
    model_name="llama-3.1-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.0,
    max_tokens=4096
)

# RTL Refiner: Uses Llama 3.3 70B for final synthesis and cleanup
rtl_refiner_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.1,
    max_tokens=8192
)

# --- 7. RTL SYSTEM PROMPTS ---

rtl_architect_system_prompt = """You are a Lead RTL Engineer. Generate synthesizable {language} code.
Strictly adhere to the provided RTL Design Specification (RDS).

REQUIREMENTS:
- Match all port names, widths, and types from the ICD section.
- Implement the micro-architecture pipeline stages exactly.
- Use the specified reset polarity and clocking strategy.
- Provide clear comments for each logic block."""

rtl_critic_system_prompt = """You are a Senior Design Verification Engineer. 
Audit the following {language} code for hardware "design killers":
- Combinational loops or unintentional latches.
- Incorrect blocking (=) vs non-blocking (<=) assignments.
- Missing signals in sensitivity lists.
- Clock domain crossing (CDC) hazards.

Flag errors as 'CRITICAL' if they prevent hardware synthesis or cause simulation mismatches."""

rtl_refiner_system_prompt = """You are the RTL Synthesis Master. 
Consolidate the original {language} code, the Critic's linting report, and Human feedback.
Deliver the final 'Golden RTL' that is optimized, bug-free, and fully synthesizable."""

# --- 8. RTL LCEL CHAINS ---

rtl_architect_prompt = ChatPromptTemplate.from_messages([
    ("system", rtl_architect_system_prompt),
    ("user", "Target Language: {language}\n\nRDS Document:\n{rds_content}")
])

rtl_critic_prompt = ChatPromptTemplate.from_messages([
    ("system", rtl_critic_system_prompt),
    ("user", "Review this {language} code:\n\n{code}")
])

rtl_refiner_prompt = ChatPromptTemplate.from_messages([
    ("system", rtl_refiner_system_prompt),
    ("user", "Original Code: {code}\nLint Report: {critique}\nHuman Feedback: {feedback}\nLanguage: {language}")
])

rtl_chain = rtl_architect_prompt | rtl_architect_llm | StrOutputParser()
lint_chain = rtl_critic_prompt | rtl_critic_llm | StrOutputParser()
refiner_chain = rtl_refiner_prompt | rtl_refiner_llm | StrOutputParser()

# --- 9. RTL HELPER FUNCTIONS ---

def generate_rtl_code(language, rds_content):
    """Generates the first draft of HDL code and an immediate audit."""
    code = rtl_chain.invoke({"language": language, "rds_content": rds_content})
    critique = lint_chain.invoke({"language": language, "code": code})
    return code, critique

def refine_rtl_code(language, code, critique, feedback):
    """Synthesizes the final HDL code based on all inputs."""
    return refiner_chain.invoke({
        "language": language,
        "code": code,
        "critique": critique,
        "feedback": feedback
    })
    
