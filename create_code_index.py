import os
import chromadb
from langchain.text_splitter import PythonCodeTextSplitter
import ollama
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_code_index():
    """Reads MISO's source code, chunks it, and stores it in a ChromaDB vector store."""
    logging.info("Starting MISO codebase indexing...")
    
    SOURCE_DIRECTORY = "python_agent_runner"
    DB_DIRECTORY = "miso_code_db"
    COLLECTION_NAME = "miso_source_code"

    # 1. Load and Chunk Code
    documents = []
    for root, _, files in os.walk(SOURCE_DIRECTORY):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                logging.info(f"Loading: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                documents.append({"code": code, "source": file_path})

    text_splitter = PythonCodeTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = []
    for doc in documents:
        split_chunks = text_splitter.create_documents([doc["code"]])
        for chunk in split_chunks:
            chunks.append({"text": chunk.page_content, "metadata": {"source": doc["source"]}})
    
    logging.info(f"Split codebase into {len(chunks)} chunks.")

    # 2. Setup Vector Database
    client = chromadb.PersistentClient(path=DB_DIRECTORY)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # 3. Embed and Store
    logging.info("Generating embeddings and storing in vector DB. This may take a few minutes...")
    for i, chunk in enumerate(chunks):
        response = ollama.embeddings(
            model='mxbai-embed-large',
            prompt=chunk["text"]
        )
        collection.add(
            ids=[str(i)],
            embeddings=[response["embedding"]],
            documents=[chunk["text"]],
            metadatas=[chunk["metadata"]]
        )
    
    logging.info(f"? Successfully indexed {collection.count()} code chunks into ChromaDB at '{DB_DIRECTORY}'.")

if __name__ == "__main__":
    create_code_index()
