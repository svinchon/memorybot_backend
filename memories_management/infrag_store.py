import json
import faiss
import os
import numpy as np
from memories_management.embedder import Embedder  # vectorization lib

# define the InfragStore class
# this class is used to store the information fragments
# that are relevant to the question
class InfragStore:

    # this method is used to initialize the InfragStore class
    def __init__(
        self,
        json_path="memories_management/data/infrags.json",
        index_path="memories_management/data/infrags.faiss",
    ):
        # store the paths to the json and index files
        self.json_path = json_path
        self.index_path = index_path
        # create the embedder object
        self.embedder = Embedder()
        self.dim = 384  # Taille du vecteur pour le modèle MiniLM
        # create the folder to store the json and index files if needed
        os.makedirs("data", exist_ok=True)
        # call the load_infrags method to load the infrags from the json file
        self.infrags = self.load_infrags()
        # create the index for the infrags
        self.index = faiss.IndexFlatL2(self.dim)
        self.id_map = [] # map to store the id of the infrags
        # check if the index file exists and rebuuild index if so
        if self.infrags:
            self.rebuild_index()

    def load_infrags(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # the save_infrags method is used to save the infrags to the json file
    def save_infrags(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.infrags, f, ensure_ascii=False, indent=2)

    # the add_infrag method is used to add an infrag to the json file
    def add_infrag(self, user_id, user_context, text, date):
        # convert the text to a vector
        vec = self.embedder.embed(text)
        # determin id of the infrag
        infrag_id = len(self.infrags)
        # adde json object to the infrags list
        self.infrags.append(
            {
                "id": infrag_id,
                "user_id": user_id,
                "user_context": user_context,
                "text": text,
                "date": date,
            }
        )
        # add the vector to the index
        self.index.add(np.array([vec]).astype("float32"))
        self.id_map.append(infrag_id)
        # save the infrags to the json file
        self.save_infrags()

    # the rebuild_index method is used to rebuild the index if needed
    def rebuild_index(self):
        vectors = []
        self.id_map = []
        for i, mem in enumerate(self.infrags):
            vec = self.embedder.embed(mem["text"])
            vectors.append(vec)
            self.id_map.append(mem["id"])
        self.index.add(np.array(vectors).astype("float32"))

    # the search_infrags method is used to search for infrags in the index
    def search_infrags(self, user_id, user_context, query, k=10):
        # 1. Filter infrags by user_id and user_context
        filtered_infrags = [
            infrag
            for infrag in self.infrags
            if infrag["user_id"] == user_id
            and infrag["user_context"] == user_context
        ]
        if not filtered_infrags:
            return []  # No matching infrags found
        # 2. Rebuild a temporary index with filtered infrags
        temp_index = faiss.IndexFlatL2(self.dim)
        temp_id_map = []
        vectors = []
        for i, infrag in enumerate(filtered_infrags):
            vec = self.embedder.embed(infrag["text"])
            vectors.append(vec)
            temp_id_map.append(i)  # Use index in filtered_infrags as temp_id
        temp_index.add(np.array(vectors).astype("float32"))
        # 3. Search the temporary index
        vec = self.embedder.embed(query)
        D, I = temp_index.search(np.array([vec]).astype("float32"), k)
        # 4. Map back to original infrags
        return [filtered_infrags[temp_id_map[i]] for i in I[0]]
