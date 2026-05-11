import os
from typing import List
from dotenv import load_dotenv

# Core LangChain & Vector Store Imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Web Search Integration (Requires 'pip install duckduckgo-search')
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables for any external keys
load_dotenv()

class VLSIRAGEngine:
    """
    Advanced Hybrid RAG Engine for VLSI Front-End Design.
    Combines local ChromaDB technical standards with real-time web search.
    """
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # Initialize Local Embeddings (Same as ingest_all.py for consistency)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}, 
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Web Search Tool
        self.web_search = DuckDuckGoSearchRun()
        
        # Initialize Vector Store reference
        self.vector_db = None
        if os.path.exists(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Retrieves context from local database AND performs a targeted web search.
        """
        context_parts = []

        # 1. LOCAL VECTOR SEARCH
        if self.vector_db:
            docs = self.vector_db.similarity_search(query, k=k)
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source", "Local Spec")
                page = doc.metadata.get("page", "N/A")
                content = doc.page_content.strip().replace("\n", " ")
                context_parts.append(f"[Local Segment {i+1}] (Source: {source}, Page: {page}): {content}")
        else:
            context_parts.append("[System Note]: Local Knowledge Base is currently empty.")

        # 2. TARGETED WEB SEARCH
        # We append 'VLSI hardware specification' to refine the search results
        try:
            web_results = self.web_search.run(f"{query} VLSI hardware protocol specification")
            context_parts.append(f"\n[Web Research Results]: {web_results}")
        except Exception as e:
            context_parts.append(f"\n[Web Research]: Search unavailable ({str(e)})")

        return "\n\n".join(context_parts)

    def get_retriever(self):
        """Returns a LangChain compatible retriever object."""
        if not self.vector_db:
            raise FileNotFoundError("Vector DB not initialized. Run ingest_all.py.")
        return self.vector_db.as_retriever(search_kwargs={"k": 4})

# --- GLOBAL INITIALIZATION (Fixes NameError) ---
# Instantiating the engine here ensures it is available when get_context is called.
rag_engine = VLSIRAGEngine()

def get_context(query: str) -> str:
    """
    Primary wrapper used by Spec_Designer.py and Spec_Chat.py.
    """
    return rag_engine.retrieve_context(query)
  
