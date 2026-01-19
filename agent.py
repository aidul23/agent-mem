# agent.py
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from auth_and_profile import get_or_create_user
from memory_layer import HindsightMemory

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
USE_ENTERPRISE_MODE = os.environ.get("USE_ENTERPRISE_MODE", "false").lower() == "true"

llm = ChatOpenAI(
    model="gpt-4o-mini",  # or lab-preferred model
    api_key=OPENAI_API_KEY,
)

SYSTEM_TEMPLATE = """You are a helpful assistant for GPT-Lab.
You can use the following long-term memory about the user:

{memory_snippets}

When answering, prefer using the user-specific information when relevant.
If memory_snippets is empty, just answer normally.
"""


def build_agent_for_user(user_id: str) -> Dict[str, Any]:
    profile = get_or_create_user(user_id)
    memory = HindsightMemory(
        base_url="http://localhost:8888",
        bank_id=f"user-{user_id}",
        enabled=profile.allow_memory,
    )
    return {"profile": profile, "memory": memory}


def run_agent_turn(
    user_id: str, 
    user_message: str,
    product_id: Optional[str] = None,
    department: Optional[str] = None
) -> str:
    """Run agent turn - uses enterprise mode if enabled"""
    if USE_ENTERPRISE_MODE:
        from enterprise_agent import run_enterprise_agent_turn
        return run_enterprise_agent_turn(
            user_id=user_id,
            user_message=user_message,
            product_id=product_id,
            department=department
        )
    
    # Original simple mode
    ctx = build_agent_for_user(user_id)
    memory: HindsightMemory = ctx["memory"]

    # 1) Recall from Hindsight to build context
    try:
        recalled = memory.recall(query=user_message)  # natural-language query
        memory_context = "\n".join(f"- {m}" for m in recalled) if recalled else "None."
    except Exception as e:
        # If Hindsight is unavailable, continue without memory
        print(f"Warning: Could not recall memory: {e}")
        memory_context = "None."

    # 2) Compose messages
    system_msg = SystemMessage(
        content=SYSTEM_TEMPLATE.format(memory_snippets=memory_context)
    )
    human_msg = HumanMessage(content=user_message)

    # Invoke LLM directly with messages
    response = llm.invoke([system_msg, human_msg])
    answer_text = response.content

    # 3) Retain new info (depends on consent)
    try:
        memory.retain(
            content=f"User said: {user_message}\nAssistant answered: {answer_text}",
            context="chat_turn",
        )
    except Exception as e:
        # If Hindsight is unavailable, continue without storing
        print(f"Warning: Could not retain memory: {e}")

    return answer_text

