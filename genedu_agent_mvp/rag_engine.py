# rag_engine.py
import os
from typing import List, Dict, Any

import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DEVICE = "cpu"  # sentence-transformers handles device automatically if cuda available

_embed_model = None
_faiss_index = None
_doc_chunks: List[str] = []
_chunk_meta: List[Dict[str, Any]] = []

def init_vector_store():
    global _embed_model, _faiss_index
    _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    dim = _embed_model.encode(["hello"]).shape[-1]
    _faiss_index = faiss.IndexFlatL2(dim)

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text() or "")
    return "\n".join(parts)

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        seg = text[start:end].strip()
        if seg:
            chunks.append(seg)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def add_to_index(chunks: List[str], source: str):
    global _doc_chunks, _chunk_meta, _faiss_index, _embed_model
    vectors = _embed_model.encode(chunks, convert_to_numpy=True)
    _faiss_index.add(vectors.astype("float32"))
    for i, c in enumerate(chunks):
        _doc_chunks.append(c)
        _chunk_meta.append({"source": source, "idx": i})

def search_similar(query: str, k: int = 3) -> List[str]:
    global _faiss_index, _embed_model, _doc_chunks
    if _faiss_index is None or _faiss_index.ntotal == 0:
        return []
    qv = _embed_model.encode([query], convert_to_numpy=True).astype("float32")
    D, I = _faiss_index.search(qv, k)
    idxs = I[0].tolist()
    return [ _doc_chunks[i] for i in idxs if 0 <= i < len(_doc_chunks) ]
