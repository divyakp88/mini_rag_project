from fastapi import FastAPI
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3
import json

app=FastAPI()  #create FastAPI app

#load fiass
index=faiss.read_index("embeddings/index.faiss") #loading the FAISS index back from disk into memory
ids=np.load("embeddings/ids.npy") #load ids

#load chunks
conn=sqlite3.connect("chunks.db")
c=conn.cursor()

#load embedding model
model=SentenceTransformer('all-MiniLM-L6-v2')

#load sources.json
with open("data/sources.json",'r') as f:
    sources=json.load(f)

#count Keyword matches
def keyword_score(chunk_text,query):
    count=sum(chunk_text.lower().count(word.lower()) for word in query.split())
    return count/max(len(query.split()),1)

@app.get("/")
def home():
    return {"message": "API is running. Use POST /ask"}

@app.post("/ask")
def ask(q:str,k:int=5,mode:str="hybrid"):
    conn=sqlite3.connect("chunks.db")
    c=conn.cursor()
    #1.embed question
    query_emb=model.encode([q]).astype('float32')

    #2.Retrieve top 20 baseline
    D,I=index.search(query_emb,20)
    seen = set()
    unique_indices = []
    for idx in I[0]:
        if idx not in seen:
            seen.add(idx)
            unique_indices.append(idx)
    candidate_chunks=[]
    for idx, score in zip(unique_indices, D[0][:len(unique_indices)]):
        #print("FAISS idx:", idx, "FAISS id:", ids[idx])
        c.execute("SELECT pdf_title,pdf_url,chunk_text FROM chunks WHERE vector_index=?",(int(idx),))
        row=c.fetchone()
        #print("DB row:",row)
        if row is None:
            continue
        candidate_chunks.append({
            "title":row[0],
            "url":row[1],
            "text":row[2],
            "vector_score":float(score)
        })

    #3Hybrid Rerenker 
    seen_texts = set()
    deduped_chunks = []
    for chunk in candidate_chunks:
            if chunk['text'] not in seen_texts:
                seen_texts.add(chunk['text'])
                deduped_chunks.append(chunk)
    candidate_chunks = deduped_chunks   
    alpha=0.6
    for chunk in candidate_chunks:
        k_score=keyword_score(chunk['text'],q)
        #Normalize score
        chunk['final_score']=alpha*chunk['vector_score']+(1-alpha)*k_score
    
    #sort by final score
    candidate_chunks.sort(key=lambda x:x['final_score'],reverse=True)

    #pick top answer
    top_chunk=candidate_chunks[0] if candidate_chunks else None
    answer_text=top_chunk['text'][:300] if top_chunk else None

    conn.close()

    #return json response
    return {
        "answer":answer_text,
        "contexts":candidate_chunks[:k],
        "reranker_used":True
    }
