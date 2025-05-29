from datetime import datetime
import json
import faiss
import os
import numpy as np
from infrags_mgr.embedder import Embedder
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
        json_path="infrags_mgr/data/infrags.json",
        index_path="infrags_mgr/data/infrags.faiss",
        gcs_bucket_name=None, #"voice-agent-infrags",
        gcs_blob_path="infrags.json",
    ):
        if (get_is_local() == False):
            json_path = "/gcs/voiceagent/infrags.json"
        self.json_path = json_path
        self.index_path = index_path
        self.embedder = Embedder()
        self.dim = 384
        # os.makedirs("data", exist_ok=True)
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

    def search_infrags(self, user_id, user_context, query, language, k=10):
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

    def update_infrag(self, infrag_id: str, user_id: str, user_context: str, new_text: str) -> bool:
        try:
            # Lire le fichier actuel
            file_path = "infrags_mgr/data/infrags.json"
            if not self.get_is_local():
                file_path = "/gcs/voiceagent/infrags.json"

            with open(file_path, "r") as file:
                infrags = json.load(file)

            # Chercher le fragment à modifier
            for infrag in infrags:
                # print(f"id: {infrag.get('id')}")
                # print(f"infrag_id: {infrag_id}")
                if (
                    str(infrag.get('id')) == infrag_id
                    or
                    (
                        infrag.get('user_id') == user_id
                        and
                        infrag.get('user_context') == user_context
                        and
                        infrag.get('id', f"{user_id}_{user_context}_{infrag.get('storage_date', '')}") == infrag_id
                    )
                ):

                    infrag['text'] = new_text
                    infrag['modified_date'] = datetime.now().strftime("%Y-%m-%d")

                    # Sauvegarder
                    with open(file_path, "w") as file:
                        json.dump(infrags, file, indent=2, ensure_ascii=False)

                    return True

            print("Fragment non trouvé")
            return False

        except Exception as e:
            print(f"Erreur lors de la mise à jour du fragment: {e}")
            return False

    def delete_infrag(self, infrag_id: str, user_id: str, user_context: str) -> bool:
        try:
            # Lire le fichier actuel
            file_path = "infrags_mgr/data/infrags.json"
            if not self.get_is_local():
                file_path = "/gcs/voiceagent/infrags.json"

            with open(file_path, "r") as file:
                infrags = json.load(file)
            #print(f"Nombre de fragments avant suppression: {len(infrags)}")
            # Chercher et supprimer le fragment
            original_length = len(infrags)
            infrags = [infrag for infrag in infrags if not (
                str(infrag.get('id')) == infrag_id
                or
                (
                    infrag.get('user_id') == user_id
                    and
                    infrag.get('user_context') == user_context
                    and
                    infrag.get('id', f"{user_id}_{user_context}_{infrag.get('storage_date', '')}") == infrag_id
                )
            )]
            #print(f"Nombre de fragments après suppression: {len(infrags)}")

            if len(infrags) < original_length:
                # Sauvegarder
                with open(file_path, "w") as file:
                    json.dump(infrags, file, indent=2, ensure_ascii=False)
                return True

            return False

        except Exception as e:
            print(f"Erreur lors de la suppression du fragment: {e}")
            return False

    def get_infrags_filtered(self, user_id: str = None, user_context: str = None) -> list:
        try:
            file_path = "infrags_mgr/data/infrags.json"
            if not self.get_is_local():
                file_path = "/gcs/voiceagent/infrags.json"

            with open(file_path, "r") as file:
                infrags = json.load(file)

            # Ajouter des IDs uniques si manquants
            for i, infrag in enumerate(infrags):
                if 'id' not in infrag:
                    infrag['id'] = f"{infrag.get('user_id', 'unknown')}_{infrag.get('user_context', 'unknown')}_{i}"

            # Filtrer si nécessaire
            if user_id:
                infrags = [infrag for infrag in infrags if infrag.get('user_id') == user_id]

            if user_context:
                infrags = [infrag for infrag in infrags if infrag.get('user_context') == user_context]

            return infrags

        except Exception as e:
            print(f"Erreur lors de la récupération des fragments: {e}")
            return []

    def get_is_local(self):
        """Méthode helper pour déterminer si on est en local"""
        islocal_path = "islocal.txt"
        return os.path.exists(islocal_path) and os.path.isfile(islocal_path)
