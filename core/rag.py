import os
from typing import List
from dotenv import load_dotenv

# Core LangChain & Vector Store Imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# --- SAFE IMPORT FOR WEB SEARCH ---
# This prevents the app from crashing if the library isn't in requirements.txt
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    HAS_SEARCH_LIB = True
except ImportError:
    HAS_SEARCH_LIB = False

# Load environment variables
load_dotenv()

class VLSIRAGEngine:
    """
    Advanced Hybrid RAG Engine for VLSI Front-End Design.
    Combines local ChromaDB technical standards with real-time web search.
    """
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # 1. Initialize Local Embeddings
        # Uses CPU for compatibility with Streamlit Cloud environments
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}, 
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 2. Initialize Web Search Tool Safely
        self.web_search = None
        if HAS_SEARCH_LIB:
            try:
                self.web_search = DuckDuckGoSearchRun()
            except Exception as e:
                print(f"Web Search initialization failed: {e}")
        
        # 3. Initialize Local Vector Store reference
        self.vector_db = None
        if os.path.exists(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Retrieves context from local database AND performs a targeted web search if available.
        """
        context_parts = []

        # SECTION A: LOCAL VECTOR SEARCH
        if self.vector_db:
            try:
                docs = self.vector_db.similarity_search(query, k=k)
                for i, doc in enumerate(docs):
                    source = doc.metadata.get("source", "Local Spec")
                    page = doc.metadata.get("page", "N/A")
                    content = doc.page_content.strip().replace("\n", " ")
                    context_parts.append(f"[Local Segment {i+1}] (Source: {source}, Page: {page}): {content}")
            except Exception as e:
                context_parts.append(f"[System Error]: Local retrieval failed ({str(e)})")
        else:
            context_parts.append("[System Note]: Local Knowledge Base is empty. Please upload PDFs first.")

        # SECTION B: TARGETED WEB SEARCH
        if self.web_search:
            try:
                # Append domain-specific keywords to focus the web search on hardware protocols
                search_query = f"{query} VLSI hardware protocol specification"
                web_results = self.web_search.run(search_query)
                context_parts.append(f"\n[Web Research Results]: {web_results}")
            except Exception as e:
                context_parts.append(f"\n[Web Research]: Search currently unavailable.")
        elif not HAS_SEARCH_LIB:
            context_parts.append("\n[Web Research]: Disabled (duckduckgo-search not installed).")

        return "\n\n".join(context_parts)

    def get_retriever(self):
        """Returns a LangChain compatible retriever object for LCEL pipelines."""
        if not self.vector_db:
            raise FileNotFoundError("Vector DB not initialized. Please run ingestion first.")
        return self.vector_db.as_retriever(search_kwargs={"k": 4})

# --- GLOBAL INITIALIZATION ---#

@st.cache_resource
def get_rag_engine():
    """
    Initializes the RAG engine once and caches it.
    This prevents reloading the embedding model on every page rerun.
    """
    return VLSIRAGEngine()

def get_context(query: str) -> str:
    """
    Primary wrapper used by other pages to get technical context.
    """
    engine = get_rag_engine()
    return engine.retrieve_context(query)
