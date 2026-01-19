# Enterprise Features Documentation

## Overview

The enterprise implementation extends the basic agent with advanced memory management, document ingestion, and intelligent tracking capabilities for company-specific knowledge bases.

## Key Features

### 1. Multi-Bank Memory Structure

The system uses separate memory banks for different knowledge domains:

- **Company Knowledge Base**: Company-wide rules, standards, DFX guidelines
- **Product Knowledge Base**: Product-specific information
- **Department Knowledge Base**: Department-specific knowledge
- **User Memory**: Individual user interactions and preferences

### 2. Enhanced Memory with Metadata

All memories are stored with rich metadata:
- **Importance**: critical, high, normal, low
- **Version**: Track document/rule versions
- **Source**: Origin of the information
- **Tags**: Categorization tags
- **Date**: Timestamp for recency tracking

### 3. Intelligent Memory Retrieval

- **Recency Prioritization**: Most recent information is prioritized
- **Importance Filtering**: Filter by importance level
- **Multi-Source Context**: Combine information from multiple knowledge bases

### 4. Document Ingestion

Ingest company documents (PDF, TXT, MD) with:
- Automatic chunking for large documents
- Metadata tagging
- Version tracking

### 5. Rule Update Tracking

- Track rule updates with version numbers
- Automatically mark old versions as superseded
- Maintain change history

### 6. Memory Reflection

- Generate summaries and consolidations
- Identify outdated information
- Create higher-level insights

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Basic configuration
OPENAI_API_KEY=your-key
HINDSIGHT_BASE_URL=http://localhost:8888

# Enterprise configuration
COMPANY_ID=your-company-id
USE_ENTERPRISE_MODE=true
ADMIN_TOKEN=your-secure-admin-token
UPLOAD_FOLDER=./uploads
```

### Enabling Enterprise Mode

Set `USE_ENTERPRISE_MODE=true` in your `.env` file to enable enterprise features.

## Usage

### Admin Panel

Access the admin panel at: `http://localhost:5001/admin`

Features:
1. **Upload Document**: Upload PDF, TXT, or MD files
2. **Ingest Text**: Directly paste text content
3. **Update Rule**: Update existing rules with new versions
4. **Reflect & Summarize**: Generate summaries on topics

### API Endpoints

#### Ingest Document
```bash
POST /admin/ingest-document
Headers: Authorization: Bearer <admin-token>
Form Data:
  - file: Document file
  - type: Document type (dfx_rule, standard, etc.)
  - version: Version number
  - importance: critical|high|normal|low
```

#### Ingest Text
```bash
POST /admin/ingest-text
Headers: Authorization: Bearer <admin-token>
Body: {
  "content": "Text content",
  "type": "dfx_rule",
  "version": "1.0",
  "importance": "high",
  "source": "manual_input"
}
```

#### Update Rule
```bash
POST /admin/update-rule
Headers: Authorization: Bearer <admin-token>
Body: {
  "rule_id": "DFX-001",
  "content": "Updated rule content",
  "version": "2.0",
  "summary": "Updated for new requirements"
}
```

#### Reflect
```bash
POST /admin/reflect
Headers: Authorization: Bearer <admin-token>
Body: {
  "topic": "DFX rules for PCB design",
  "bank_type": "company",
  "product_id": "optional-if-product-bank"
}
```

### Chat Interface

The chat interface now supports:
- **Product ID**: Filter by specific product
- **Department**: Filter by department

These are optional fields that help the agent retrieve more relevant information.

## Architecture

### File Structure

```
agent-mem/
├── enhanced_memory.py          # Enhanced memory with metadata
├── enterprise_memory.py        # Multi-bank memory manager
├── enterprise_agent.py         # Enterprise agent implementation
├── document_ingestion.py       # Document ingestion system
├── memory_reflection.py        # Reflection and update tracking
├── agent.py                    # Main agent (supports both modes)
├── app.py                      # Flask app with admin endpoints
└── static/
    ├── index.html              # Main chat interface
    └── admin.html              # Admin panel
```

### Memory Banks

Memory banks are organized as:
- `company-{company_id}-kb`: Company knowledge base
- `company-{company_id}-product-{product_id}`: Product knowledge
- `company-{company_id}-dept-{department}`: Department knowledge
- `company-{company_id}-user-{user_id}`: User memory

## Best Practices

### 1. Document Organization

- Use consistent naming for document types
- Maintain version numbers
- Tag documents appropriately

### 2. Rule Updates

- Always increment version numbers
- Provide change summaries
- Use rule IDs for tracking

### 3. Importance Levels

- **Critical**: Must-know information, compliance requirements
- **High**: Important guidelines, standards
- **Normal**: General information
- **Low**: Reference material, historical data

### 4. Regular Reflection

- Periodically run reflection on key topics
- Identify and update outdated information
- Consolidate related knowledge

## Security

- Admin endpoints require authentication token
- Set `ADMIN_TOKEN` in environment variables
- Never commit admin tokens to version control
- Use strong, unique tokens in production

## Troubleshooting

### Memory Not Updating

- Check Hindsight server is running
- Verify memory bank IDs are correct
- Check logs for errors

### Documents Not Ingesting

- Verify file format is supported
- Check file size (large files are chunked)
- Ensure admin token is correct

### Agent Not Using Company Knowledge

- Verify `USE_ENTERPRISE_MODE=true`
- Check company_id is set correctly
- Ensure documents are ingested into company KB

## Migration from Basic Mode

1. Set `USE_ENTERPRISE_MODE=true` in `.env`
2. Set `COMPANY_ID` to your company identifier
3. Set `ADMIN_TOKEN` for admin access
4. Restart the application
5. Access admin panel to ingest documents

Existing user memories will continue to work, but will be organized under the company structure.

