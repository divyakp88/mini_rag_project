import sqlite3
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
os.makedirs("embeddings", exist_ok=True)

#Load sqlite chunks
conn=sqlite3.connect("chunks.db")
c=conn.cursor()
c.execute("SELECT vector_index,chunk_text FROM chunks ORDER BY vector_index")
data=c.fetchall()
print("Rows fetched from DB:", len(data))
conn.close()

ids=[row[0] for row in data]
texts=[row[1] for row in data]

#load embeddding model
model=SentenceTransformer('all-MiniLM-L6-v2')

#generate embeddings
embeddings=model.encode(texts,show_progress_bar=True)
embeddings=np.array(embeddings).astype('float32') #convert embeddings to numpy array

#Build FAISS index
dimension=embeddings.shape[1]
index=faiss.IndexFlatL2(dimension)
index.add(embeddings)

#save index and IDS
faiss.write_index(index,"embeddings/index.faiss")
np.save("embeddings/ids.npy",np.array(ids))
print("FAISS index built and saved!")