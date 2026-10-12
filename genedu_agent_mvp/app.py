# app.py
import os
import time
import uuid
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_engine import extract_text_from_pdf, chunk_text, add_to_index, search_similar, init_vector_store
from prompt_engineering import build_prompt
from llm_api import generate_answer

# ===== App & CORS =====
app = FastAPI(title="GenEdu Agent MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Globals =====
DATA_DIR = os.getenv("DATA_DIR", "data/documents")
TOP_K = int(os.getenv("TOP_K", "3"))
os.makedirs(DATA_DIR, exist_ok=True)

# init vector store (faiss + embedding)
init_vector_store()

SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_session(sid: Optional[str]) -> str:
    if sid and sid in SESSIONS:
        return sid
    new_sid = uuid.uuid4().hex[:12]
    SESSIONS[new_sid] = {"history": []}
    return new_sid

# ===== Schemas =====
class AskPayload(BaseModel):
    session_id: Optional[str] = None
    question: str = Field(..., min_length=2)
    mode: str = Field("few_shot", description="few_shot | zero_shot | cot | role | format")
    use_rag: bool = True
    role: Optional[str] = "교육 RFP 분석가"

class ScenarioCase(BaseModel):
    name: str
    question: str
    expected_contains: Optional[List[str]] = None

class ScenarioSuite(BaseModel):
    cases: List[ScenarioCase]
    mode: str = "few_shot"
    use_rag: bool = True

# ===== Endpoints =====
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(session_id: Optional[str] = None):
    sid = get_session(session_id)
    SESSIONS[sid]["history"] = []
    return {"session_id": sid, "message": "세션 초기화 완료"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "PDF만 업로드 가능")
    dest = os.path.join(DATA_DIR, file.filename)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    text = extract_text_from_pdf(dest)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(400, "텍스트 추출 실패")
    add_to_index(chunks, source=file.filename)
    return {"status": "uploaded", "file": file.filename, "chunks": len(chunks)}

@app.post("/ask")
def ask(payload: AskPayload):
    sid = get_session(payload.session_id)
    ctx_chunks = search_similar(payload.question, k=TOP_K) if payload.use_rag else []
    context = "\n---\n".join(ctx_chunks) if ctx_chunks else "(컨텍스트 없음)"
    prompt = build_prompt(
        question=payload.question,
        context=context,
        mode=payload.mode,
        role=payload.role,
    )
    answer = generate_answer(prompt)
    SESSIONS[sid]["history"].append(
        {"q": payload.question, "ctx": ctx_chunks, "a": answer, "ts": time.time()}
    )
    return {
        "session_id": sid,
        "answer": answer,
        "used_rag": payload.use_rag,
        "k": TOP_K,
        "context_preview": ctx_chunks,
        "history_len": len(SESSIONS[sid]["history"]),
    }

@app.post("/scenario/test")
def run_scenarios(suite: ScenarioSuite):
    results = []
    total = 0
    correct = 0
    for case in suite.cases:
        ctx = "\n---\n".join(search_similar(case.question, k=TOP_K)) if suite.use_rag else "(컨텍스트 없음)"
        prompt = build_prompt(question=case.question, context=ctx, mode=suite.mode)
        ans = generate_answer(prompt)
        checks = []
        if case.expected_contains:
            total += len(case.expected_contains)
            for kw in case.expected_contains:
                hit = (kw.lower() in ans.lower())
                checks.append({"kw": kw, "hit": hit})
                correct += 1 if hit else 0
        results.append({"name": case.name, "answer": ans, "checks": checks})
    score = 0.0 if total == 0 else round(correct / total * 100, 2)
    return {"score": score, "correct": correct, "total": total, "results": results}
