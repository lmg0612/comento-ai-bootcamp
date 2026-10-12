# 코멘토 직무부트캠프 — 인공지능 (JJ 현직자 직무부트캠프)

> 2025.07 ~ 2025.08 · 수료

## 개요
현직자 멘토의 업무 요청서에 따라 LLM 기반 서비스를 단계적으로 만든 직무 부트캠프입니다. 프롬프트 설계 → RAG 파이프라인 → 프론트엔드 배포 → 에이전트 MVP 순으로 진행했습니다.

## 과제
### 2주차 — RAG 파이프라인 + 웹 배포 (`assignments/week2/`)
- **Backend**: PDF 로드 → 청크 분할 → OpenAI 임베딩 → FAISS 저장 → Retriever → 프롬프트 → GPT-4o 체인 (금융상품 안내 챗봇)
- **Frontend**: Streamlit 챗봇 UI로 PDF 업로드·질의응답, localtunnel로 외부 공개

### 최종 — GenEdu Agent MVP (`genedu_agent_mvp/`)
FastAPI 기반 **RAG + 프롬프트 튜닝** 에이전트. RFP·제안서 PDF를 올리면 관련 내용을 검색해 답변합니다.
- 임베딩 `all-MiniLM-L6-v2`, 생성 `gemma-1.1-2b-it` (무료 모델)
- 엔드포인트: `/upload_pdf`, `/ask` (zero-shot / few-shot 모드), `/scenario/test`
- Dockerfile 포함, Cloud Run 배포 가능

```bash
cd genedu_agent_mvp
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## 문서 (`docs/`)
`코멘토 최종.pdf` — 최종 제안서 (교육용 RAG 에이전트 서비스 구축 제안)

> 코멘토 제공 강의자료·업무요청서·가이드 문서는 저작권 문제로 공개본에서 제외했습니다.

## 기술
Python · LangChain · OpenAI API · FAISS · Streamlit · FastAPI · Hugging Face Transformers · Docker
