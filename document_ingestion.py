# document_ingestion.py
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Handles ingestion of company documents into memory"""
    
    def __init__(self, memory):
        self.memory = memory
    
    def ingest_document(
        self, 
        file_path: str,
        document_type: str = "dfx_rule",
        version: str = "1.0",
        importance: str = "high",
        content: Optional[str] = None
    ):
        """Ingest a document into memory"""
        try:
            # Load content if not provided
            if content is None:
                content = self._load_document(file_path)
            
            # Split into chunks (for large documents)
            chunks = self._chunk_document(content, chunk_size=1000)
            
            # Store each chunk with metadata
            for i, chunk in enumerate(chunks):
                self.memory.retain_with_metadata(
                    content=chunk,
                    context=f"{document_type}_chunk_{i}",
                    importance=importance,
                    source=file_path,
                    version=version,
                    tags=[document_type, "company_standard"]
                )
            
            logger.info(f"Ingested {len(chunks)} chunks from {file_path}")
            return len(chunks)
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            raise
    
    def _load_document(self, file_path: str) -> str:
        """Extract text from document"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Handle different file types
        if file_path.endswith('.txt') or file_path.endswith('.md'):
            return file_path_obj.read_text(encoding='utf-8')
        elif file_path.endswith('.pdf'):
            # For PDF, try to use PyPDF2 if available
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                logger.warning("PyPDF2 not available, cannot read PDF. Install with: pip install PyPDF2")
                raise ImportError("PyPDF2 required for PDF processing")
        else:
            # Try to read as text
            try:
                return file_path_obj.read_text(encoding='utf-8')
            except:
                raise ValueError(f"Unsupported file type: {file_path}")
    
    def _chunk_document(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Split document into manageable chunks"""
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [content]

