import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService(object):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, text: str) -> np.ndarray:
        return self.model.encode(text)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts)

    def build_index(self, projects: list[dict]) -> faiss.IndexFlatIP:
        texts = [f"[{", ".join(p["technologies"])}] {p["description"]}" for p in projects]
        embeddings = self.encode_batch(texts)

        # Normalizar embeddings para similaridade coseno
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        index = faiss.IndexFlatIP(self.dimension)  # Inner Product = coseno após normalização
        index.add(embeddings)

        # Guardar referência aos projetos
        self.projects = projects
        return index

    def search(self, index: faiss.IndexFlatIP, job_description: str, top_n: int = 5):
        query_vec = self.encode(job_description)
        query_vec = query_vec / np.linalg.norm(query_vec)

        query_vec = np.expand_dims(query_vec, axis=0)  # FAISS espera 2D
        scores, indices = index.search(query_vec, top_n)

        results = []
        for rank, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            project = self.projects[idx]
            results.append({
                "rank": rank + 1,
                "score": float(scores[0][rank]),
                "project": project
            })

        return results
