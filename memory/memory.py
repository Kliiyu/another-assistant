import faiss
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

index_path = 'memory/faiss_index/index.faiss'
data_path = 'memory/faiss_index/data.pkl'

# Load or create
if os.path.exists(index_path):
    index = faiss.read_index(index_path)
    with open(data_path, 'rb') as f:
        documents = pickle.load(f)
else:
    index = faiss.IndexFlatL2(384)
    documents = []

def add_to_memory(text: str):
    embedding = model.encode([text])
    index.add(np.array(embedding))
    documents.append(text)
    faiss.write_index(index, index_path)
    with open(data_path, 'wb') as f:
        pickle.dump(documents, f)

def search_memory(query: str, k: int = 3) -> list:
    if len(documents) == 0:
        return []
    embedding = model.encode([query])
    D, I = index.search(np.array(embedding), k)
    return [documents[i] for i in I[0] if i < len(documents)]
