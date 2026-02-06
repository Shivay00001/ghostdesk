import os
import uuid
import logging
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class KnowledgeBase:
    _instance = None
    
    def __init__(self, persist_dir="knowledge_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        # Use default sentence-transformers model (all-MiniLM-L6-v2)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="enterprise_docs",
            embedding_function=self.ef
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = KnowledgeBase()
        return cls._instance

    def ingest_file(self, file_path: str) -> bool:
        """
        Ingests a PDF or Text file into the vector DB.
        """
        try:
            text = ""
            if file_path.endswith(".pdf"):
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

            if not text.strip():
                logger.warn(f"Empty text in {file_path}")
                return False

            # Naive Chunking
            chunk_size = 500
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": os.path.basename(file_path), "chunk_id": i} for i in range(len(chunks))]

            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Ingested {len(chunks)} chunks from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Ingest failed: {e}")
            return False

    def query(self, query_text: str, n_results=3) -> List[Dict[str, Any]]:
        """
        Retrieves top-N relevant chunks.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Parse Chroma result structure
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0]
        
        structured_results = []
        for doc, meta, dist in zip(docs, metas, distances):
            structured_results.append({
                "text": doc,
                "metadata": meta,
                "distance": dist
            })
            
        return structured_results
