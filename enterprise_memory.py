# enterprise_memory.py
from typing import Dict, Optional
from enhanced_memory import EnhancedHindsightMemory


class EnterpriseMemoryManager:
    """Manages multiple memory banks for enterprise use"""
    
    def __init__(self, base_url: str, company_id: str):
        self.base_url = base_url
        self.company_id = company_id
    
    def get_company_kb(self) -> EnhancedHindsightMemory:
        """Company-wide knowledge base (DFX rules, standards, etc.)"""
        return EnhancedHindsightMemory(
            base_url=self.base_url,
            bank_id=f"company-{self.company_id}-kb",
            enabled=True
        )
    
    def get_product_kb(self, product_id: str) -> EnhancedHindsightMemory:
        """Product-specific knowledge base"""
        return EnhancedHindsightMemory(
            base_url=self.base_url,
            bank_id=f"company-{self.company_id}-product-{product_id}",
            enabled=True
        )
    
    def get_user_memory(self, user_id: str) -> EnhancedHindsightMemory:
        """User-specific memory"""
        return EnhancedHindsightMemory(
            base_url=self.base_url,
            bank_id=f"company-{self.company_id}-user-{user_id}",
            enabled=True
        )
    
    def get_department_kb(self, department: str) -> EnhancedHindsightMemory:
        """Department-specific knowledge base"""
        return EnhancedHindsightMemory(
            base_url=self.base_url,
            bank_id=f"company-{self.company_id}-dept-{department}",
            enabled=True
        )

