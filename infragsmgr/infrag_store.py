import json
import faiss
import os
import numpy as np
from infragsmgr.embedder import Embedder
from google.cloud import storage

def get_is_local():
    islocal_path = "islocal.txt"
    if os.path.exists(islocal_path) and os.path.isfile(islocal_path):
        return True
    else:
        return False

class InfragStore:

    def __init__(
        self,
        json_path="infragsmgr/data/infrags.json",
        index_path="infragsmgr/data/infrags.faiss",
        gcs_bucket_name=None, #"voice-agent-infrags",
        gcs_blob_path="infrags.json",
    ):
        if (get_is_local() == False):
            json_path = "/gcs/voiceagent/infrags.json"
        self.json_path = json_path
        self.index_path = index_path
        self.embedder = Embedder()
        self.dim = 384
        os.makedirs("data", exist_ok=True)
        self.infrags = self.load_infrags()
        self.index = faiss.IndexFlatL2(self.dim)
        self.id_map = []
        if self.infrags:
            self.rebuild_index()
        self.gcs_bucket_name = gcs_bucket_name
        self.gcs_blob_path = gcs_blob_path
        if gcs_bucket_name:
            self.gcs_client = storage.Client()
            self.gcs_bucket = self.gcs_client.bucket(gcs_bucket_name)

    def load_infrags(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_infrags(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.infrags, f, ensure_ascii=False, indent=2)

    def add_infrag(self, user_id, user_context, text, date):
        vec = self.embedder.embed(text)
        infrag_id = len(self.infrags)
        json_data = {
            "id": infrag_id,
            "user_id": user_id,
            "user_context": user_context,
            "text": text,
            "storage_date": date,
        }
        self.infrags.append(json_data)
        self.index.add(np.array([vec]).astype("float32"))
        self.id_map.append(infrag_id)
        self.save_infrags()

    def rebuild_index(self):
        vectors = []
        self.id_map = []
        for i, mem in enumerate(self.infrags):
            vec = self.embedder.embed(mem["text"])
            vectors.append(vec)
            self.id_map.append(mem["id"])
        self.index.add(np.array(vectors).astype("float32"))

    def search_infrags(self, user_id, user_context, query, k=10):
        filtered_infrags = [
            infrag
            for infrag in self.infrags
            if infrag["user_id"] == user_id
            and infrag["user_context"] == user_context
        ]
        if not filtered_infrags:
            return []
        temp_index = faiss.IndexFlatL2(self.dim)
        temp_id_map = []
        vectors = []
        for i, infrag in enumerate(filtered_infrags):
            vec = self.embedder.embed(infrag["text"])
            vectors.append(vec)
            temp_id_map.append(i)
        temp_index.add(np.array(vectors).astype("float32"))
        vec = self.embedder.embed(query)
        D, I = temp_index.search(np.array([vec]).astype("float32"), k)
        return [filtered_infrags[temp_id_map[i]] for i in I[0]]

    def reload_infrags(self):
        self.infrags = self.load_infrags()
        self.index.reset()  # Clear the existing FAISS index
        if self.infrags:
            self.rebuild_index()

