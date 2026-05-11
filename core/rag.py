import os
from typing import List
from dotenv import load_dotenv

# Newer LangChain HuggingFace integration
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

class VLSIRAGEngine:
    """
    Advanced RAG Engine for VLSI Front-End Design.
    Uses HuggingFace local embeddings and ChromaDB for high-speed, 
    cost-effective retrieval of hardware specifications.
    """
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory[cite: 1]
        
        # Initialize the embedding model (HuggingFace Local)
        # 'all-MiniLM-L6-v2' provides excellent performance/latency ratio for technical docs
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}, 
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Vector Store reference
        self.vector_db = None
        if os.path.exists(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )[cite: 1]

    def retrieve_context(self, query: str, k: int = 4) -> str:
        """
        Performs a semantic similarity search across indexed VLSI standards.
        Returns formatted context segments for LLM consumption.
        """
        if not self.vector_db:
            return "No reference standards found in the local database. Please run ingest_all.py first."[cite: 1]
        
        # Retrieve the k most similar chunks[cite: 1]
        docs = self.vector_db.similarity_search(query, k=k)
        
        # Format the results into a structured context string[cite: 1]
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Spec")[cite: 1]
            page = doc.metadata.get("page", "N/A")[cite: 1]
            content = doc.page_content.strip().replace("\n", " ")[cite: 1]
            
            context_parts.append(
                f"[Document Segment {i+1}]\n"
                f"Source: {source} (Page {page})\n"
                f"Content: {content}\n"
                "-----------------------------------"
            )[cite: 1]
            
        return "\n\n".join(context_parts)[cite: 1]

    def get_retriever(self):
        """
        Returns a LangChain compatible retriever object for LCEL pipelines.[cite: 1]
        """
        if not self.vector_db:
            raise FileNotFoundError("Vector DB not initialized. Ensure /data/chroma_db exists.")[cite: 1]
        return self.vector_db.as_retriever(search_kwargs={"k": 4})[cite: 1]

# Global instance for easy import into the LangGraph state machine[cite: 1]
rag_engine = VLSIRAGEngine()

def get_context(query: str) -> str:
    """
    Helper wrapper for the Streamlit UI and Agents.[cite: 1]
    """
    return rag_engine.retrieve_context(query)[cite: 1]
    
