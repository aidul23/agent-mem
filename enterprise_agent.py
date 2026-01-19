# enterprise_agent.py
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from auth_and_profile import get_or_create_user
from enterprise_memory import EnterpriseMemoryManager
from enhanced_memory import EnhancedHindsightMemory

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
HINDSIGHT_BASE_URL = os.environ.get("HINDSIGHT_BASE_URL", "http://localhost:8888")
COMPANY_ID = os.environ.get("COMPANY_ID", "default-company")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
)


class EnterpriseAgent:
    """Enterprise agent with multi-source memory"""
    
    def __init__(self, company_id: str = COMPANY_ID, base_url: str = HINDSIGHT_BASE_URL):
        self.company_id = company_id
        self.memory_manager = EnterpriseMemoryManager(base_url, company_id)
        self.llm = llm
    
    def run_agent_turn(
        self, 
        user_id: str, 
        user_message: str,
        product_id: Optional[str] = None,
        department: Optional[str] = None
    ) -> str:
        """Run agent turn with enterprise memory"""
        # Get all relevant memory banks
        company_kb = self.memory_manager.get_company_kb()
        user_memory = self.memory_manager.get_user_memory(user_id)
        
        # Recall from company knowledge base (DFX rules, etc.)
        company_context = company_kb.recall_with_priority(
            query=user_message,
            prioritize_recent=True,
            min_importance="normal",
            limit=5
        )
        
        # Recall from user-specific memory
        user_context = user_memory.recall_with_priority(
            query=user_message,
            prioritize_recent=True,
            limit=3
        )
        
        # If product-specific, get product KB
        product_context = []
        if product_id:
            product_kb = self.memory_manager.get_product_kb(product_id)
            product_context = product_kb.recall_with_priority(
                query=user_message,
                prioritize_recent=True,
                limit=5
            )
        
        # If department-specific, get department KB
        dept_context = []
        if department:
            dept_kb = self.memory_manager.get_department_kb(department)
            dept_context = dept_kb.recall_with_priority(
                query=user_message,
                prioritize_recent=True,
                limit=5
            )
        
        # Build comprehensive context
        memory_context = self._build_context(
            company_context,
            user_context,
            product_context,
            dept_context
        )
        
        # Generate response with all context
        system_msg = SystemMessage(content=f"""You are an expert assistant for {self.company_id}.

COMPANY KNOWLEDGE BASE (DFX Rules, Standards):
{memory_context['company']}

PRODUCT-SPECIFIC INFORMATION:
{memory_context['product']}

DEPARTMENT-SPECIFIC INFORMATION:
{memory_context['department']}

USER-SPECIFIC CONTEXT:
{memory_context['user']}

IMPORTANT INSTRUCTIONS:
- Always prioritize the most recent information
- If there are conflicting rules or standards, use the most up-to-date version
- When answering, cite which knowledge source you're using (company KB, product KB, etc.)
- Be precise and reference specific rules when applicable
- If information is outdated, mention that and use the latest version""")
        
        human_msg = HumanMessage(content=user_message)
        response = self.llm.invoke([system_msg, human_msg])
        answer_text = response.content
        
        # Store interaction with metadata
        user_memory.retain_with_metadata(
            content=f"Q: {user_message}\nA: {answer_text}",
            context="user_interaction",
            importance="normal",
            source="chat",
            tags=["interaction", "user_query"]
        )
        
        return answer_text
    
    def _build_context(self, company: list, user: list, product: list, dept: list) -> Dict:
        """Build structured context from multiple memory sources"""
        return {
            "company": "\n".join(f"- {m}" for m in company) if company else "None.",
            "user": "\n".join(f"- {m}" for m in user) if user else "None.",
            "product": "\n".join(f"- {m}" for m in product) if product else "None.",
            "department": "\n".join(f"- {m}" for m in dept) if dept else "None."
        }


# Global enterprise agent instance
_enterprise_agent: Optional[EnterpriseAgent] = None


def get_enterprise_agent(company_id: str = COMPANY_ID) -> EnterpriseAgent:
    """Get or create enterprise agent instance"""
    global _enterprise_agent
    if _enterprise_agent is None:
        _enterprise_agent = EnterpriseAgent(company_id=company_id)
    return _enterprise_agent


def run_enterprise_agent_turn(
    user_id: str,
    user_message: str,
    product_id: Optional[str] = None,
    department: Optional[str] = None,
    company_id: Optional[str] = None
) -> str:
    """Convenience function to run enterprise agent turn"""
    agent = get_enterprise_agent(company_id or COMPANY_ID)
    return agent.run_agent_turn(user_id, user_message, product_id, department)

