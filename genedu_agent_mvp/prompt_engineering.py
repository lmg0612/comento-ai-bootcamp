# prompt_engineering.py
from typing import List

SYSTEM_ROLE = """당신은 교육기관 RFP/제안서를 해석하고 요약/질의응답/액션아이템을 제시하는
도우미입니다. 불분명하면 추가 정보를 요청하고, 사실 근거가 없으면 추측을 경계하세요.
말투는 친절하고 간결하게, 단 답변은 근거(문맥 요약 또는 출처)를 함께 제시하세요."""

FORMAT_GUIDE = """#출력형식
- 요약: 한두 문장
- 핵심포인트: 불릿 3개 이내
- 답변: 본문
- 근거: 문맥 근거(있다면 출처 힌트)
"""

FEW_SHOT = [
    {
        "q": "핵심 목표는?",
        "a": "요약: 생성형 AI 기반 교수학습 지원 환경 구축\n핵심포인트:\n- 드라이브+RAG 기반 Q&A\n- 교수/학습자 맞춤 프롬프트\n- 운영/보안 고려\n답변: 교육현장에서 AI를 활용해 자료 관리/검색/요약/질의응답을 통합 제공하는 것이 목적입니다.\n근거: RFP Ⅰ-Ⅲ 항목."
    },
    {
        "q": "보안은 어떻게?",
        "a": "요약: 최소 권한과 암호화\n핵심포인트:\n- 접근제어/로그\n- 데이터 전송/저장 암호화\n- 관리자 페이지 보호\n답변: 개인정보 및 문서 보안을 위해 접근제어와 암호화, 관리자 접근 통제를 적용합니다.\n근거: 보안 요구사항 절."
    }
]

def _few_shot_block() -> str:
    shots = "\n\n".join([f"Q: {s['q']}\nA: {s['a']}" for s in FEW_SHOT])
    return f"\n#예시(Few-Shot)\n{shots}"

def build_prompt(question: str, context: str, mode: str = "few_shot", role: str = "교육 RFP 분석가") -> str:
    header = f"""{SYSTEM_ROLE}

#역할
{role}

#명령문
아래 제약조건과 입력문을 참고해 출력형식에 맞춰 답하세요.

#제약조건
- 근거 없는 단정 금지
- 필요한 경우 반문
- 7문장 이내

{FORMAT_GUIDE}
#입력문
질문: {question}

#문맥(컨텍스트):
{context}
"""
    if mode == "few_shot":
        return header + _few_shot_block() + "\n\n#출력개시\n답변:"
    if mode == "cot":
        return header + "\n참고: 단계적으로 사고하여 근거를 정리하세요.\n\n#출력개시\n답변:"
    if mode == "role":
        return header + "\n참고: 지정된 역할 관점으로 설명하세요.\n\n#출력개시\n답변:"
    if mode == "format":
        return header + "\n참고: 마크다운 소제목을 활용해 가독성 있게 작성하세요.\n\n#출력개시\n답변:"
    # zero_shot or default
    return header + "\n#출력개시\n답변:"
