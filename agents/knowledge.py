import logging
import json
from typing import Optional
from ..core.llm import OllamaClient
from ..core.rag import KnowledgeBase
from .skeletons import BaseAgent

logger = logging.getLogger(__name__)

class AttributionAgent(BaseAgent):
    def __init__(self, model: str = "llama3.2"):
        super().__init__("Attribution")
        self.llm = OllamaClient()
        self.kb = KnowledgeBase.get_instance()
        self.model = model

    def answer_question(self, query: str) -> str:
        """
        RAG workflow: Retrieve -> Augment -> Generate -> Cite.
        """
        # 1. Retrieve
        chunks = self.kb.query(query, n_results=3)
        
        if not chunks:
            return "I checked the Knowledge Base, but found no relevant documents."

        # Filter by relevance threshold (e.g., distance < 1.5, varies by metric)
        # For PoC, we just use what we found.
        
        context_str = ""
        sources = set()
        
        for i, chunk in enumerate(chunks):
            src = chunk['metadata']['source']
            context_str += f"CHUNK {i+1} (Source: {src}):\n{chunk['text']}\n---\n"
            sources.add(src)

        # 2. Prompt
        system = """
        You are an Enterprise Attribution Bot. 
        Answer the question using ONLY the provided context chunks.
        Do NOT use outside knowledge.
        If the answer is not in the context, say "I don't know".
        Always cite the Source at the end.
        """
        
        full_prompt = f"Context:\n{context_str}\n\nQuestion: {query}\nAnswer:"
        
        logger.info(f"Generating RAG answer for: {query}")
        response = self.llm.generate(
            prompt=full_prompt,
            system=system,
            model=self.model
        )
        
        if response:
            return response
        else:
            return "Failed to generate answer."
