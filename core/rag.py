import os
from typing import List
from dotenv import load_dotenv

# Newer LangChain HuggingFace integration
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Load environment variables (for OpenAI or Groq keys)
load_dotenv()

class VLSI_RAG_Engine:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # Initialize the embedding model
        # 'all-MiniLM-L6-v2' is fast, accurate, and runs locally on your CPU/GPU
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}, # Change to 'cuda' if using GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Vector Store reference
        self.vector_db = None
        if os.path.exists(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Performs a similarity search and returns a concatenated string of context.
        """
        if not self.vector_db:
            return "No reference standards found in the local database. Please run ingest_data.py first."
        
        # Perform Similarity Search
        # 
        docs = self.vector_db.similarity_search(query, k=k)
        
        # Format the results for the LLM
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Source")
            content = doc.page_content.replace("\n", " ")
            context_parts.append(f"--- Context Segment {i+1} (Source: {source}) ---\n{content}")
            
        return "\n\n".join(context_parts)

    def get_retriever(self):
        """
        Returns the vector_db as a retriever object for use in LangChain LCEL chains.
        """
        if not self.vector_db:
            raise ValueError("Vector DB not initialized.")
        return self.vector_db.as_retriever(search_kwargs={"k": 3})

# Global instance for easy import
rag_engine = VLSI_RAG_Engine()

def get_context(query: str) -> str:
    """Helper function for the Streamlit UI to call."""
    return rag_engine.retrieve_context(query)
