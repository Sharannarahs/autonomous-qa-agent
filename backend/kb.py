import os
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

class KnowledgeBase:
    def __init__(self):
        os.makedirs("data", exist_ok=True)

        # NEW ChromaDB client (no Settings required)
        self.client = PersistentClient(path="data")

        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_document(self, text: str, source: str):
        embedding = self.model.encode([text])[0].tolist()

        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"source": source}],
            ids=[source + "_" + str(len(text))]   # unique ID
        )

    def query(self, query_text: str, top_k=5):
        embedding = self.model.encode([query_text])[0].tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        docs = []
        for i in range(len(results["documents"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"]
            })

        return docs
