# GenEdu Agent MVP

프론트 없이 FastAPI로 동작하는 **RAG + 프롬프트 튜닝** 에이전트.
- 임베딩: `sentence-transformers/all-MiniLM-L6-v2` (무료)
- 생성: `google/gemma-1.1-2b-it` (Transformers 로컬/허깅페이스 Hub)

## 빠른 실행
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## 엔드포인트
- `GET /health`
- `POST /upload_pdf` (form-data: `file=@RFP.pdf`)
- `POST /ask` (JSON: `{ "question": "...", "use_rag": true, "mode": "few_shot" }`)
- `POST /scenario/test` (`sample_scenarios.json` 참고)
- `POST /reset`

## 환경변수
- `GEN_MODEL` 기본: `google/gemma-1.1-2b-it`
- `EMBED_MODEL` 기본: `sentence-transformers/all-MiniLM-L6-v2`
- `TOP_K` 기본: 3
- `MAX_NEW_TOKENS` 기본: 256
- `TEMPERATURE` 기본: 0.4

## 배포 (예: Cloud Run)
```bash
gcloud run deploy genedu-agent --source . --region=asia-northeast3 --allow-unauthenticated
```

## 데이터 확보 방법
- 본인이 가진 공개 RFP/제안서 PDF를 업로드
- 공개 자료: 대학 산학협력단 공지, 나라장터 공고, 교육부/지자체 보고서 등
