# Mini RAG Project

A small **RAG-based Q&A system** built using **FAISS**, **Sentence Transformers**, and **FastAPI**.  
It allows users to ask questions over a small set of documents and retrieve relevant answers with hybrid retrieval + reranker.

---

## Setup Instructions

1. Clone the repo:  
```bash
git clone https://github.com/divyakp88/mini_rag_project.git
```

2.Create and activate a virtual environment:
```bash
python -m venv rag_env
# Windows
rag_env\Scripts\activate
# Linux/macOS
source rag_env/bin/activate
```
3.Install dependencies:
```bash
pip install -r requirements.txt
```
4.Run the FastAPI app:
```bash
uvicorn api.main:app --reload
```
The API will be available at http://127.0.0.1:8000/

Interactive docs: http://127.0.0.1:8000/docs

## Screenshots

## What I Learned

Building this project taught me how to:

1.Split documents into chunks and generate embeddings using Sentence Transformers.

2.Use FAISS for efficient similarity search.

3.Implement a hybrid reranker combining vector similarity and keyword matching.

4.Build a FastAPI backend for serving a question-answering service.

5.Organize a small project for clarity, including docs, examples, and reproducible results.


