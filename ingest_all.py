import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

def build_vlsi_knowledge_base():
    """
    Processes all PDFs in the /data directory and adds them to the 
    persistent ChromaDB vector store if they are not already indexed.
    """
    # 1. Initialize Local Embeddings (Same as in rag.py)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    persist_dir = "./data/chroma_db"
    
    # 2. Initialize or Load the Vector Store
    vector_db = Chroma(
        persist_directory=persist_dir, 
        embedding_function=embeddings
    )
    
    # 3. Identify Already Indexed Files (Avoid Redundancy)
    existing_sources = set()
    try:
        # Fetch metadata from the DB to see which files are already present[cite: 1]
        db_data = vector_db.get()
        if db_data and 'metadatas' in db_data:
            existing_sources = {m['source'] for m in db_data['metadatas'] if 'source' in m}
    except Exception as e:
        print(f"Starting with a fresh database. (Internal info: {e})")

    # 4. Collect and Load New Documents[cite: 1]
    documents = []
    data_path = "./data"
    
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print("Folder './data' created. Please add VLSI PDF specs there.")
        return

    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            full_path = os.path.join(data_path, file)
            # Normalize path for comparison[cite: 1]
            normalized_path = os.path.abspath(full_path)
            
            # Check against the existing_sources set[cite: 1]
            if normalized_path not in [os.path.abspath(s) for s in existing_sources]:
                print(f"🆕 Indexing NEW file: {file}")
                try:
                    loader = PyPDFLoader(full_path)
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"❌ Error loading {file}: {e}")
            else:
                print(f"⏭️ Skipping (Already Indexed): {file}")

    # 5. Process and Append New Data[cite: 1]
    if documents:
        # Technical specs benefit from smaller chunks to maintain signal accuracy[cite: 1]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=120
        )
        splits = text_splitter.split_documents(documents)
        
        # .add_documents appends to existing index; .from_documents would overwrite[cite: 1]
        vector_db.add_documents(splits)
        print(f"✅ Successfully added {len(splits)} new chunks to the Knowledge Base.")
    else:
        print("🏁 No new documents were processed.")

if __name__ == "__main__":
    build_vlsi_knowledge_base()
  
