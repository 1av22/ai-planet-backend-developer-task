# ai-planet-backend-developer-task/Backend/app/search.py
import faiss
import numpy as np
from .rag_integration import generate_gemini_embeddings


class DocumentSearch:
    def __init__(self, dimension: int = 768):
        self.index = faiss.IndexFlatL2(dimension)

    def add_documents(self, documents: list):
        """Adds document embeddings to the FAISS index."""
        embeddings = [generate_gemini_embeddings(
            doc['content']) for doc in documents]
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 5):
        """Search for the most relevant documents based on the query."""
        query_embedding = np.array(
            generate_gemini_embeddings(query)).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)
        return indices, distances
