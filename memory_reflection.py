# memory_reflection.py
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryReflection:
    """Handles reflection and summarization of memories"""
    
    def __init__(self, memory):
        self.memory = memory
    
    def reflect_and_summarize(self, topic: str) -> Optional[str]:
        """Use reflection to create higher-level insights"""
        try:
            reflection = self.memory.reflect(f"Summarize and consolidate knowledge about: {topic}")
            
            if reflection:
                # Store the reflection as important knowledge
                self.memory.retain_with_metadata(
                    content=reflection,
                    context="reflection",
                    importance="high",
                    source="reflection",
                    tags=["summary", "consolidated_knowledge", topic.lower().replace(" ", "_")]
                )
                return reflection
        except Exception as e:
            logger.warning(f"Reflection failed: {e}")
        
        return None
    
    def identify_outdated_info(self, topic: str) -> List[str]:
        """Identify potentially outdated information"""
        memories = self.memory.recall_with_priority(topic, limit=50)
        
        # Group by version and identify old ones
        versioned_memories = {}
        for memory in memories:
            if "[VERSION:" in memory:
                try:
                    version = memory.split("[VERSION:")[1].split("]")[0].strip()
                    if version not in versioned_memories:
                        versioned_memories[version] = []
                    versioned_memories[version].append(memory)
                except:
                    pass
        
        # If multiple versions exist, flag older ones
        if len(versioned_memories) > 1:
            # Sort versions (simple string comparison - could be improved)
            sorted_versions = sorted(versioned_memories.keys(), reverse=True)
            outdated = []
            for old_version in sorted_versions[1:]:  # All except the latest
                outdated.extend(versioned_memories[old_version])
            return outdated
        
        return []


class UpdateTracker:
    """Tracks updates to company rules and standards"""
    
    def __init__(self, memory):
        self.memory = memory
    
    def update_rule(
        self,
        rule_id: str,
        new_content: str,
        new_version: str,
        change_summary: str = ""
    ):
        """Update a company rule and mark old version as superseded"""
        # Store new version with high importance
        content = f"RULE ID: {rule_id}\n"
        if change_summary:
            content += f"CHANGE SUMMARY: {change_summary}\n"
        content += f"\n{new_content}"
        
        self.memory.retain_with_metadata(
            content=content,
            context=f"dfx_rule_{rule_id}",
            importance="critical",
            source="rule_update",
            version=new_version,
            tags=["dfx_rule", rule_id, "current"]
        )
        
        # Mark old versions as superseded
        old_memories = self.memory.recall_with_priority(f"RULE ID: {rule_id}", limit=20)
        for old_memory in old_memories:
            if "[VERSION:" in old_memory and new_version not in old_memory:
                # Check if it's the same rule
                if rule_id in old_memory:
                    # Store superseded marker
                    self.memory.retain_with_metadata(
                        content=f"[SUPERSEDED BY v{new_version}] {old_memory}",
                        context="superseded_rule",
                        importance="low",
                        source="rule_update",
                        tags=["superseded", rule_id]
                    )
        
        logger.info(f"Updated rule {rule_id} to version {new_version}")

