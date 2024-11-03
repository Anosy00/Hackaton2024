import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialisez FAISS et le modèle d'encodage
dimension = 384
index = faiss.IndexFlatL2(dimension)
model = SentenceTransformer('all-MiniLM-L6-v2')

def add_to_faiss_index(text, document_id):
    vector = model.encode(text)
    index.add(np.array([vector]).astype('float32'))

def search_in_faiss(query, k=5):
    query_vector = model.encode(query)
    _, indices = index.search(np.array([query_vector]).astype('float32'), k)
    return indices
