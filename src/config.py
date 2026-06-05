import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_keywords() -> dict:
    with open(CONFIG_DIR / "keywords.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources() -> dict:
    with open(CONFIG_DIR / "sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

MAX_PAPERS_PER_WEEK = int(os.getenv("MAX_PAPERS_PER_WEEK", "20"))
