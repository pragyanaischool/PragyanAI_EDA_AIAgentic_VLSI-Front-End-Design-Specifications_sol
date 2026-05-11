import os
from typing import List
from dotenv import load_dotenv

# Modern LangChain and HuggingFace integrations
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Load environment variables (GROQ_API_KEY, etc.)
load_dotenv()

class VLSIRAGEngine:
    """
    Advanced Retrieval-Augmented Generation (RAG) Engine for VLSI Design.
    Uses local HuggingFace embeddings for cost-efficiency and ChromaDB
    for high-speed semantic retrieval of hardware specifications.
    """
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # Initialize local HuggingFace Embeddings
        # 'all-MiniLM-L6-v2' is optimized for technical document similarity
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},  # Can be changed to 'cuda' for GPU acceleration
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize the Vector Store reference
        self.vector_db = None
        if os.path.exists(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            print(f"Warning: Persist directory {self.persist_directory} not found. Please run ingest_data.py.")

    def retrieve_context(self, query: str, k: int = 4) -> str:
        """
        Performs a similarity search and returns concatenated context segments.
        """
        if not self.vector_db:
            return "No reference standards found. Grounding will rely on pre-trained LLM knowledge."
        
        # Search for top-k relevant snippets
        docs = self.vector_db.similarity_search(query, k=k)
        
        # Format the output for the LLM Architect
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Spec")
            page = doc.metadata.get("page", "N/A")
            content = doc.page_content.strip().replace("\n", " ")
            
            context_parts.append(
                f"--- Reference {i+1} [Source: {source}, Page: {page}] ---\n"
                f"{content}\n"
            )
            
        return "\n".join(context_parts)

    def get_retriever(self):
        """
        Returns a LangChain-compatible retriever for use in LangGraph pipelines.
        """
        if not self.vector_db:
            raise FileNotFoundError("Vector DB not initialized.")
        return self.vector_db.as_retriever(search_kwargs={"k": 4})

# Global instance for the Multi-Agentic Framework
rag_engine = VLSIRAGEngine()

def get_context(query: str) -> str:
    """
    Simplified helper function for agents to fetch grounding data.
    """
    return rag_engine.retrieve_context(query)
    
