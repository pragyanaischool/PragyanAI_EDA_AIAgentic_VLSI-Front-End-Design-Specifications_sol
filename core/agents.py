import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables for GROQ_API_KEY
load_dotenv()

# --- Model Initializations (Specialized for Multi-Agent Roles) ---

# Architect: Uses Llama 3.3 70B for creative hardware design reasoning
architect_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.2, # Slight randomness for architectural trade-offs
    max_tokens=4096
)

# Critic: Uses Llama 3.1 70B for cold, deterministic technical auditing[cite: 1]
critic_llm = ChatGroq(
    model_name="openai/gpt-oss-120b", 
    temperature=0.0, # Zero temperature for strict instruction following[cite: 1]
    max_tokens=2048
)

# Master: Uses Llama 3.3 70B for high-quality document synthesis[cite: 1]
master_llm = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct", 
    temperature=0.1, 
    max_tokens=4096
)

# --- 1. ENHANCED ARCHITECT PROMPT ---[cite: 1]
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

architect_prompt = ChatPromptTemplate.from_messages([
    ("system", architect_system_prompt),
    ("user", "Design Requirement: {user_input}")
])

# --- 2. ENHANCED CRITIC PROMPT ---[cite: 1]
critic_system_prompt = """You are a Senior Design Verification (DV) Engineer. 
Actively search for "design killers" in the provided RDS. Focus your critique on:
- CDC Hazards: Are there unsynchronized signals crossing clock boundaries?
- Reset Integrity: Is the reset de-assertion strategy defined?
- Protocol Violations: Does it break AXI/APB/AHB standard handshakes (e.g., Ready/Valid dependencies)?
- Resource Efficiency: Are there unnecessary pipeline stalls or oversized buffers?

Format your response as a rigorous technical audit. If a section is missing, flag it as 'CRITICAL MISSING'."""

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", critic_system_prompt),
    ("user", "Audit this RDS Draft:\\n\\n{draft}")
])

# --- 3. ENHANCED MASTER PROMPT ---[cite: 1]
master_system_prompt = """You are the VLSI Specification Master. 
Your role is to produce the 'Golden' version of the RDS by merging the Architect's design with the Critic's Audit and Human Feedback.

GOALS:
- Fix every technical gap identified by the Critic.
- Implement every Human Override exactly as requested.
- Ensure 'Self-Consistency': If the human changes a port width, update the Register Map and Micro-Arch sections accordingly.
- Use professional IEEE/Standard formatting.

INPUT DATA:
Draft: {draft}
Audit: {critique}
Human Feedback: {human_input}"""

master_prompt = ChatPromptTemplate.from_messages([
    ("system", master_system_prompt),
    ("user", "Synthesize the Golden RDS.")
])

# --- LCEL CHAINS (The Newer Way) ---[cite: 1]
# Syntax: Prompt | Model | OutputParser[cite: 1]
architect_chain = architect_prompt | architect_llm | StrOutputParser()
critic_chain = critic_prompt | critic_llm | StrOutputParser()
master_chain = master_prompt | master_llm | StrOutputParser()

# --- HELPER FUNCTIONS FOR EXTERNAL ORCHESTRATION ---[cite: 1]
def generate_initial_spec(user_input, rag_context):
    \"\"\"Triggers the Architect and Critic agents in sequence.\"\"\"[cite: 1]
    draft = architect_chain.invoke({
        "user_input": user_input, 
        "rag_context": rag_context
    })
    
    critique = critic_chain.invoke({
        "draft": draft
    })
    
    return draft, critique

def finalize_spec(draft, critique, human_input):
    \"\"\"Triggers the Master agent to consolidate the final document.\"\"\"[cite: 1]
    return master_chain.invoke({
        "draft": draft,
        "critique": critique,
        "human_input": human_input
    })
    
