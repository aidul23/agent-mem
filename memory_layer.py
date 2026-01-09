# memory_layer.py
from typing import List
import logging

try:
    from hindsight_client import Hindsight
except ImportError:
    # Fallback for different package structures
    try:
        from hindsight import Hindsight
    except ImportError:
        raise ImportError(
            "Hindsight client not found. Please install: pip install hindsight-all"
        )

logger = logging.getLogger(__name__)


class HindsightMemory:
    def __init__(self, base_url: str, bank_id: str, enabled: bool = True):
        self.client = Hindsight(base_url=base_url)
        self.bank_id = bank_id
        self.enabled = enabled

    def retain(self, content: str, context: str | None = None):
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

    def recall(self, query: str) -> List[str]:
        if not self.enabled:
            return []
        try:
            results = self.client.recall(
                bank_id=self.bank_id,
                query=query,
            )
            return [r.text for r in results]  # per SDK docs
        except Exception as e:
            logger.warning(f"Failed to recall memory: {e}")
            return []

