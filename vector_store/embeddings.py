import os
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingGenerator:
    """Generate embeddings for text summaries"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv(
            'EMBEDDING_MODEL',
            'sentence-transformers/all-MiniLM-L6-v2'
        )
        print(f"🔄 Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("✅ Embedding model loaded")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()

# Usage
if __name__ == "__main__":
    generator = EmbeddingGenerator()
    text = "ARGO float temperature profile in Arabian Sea"
    embedding = generator.generate_embedding(text)
    print(f"Embedding dimension: {len(embedding)}")
