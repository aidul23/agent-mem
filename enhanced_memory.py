# enhanced_memory.py
from typing import List, Optional
from datetime import datetime
import logging

try:
    from hindsight_client import Hindsight
except ImportError:
    try:
        from hindsight import Hindsight
    except ImportError:
        raise ImportError(
            "Hindsight client not found. Please install: pip install hindsight-all"
        )

logger = logging.getLogger(__name__)


class EnhancedHindsightMemory:
    """Enhanced memory with metadata support for enterprise use"""
    
    def __init__(self, base_url: str, bank_id: str, enabled: bool = True):
        self.client = Hindsight(base_url=base_url)
        self.bank_id = bank_id
        self.enabled = enabled
    
    def retain(self, content: str, context: str | None = None):
        """Basic retain for backward compatibility"""
        if not self.enabled:
            return
        try:
            self.client.retain(
                bank_id=self.bank_id,
                content=content,
                context=context,
            )
        except Exception as e:
            logger.warning(f"Failed to retain memory: {e}")
    
    def retain_with_metadata(
        self, 
        content: str, 
        context: str | None = None,
        importance: str = "normal",  # "critical", "high", "normal", "low"
        source: str | None = None,
        version: str | None = None,
        tags: List[str] | None = None
    ):
        """Store content with rich metadata for intelligent tracking"""
        if not self.enabled:
            return
        
        # Add metadata to content
        metadata_parts = [f"[IMPORTANCE: {importance}]"]
        if version:
            metadata_parts.append(f"[VERSION: {version}]")
        if source:
            metadata_parts.append(f"[SOURCE: {source}]")
        if tags:
            metadata_parts.append(f"[TAGS: {', '.join(tags)}]")
        metadata_parts.append(f"[DATE: {datetime.now().isoformat()}]")
        
        metadata_header = " ".join(metadata_parts)
        enhanced_content = f"{metadata_header}\n{content}"
        
        try:
            self.client.retain(
                bank_id=self.bank_id,
                content=enhanced_content,
                context=context or "general",
            )
        except Exception as e:
            logger.warning(f"Failed to retain memory: {e}")
    
    def recall(self, query: str) -> List[str]:
        """Basic recall for backward compatibility"""
        if not self.enabled:
            return []
        try:
            results = self.client.recall(
                bank_id=self.bank_id,
                query=query,
            )
            return [r.text for r in results]
        except Exception as e:
            logger.warning(f"Failed to recall memory: {e}")
            return []
    
    def recall_with_priority(
        self, 
        query: str,
        prioritize_recent: bool = True,
        min_importance: str = "normal",
        limit: int = 10
    ) -> List[str]:
        """Recall with intelligent prioritization"""
        if not self.enabled:
            return []
        
        try:
            # Hindsight's recall already does semantic search
            results = self.client.recall(
                bank_id=self.bank_id,
                query=query,
            )
            
            memories = [r.text for r in results]
            
            # Post-process to prioritize recent/important memories
            if prioritize_recent:
                memories = self._prioritize_by_recency(memories)
            
            # Filter by importance
            memories = self._filter_by_importance(memories, min_importance)
            
            return memories[:limit]
        except Exception as e:
            logger.warning(f"Failed to recall memory: {e}")
            return []
    
    def _prioritize_by_recency(self, memories: List[str]) -> List[str]:
        """Sort memories by date, most recent first"""
        def extract_date(memory: str) -> datetime:
            try:
                if "[DATE:" in memory:
                    date_str = memory.split("[DATE:")[1].split("]")[0].strip()
                    return datetime.fromisoformat(date_str)
            except:
                pass
            return datetime.min  # Put undated items at end
        
        return sorted(memories, key=extract_date, reverse=True)
    
    def _filter_by_importance(self, memories: List[str], min_level: str) -> List[str]:
        """Filter memories by importance level"""
        importance_order = {"critical": 3, "high": 2, "normal": 1, "low": 0}
        min_value = importance_order.get(min_level, 0)
        
        filtered = []
        for memory in memories:
            importance = "normal"
            if "[IMPORTANCE:" in memory:
                try:
                    importance = memory.split("[IMPORTANCE:")[1].split("]")[0].strip()
                except:
                    pass
            
            if importance_order.get(importance, 1) >= min_value:
                filtered.append(memory)
        
        return filtered
    
    def reflect(self, query: str) -> Optional[str]:
        """Use Hindsight's reflect feature to create higher-level insights"""
        if not self.enabled:
            return None
        
        try:
            # Check if reflect method exists
            if hasattr(self.client, 'reflect'):
                reflection = self.client.reflect(
                    bank_id=self.bank_id,
                    query=query
                )
                return reflection
            else:
                # Fallback: use recall and summarize
                memories = self.recall_with_priority(query, limit=20)
                if memories:
                    return "\n".join(memories[:5])
        except Exception as e:
            logger.warning(f"Reflection failed: {e}")
        
        return None

