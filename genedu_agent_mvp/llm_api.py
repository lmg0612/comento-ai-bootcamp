# llm_api.py
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
GEN_MODEL_NAME = os.getenv("GEN_MODEL", "google/gemma-1.1-2b-it")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.4"))

# Lazy-load once
_tokenizer = None
_model = None
_generator = None

def _load():
    global _tokenizer, _model, _generator
    if _generator is not None:
        return _generator
    _tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_NAME)
    _model = AutoModelForCausalLM.from_pretrained(
        GEN_MODEL_NAME,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        device_map="auto" if DEVICE == "cuda" else None,
    )
    _generator = pipeline("text-generation", model=_model, tokenizer=_tokenizer, device=0 if DEVICE=="cuda" else -1)
    return _generator

def generate_answer(prompt: str) -> str:
    gen = _load()
    outputs = gen(prompt, max_new_tokens=MAX_NEW_TOKENS, temperature=TEMPERATURE, pad_token_id=getattr(gen.tokenizer, "eos_token_id", None))
    text = outputs[0]["generated_text"]
    # try to trim from last '답변:' marker if present
    if "답변:" in text:
        text = text.split("답변:", 1)[-1]
    return text.strip()
