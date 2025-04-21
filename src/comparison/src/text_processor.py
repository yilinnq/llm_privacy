from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import textwrap

class TextProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 200
        self.overlap = 50

    def create_chunks(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        
        return chunks

    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        return self.model.encode(chunks)

    def find_relevant_chunks(self, query: str, chunks: List[str], embeddings: np.ndarray, top_k: int = 3) -> List[Dict]:
        query_embedding = self.model.encode([query])[0]
        similarities = np.dot(embeddings, query_embedding)
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'chunk': chunks[idx],
                'similarity': similarities[idx],
                'index': idx
            })
        
        return results
