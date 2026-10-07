"""Natural-language assistant over the Patients analytics database."""

from __future__ import annotations

import os

from src.analytics import answer_question, load_patients
from src.config import ANALYTICS_DB, env_flag, sqlite_uri

try:
    from langchain_community.utilities import SQLDatabase
except Exception:  # pragma: no cover - optional dependency
    SQLDatabase = None

try:
    from langchain_experimental.agents import create_sql_agent
except Exception:  # pragma: no cover - compatibility fallback
    create_sql_agent = None

try:
    from langchain_ollama import ChatOllama
except Exception:  # pragma: no cover - optional dependency
    ChatOllama = None

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency
    ChatOpenAI = None


def _build_llm():
    if env_flag("USE_OLLAMA", "0"):
        if ChatOllama is None:
            raise RuntimeError("Ollama support is not installed. pip install langchain-ollama")
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:latest"),
            temperature=0,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if os.getenv("OPENAI_API_KEY"):
        if ChatOpenAI is None:
            raise RuntimeError("OpenAI support is not installed. pip install langchain-openai")
        return ChatOpenAI(temperature=0, model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    return None


def ask_hospital_ai(user_question: str) -> str:
    llm = None
    try:
        llm = _build_llm()
    except Exception as exc:
        return _with_fallback(user_question, f"LLM setup failed ({exc}). Using built-in analytics instead.")

    if llm is None or SQLDatabase is None or create_sql_agent is None or not ANALYTICS_DB.exists():
        return answer_question(user_question)

    try:
        db = SQLDatabase.from_uri(sqlite_uri(ANALYTICS_DB))
        agent_executor = create_sql_agent(llm, db=db, verbose=False)
        response = agent_executor.invoke({"input": user_question})
        return response["output"]
    except Exception as exc:
        message = str(exc).lower()
        if "connection refused" in message or "ollama" in message:
            return _with_fallback(
                user_question,
                "Local Ollama is not reachable. Using built-in analytics instead.",
            )
        return _with_fallback(user_question, f"The SQL agent could not complete that request ({exc}).")


def _with_fallback(user_question: str, note: str) -> str:
    try:
        answer = answer_question(user_question, load_patients())
    except Exception:
        return note
    return f"{note}\n\n{answer}"
