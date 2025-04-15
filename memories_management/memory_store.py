import json
import faiss
import os
import numpy as np
from memories_management.embedder import Embedder # vectorization lib

class MemoryStore:

    def __init__(self, json_path="data/memories.json", index_path="data/index.faiss"):
        self.json_path = json_path
        self.index_path = index_path
        self.embedder = Embedder()
        self.dim = 384  # Taille du vecteur pour le modèle MiniLM

        os.makedirs("data", exist_ok=True)
        self.memories = self.load_memories()

        self.index = faiss.IndexFlatL2(self.dim)
        self.id_map = []  # correspondance entre index et ID de souvenir

        if self.memories:
            self.rebuild_index()

    def load_memories(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_memories(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_memory(self, text, date):
        vec = self.embedder.embed(text)
        memory_id = len(self.memories)
        self.memories.append({
            "id": memory_id,
            "text": text,
            "date": date
        })
        self.index.add(np.array([vec]).astype("float32"))
        self.id_map.append(memory_id)
        self.save_memories()

    def rebuild_index(self):
        vectors = []
        self.id_map = []
        for i, mem in enumerate(self.memories):
            vec = self.embedder.embed(mem["text"])
            vectors.append(vec)
            self.id_map.append(mem["id"])
        self.index.add(np.array(vectors).astype("float32"))

    def search_memories(self, query, k=3):
        vec = self.embedder.embed(query)
        D, I = self.index.search(np.array([vec]).astype("float32"), k)
        return [self.memories[self.id_map[i]] for i in I[0]]
