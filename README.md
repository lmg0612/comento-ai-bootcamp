# 코멘토 AI 직무부트캠프 — RAG 파이프라인 & GenEdu Agent MVP

> 2025.07 ~ 2025.08 · 수료 · 개인 과제
> 현직자 멘토의 업무 요청서에 따라 프롬프트 설계 → RAG 파이프라인 → 웹 배포 → 에이전트 MVP 순으로 LLM 서비스를 단계적으로 만든 과정

## 핵심 요약

- **2주차**: PDF를 청크로 나눠 OpenAI 임베딩·FAISS에 저장하고, LangChain 체인으로 GPT-4o가 답하는 금융상품 안내 챗봇을 만들고 Streamlit으로 공개했습니다.
- **최종 과제(GenEdu Agent MVP)**: 교육 기관의 RFP·제안서 PDF를 올리면 관련 내용을 찾아 답하는 **FastAPI RAG 에이전트**입니다. 유료 API 없이 무료 모델(임베딩 MiniLM, 생성 Gemma 2B)로 동작합니다.
- 같은 질문을 **zero-shot / few-shot** 프롬프트로 바꿔 보고, 기대 키워드를 담은 **시나리오 테스트 엔드포인트**로 답변을 점검할 수 있게 했습니다.

## 아키텍처 (GenEdu Agent MVP)

```
POST /upload_pdf  ─▶ PyMuPDF 텍스트 추출 ─▶ 600자 청크 (80자 겹침)
                    ─▶ all-MiniLM-L6-v2 임베딩 ─▶ FAISS (L2)

POST /ask         ─▶ 질문 임베딩 ─▶ FAISS 상위 3개 청크
                    ─▶ build_prompt (역할 · 제약조건 · 출력형식 · few-shot 예시)
                    ─▶ gemma-1.1-2b-it (Transformers) ─▶ 요약 · 핵심포인트 · 답변 · 근거

POST /scenario/test ─▶ sample_scenarios.json의 질문들을 일괄 실행, 기대 키워드 포함 여부 확인
```

## 구현 포인트

| 영역 | 구현 내용 | 관련 파일 |
|---|---|---|
| 문서 처리 | PDF 텍스트 추출, 고정 길이 청크 + 겹침 | `genedu_agent_mvp/rag_engine.py` |
| 검색 | sentence-transformers 임베딩, FAISS 인메모리 인덱스, 상위 k개 반환 (`TOP_K` 환경 변수) | `rag_engine.py` |
| 프롬프트 | 역할·명령문·제약조건("근거 없는 단정 금지")·출력형식을 나눈 템플릿, zero-shot / few-shot 모드 | `prompt_engineering.py` |
| 생성 | Hugging Face Transformers 파이프라인, 생성 길이·온도 환경 변수로 조정 | `llm_api.py` |
| API | `/health` · `/upload_pdf` · `/ask` · `/scenario/test` · `/reset`, 세션별 대화 기록 | `app.py` |
| 배포 | Dockerfile, Cloud Run 배포 명령 | `Dockerfile` |

## 프로젝트 구조

```
assignments/week2/      2주차 과제: RAG 백엔드(LangChain·FAISS·GPT-4o) + Streamlit 프론트 노트북
genedu_agent_mvp/       최종 과제: FastAPI RAG 에이전트
├─ app.py               API 엔드포인트
├─ rag_engine.py        PDF 추출 · 청크 · 임베딩 · FAISS 검색
├─ prompt_engineering.py 프롬프트 템플릿, few-shot 예시
├─ llm_api.py           Gemma 생성 파이프라인
└─ sample_scenarios.json 시나리오 테스트 질문
docs/코멘토 최종.pdf     최종 제안서 (교육용 RAG 에이전트 서비스 구축 제안)
```

## 빠른 실행

```bash
cd genedu_agent_mvp
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# curl -F "file=@RFP.pdf" localhost:8000/upload_pdf
# curl -X POST localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"핵심 목표는?","use_rag":true,"mode":"few_shot"}'
```

## 기술 스택

Python · LangChain · OpenAI API · FAISS · Streamlit · FastAPI · Hugging Face Transformers · sentence-transformers · PyMuPDF · Docker

## 공개 범위

코멘토 제공 강의자료·업무요청서·가이드 문서는 저작권 문제로 공개본에서 제외했습니다.
