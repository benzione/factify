# Factify AI-Ready API Documentation

This document describes the API endpoints for the Factify Intelligent Document Understanding system.

## Base URL

`http://127.0.0.1:5000`

## Supported Document Types

The Factify system can intelligently classify and process the following document types:

### Predefined Document Types
- **Invoice**: Business invoices with vendor information, amounts, due dates, and line items
- **Contract**: Legal contracts and agreements with parties, dates, and key terms
- **Report**: Business reports including financial statements, quarterly reports, and analytics

### Dynamic "Other" Document Type
For documents that don't fit the predefined categories, the system automatically:
- **Classifies as "other"**: Handles letters, memos, presentations, manuals, forms, and general business documents
- **Dynamic analysis**: Uses AI to identify the most relevant metadata fields for each specific document
- **Intelligent extraction**: Extracts both standard metadata (title, author, date) and document-specific information
- **Smart actionable items**: Generates relevant actionable items even for unknown document types

### Example Document Classifications

| Document Type | Confidence | Extracted Metadata Examples |
|---------------|------------|------------------------------|
| `invoice` | 0.95 | vendor, amount, due_date, line_items |
| `contract` | 0.88 | parties, effective_date, termination_date, key_terms |
| `report` | 0.92 | reporting_period, key_metrics, executive_summary |
| `other` | 0.75 | document_title, author, subject, key_points, document_purpose |

## Environment Configuration

Before using the API, ensure your environment is properly configured:

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# --- API Keys ---
GEMINI_API_KEY="your_actual_gemini_api_key_here"

# --- LLM Configuration ---
GEMINI_MODEL="gemini-1.5-flash"        # Available: gemini-1.5-flash, gemini-1.5-pro, gemini-pro
LLM_TEMPERATURE="0.3"                  # 0.0-1.0, lower = more focused responses
LLM_MAX_TOKENS="2048"                  # Maximum response length

# --- Caching Configuration ---
CACHE_ENABLED="true"                   # Enable/disable response caching
CACHE_EXPIRATION_TIME_SECONDS="3600"  # Cache expiration time (1 hour)
```

### Model Selection Guide

| Model | Speed | Cost | Accuracy | Best For |
|-------|-------|------|----------|----------|
| `gemini-1.5-flash` | ⚡ Fast | 💰 Low | ✅ Good | Most documents, production use |
| `gemini-1.5-pro` | 🐌 Slower | 💰💰 Higher | ✅✅ Excellent | Complex documents, high accuracy needs |
| `gemini-pro` | 🐌 Slower | 💰 Low | ✅ Good | Legacy fallback option |

### Quick Setup

Use the provided helper script to create your environment configuration:

```bash
python create_env.py
```

This script will:
- Create a `.env` file with all required variables
- Guide you through the configuration process
- Validate your current settings

## Error Responses

All errors will follow a consistent JSON format:

```json
{
  "code": "ERROR_CODE_STRING",
  "message": "A human-readable error message.",
  "details": {
    // Optional additional details specific to the error
  }
}
```

## Endpoints

### 1. POST /documents/analyze

Accepts a raw PDF file for processing and returns the extracted metadata. The endpoint now accepts multipart/form-data file uploads directly.

**Method:** POST  
**URL:** `/documents/analyze`  
**Content-Type:** `multipart/form-data`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | The PDF file to be processed (must be a valid PDF) |

### Request Example

**Using curl:**
```bash
curl -X POST http://127.0.0.1:5000/documents/analyze \
  -F "file=@/path/to/your/document.pdf" \
  -H "Content-Type: multipart/form-data"
```

**Using Python requests:**
```python
import requests

# Upload a file directly
with open('invoice.pdf', 'rb') as file:
    files = {'file': ('invoice.pdf', file, 'application/pdf')}
    response = requests.post('http://127.0.0.1:5000/documents/analyze', files=files)
    result = response.json()
```

**Using JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://127.0.0.1:5000/documents/analyze', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Example Response (200 OK)

**For Invoice Document:**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "filename": "invoice_sample.pdf",
  "classification": {
    "type": "invoice",
    "confidence": 0.98
  },
  "metadata": {
    "vendor": {
      "value": "Acme Corp",
      "description": "The name of the company or individual issuing the invoice."
    },
    "amount": {
      "value": "$1500.00",
      "description": "The total amount due on the invoice, including currency."
    },
    "due_date": {
      "value": "2024-07-15",
      "description": "The date by which the invoice payment is expected."
    },
    "line_items": {
      "value": [
        {"description": "Consulting Services", "quantity": 10, "unit_price": 150.0, "total": 1500.0}
      ],
      "description": "A list of individual products or services with their quantities and prices."
    }
  },
  "processing_status": "success",
  "error_message": null
}
```

**For "Other" Document Type (e.g., Business Letter):**
```json
{
  "document_id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
  "filename": "meeting_announcement.pdf", 
  "classification": {
    "type": "other",
    "confidence": 0.75
  },
  "metadata": {
    "document_title": {
      "value": "Quarterly Team Meeting Announcement",
      "description": "The title or main heading of the document."
    },
    "author": {
      "value": "John Smith, Project Manager",
      "description": "The person or organization who created or authored the document."
    },
    "date_created": {
      "value": "2024-01-10",
      "description": "The date when the document was created or issued."
    },
    "subject": {
      "value": "Q1 2024 Team Meeting Logistics",
      "description": "The main subject or topic that the document addresses."
    },
    "key_points": {
      "value": "Meeting scheduled for January 15th at 2:00 PM in main conference room. Agenda includes Q4 performance review, new project initiatives, and Q1 budget planning.",
      "description": "The most important points, findings, or conclusions mentioned in the document."
    },
    "document_purpose": {
      "value": "Inform team members about upcoming quarterly meeting and provide agenda details",
      "description": "The primary purpose or intended use of the document."
    },
    "meeting_date": {
      "value": "2024-01-15",
      "description": "Meeting date identified through dynamic analysis."
    },
    "location": {
      "value": "Main conference room",
      "description": "Meeting location identified through dynamic analysis."
    }
  },
  "processing_status": "success",
  "error_message": null
}
```

**Key Differences for "Other" Documents:**
- **Dynamic Metadata Fields**: The system intelligently identifies relevant fields beyond the standard ones
- **Lower Confidence**: Typically 0.3-0.8 confidence range as these are catch-all classifications
- **Adaptive Extraction**: Metadata fields vary based on document content and purpose
- **Contextual Descriptions**: Each field includes AI-generated descriptions explaining its relevance

#### Example Error Response (400 Bad Request - Invalid Input)
```json
{
  "code": "INVALID_INPUT",
  "message": "No file uploaded. Please include a file in the 'file' field of the multipart/form-data request.",
  "details": {}
}
```

**Other possible validation errors:**
```json
{
  "code": "INVALID_INPUT",
  "message": "No file selected for upload.",
  "details": {}
}
```
```json
{
  "code": "INVALID_INPUT",
  "message": "Only PDF files are supported.",
  "details": {}
}
```

#### Example Error Response (500 Internal Server Error - Document Processing Failed)
```json
{
  "code": "DOCUMENT_PROCESSING_FAILED",
  "message": "Failed to read PDF file corrupted.pdf: PDF doesn't contain a /Root object",
  "details": {
    "file_path": "/tmp/corrupted.pdf"
  }
}
```

### 2. GET /documents/{id}

Returns a specific document's metadata by its unique ID. The response is structured to be easily consumable by AI agents, including semantic descriptions of fields.

**Method:** GET  
**URL:** `/documents/{id}` (e.g., `/documents/a1b2c3d4-e5f6-7890-1234-567890abcdef`)

#### Example Response (200 OK)
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "filename": "invoice_sample.pdf",
  "classification": {
    "type": "invoice",
    "confidence": 0.98
  },
  "metadata": {
    "vendor": {
      "value": "Acme Corp",
      "description": "The name of the company or individual issuing the invoice."
    },
    "amount": {
      "value": "$1500.00",
      "description": "The total amount due on the invoice, including currency."
    },
    "due_date": {
      "value": "2024-07-15",
      "description": "The date by which the invoice payment is expected."
    },
    "line_items": {
      "value": [
        {"description": "Consulting Services", "quantity": 10, "unit_price": 150.0, "total": 1500.0}
      ],
      "description": "A list of individual products or services with their quantities and prices."
    }
  },
  "processing_status": "success",
  "error_message": null
}
```

#### Example Error Response (404 Not Found)
```json
{
  "code": "DOCUMENT_NOT_FOUND",
  "message": "Document not found.",
  "details": {
    "document_id": "non-existent-id-12345"
  }
}
```

### 3. GET /documents/{id}/actions

Returns all actionable items identified for a specific document, with optional filtering.

**Method:** GET  
**URL:** `/documents/{id}/actions` (e.g., `/documents/a1b2c3d4-e5f6-7890-1234-567890abcdef/actions`)

#### Query Parameters (Optional):
- `status`: Filter by action status (e.g., `pending`, `completed`, `overdue`)
- `deadline`: Filter by exact deadline date (e.g., `2024-07-15`)
- `priority`: Filter by priority level (e.g., `low`, `medium`, `high`)

#### Example Response (200 OK)
```json
[
  {
    "item_id": "f7e8d9c0-b1a2-3456-7890-abcdef123456",
    "description": "Pay invoice for $1500.00 from Acme Corp.",
    "status": "pending",
    "deadline": "2024-07-15",
    "priority": "high",
    "source_field": "amount, due_date"
  },
  {
    "item_id": "12345678-90ab-cdef-1234-567890abcdef",
    "description": "Review line item: Consulting Services",
    "status": "pending",
    "deadline": null,
    "priority": "medium",
    "source_field": "line_items"
  }
]
```

#### Example Response with Filtering
**GET** `/documents/{id}/actions?status=pending&priority=high`

```json
[
  {
    "item_id": "f7e8d9c0-b1a2-3456-7890-abcdef123456",
    "description": "Pay invoice for $1500.00 from Acme Corp.",
    "status": "pending",
    "deadline": "2024-07-15",
    "priority": "high",
    "source_field": "amount, due_date"
  }
]
```

#### Example Response for "Other" Document Type (Meeting Announcement)
```json
[
  {
    "item_id": "c3d4e5f6-g7h8-9012-3456-789012cdefgh",
    "description": "Review and process document: Quarterly Team Meeting Announcement",
    "status": "pending",
    "deadline": null,
    "priority": "medium",
    "source_field": "document_title, subject"
  },
  {
    "item_id": "d4e5f6g7-h8i9-0123-4567-890123defghi",
    "description": "Address document purpose: Inform team members about upcoming quarterly meeting and provide agenda details",
    "status": "pending",
    "deadline": null,
    "priority": "medium",
    "source_field": "document_purpose"
  },
  {
    "item_id": "e5f6g7h8-i9j0-1234-5678-901234efghij",
    "description": "Consider key point 1: Meeting scheduled for January 15th at 2:00 PM in main conference room",
    "status": "pending",
    "deadline": "2024-01-15",
    "priority": "high",
    "source_field": "key_points"
  },
  {
    "item_id": "f6g7h8i9-j0k1-2345-6789-012345fghijk",
    "description": "Follow up with document author: John Smith, Project Manager",
    "status": "pending",
    "deadline": null,
    "priority": "low",
    "source_field": "author"
  }
]
```

#### Example Error Response (404 Not Found)
```json
{
  "code": "DOCUMENT_NOT_FOUND",
  "message": "Document not found.",
  "details": {
    "document_id": "non-existent-id-12345"
  }
}
```

### 4. GET /health

Health check endpoint to verify the API is running.

**Method:** GET  
**URL:** `/health`

#### Example Response (200 OK)
```json
{
  "status": "healthy",
  "message": "Factify API is running!"
}
```

## API Usage Examples

### Using curl

1. **Health Check**
   ```bash
   curl -X GET http://127.0.0.1:5000/health
   ```

2. **Analyze Document** (with direct file upload)
   ```bash
   # Upload a PDF file directly
   curl -X POST http://127.0.0.1:5000/documents/analyze \
     -F "file=@documents_to_process/invoice.pdf"
   
   # Upload with explicit content type
   curl -X POST http://127.0.0.1:5000/documents/analyze \
     -F "file=@path/to/your/document.pdf;type=application/pdf"
   ```

3. **Get Document Metadata**
   ```bash
   curl -X GET http://127.0.0.1:5000/documents/a1b2c3d4-e5f6-7890-1234-567890abcdef
   ```

4. **Get Actionable Items with Filtering**
   ```bash
   curl -X GET "http://127.0.0.1:5000/documents/a1b2c3d4-e5f6-7890-1234-567890abcdef/actions?status=pending&priority=high"
   ```

### Using Python requests

```python
import requests

# Health check
response = requests.get('http://127.0.0.1:5000/health')
print(response.json())

# Analyze document with direct file upload
with open('invoice.pdf', 'rb') as file:
    files = {'file': ('invoice.pdf', file, 'application/pdf')}
    response = requests.post('http://127.0.0.1:5000/documents/analyze', files=files)
    
if response.status_code == 200:
    result = response.json()
    document_id = result['document_id']
    print(f"Document processed successfully! ID: {document_id}")
    
    # Get metadata
    response = requests.get(f'http://127.0.0.1:5000/documents/{document_id}')
    print("Metadata:", response.json())

    # Get actionable items
    response = requests.get(f'http://127.0.0.1:5000/documents/{document_id}/actions?status=pending')
    print("Actionable items:", response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Using JavaScript (Fetch API)

```javascript
// File upload with fetch
async function uploadDocument(fileInput) {
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch('http://127.0.0.1:5000/documents/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Document processed:', result);
            
            // Get metadata
            const metadataResponse = await fetch(`http://127.0.0.1:5000/documents/${result.document_id}`);
            const metadata = await metadataResponse.json();
            console.log('Metadata:', metadata);
            
        } else {
            console.error('Upload failed:', response.status, await response.text());
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Usage with HTML file input
// <input type="file" id="fileInput" accept=".pdf" onchange="uploadDocument(this)">
```

## AI Agent Integration

This API is designed to be easily consumed by AI agents with the following features:

1. **Semantic Descriptions**: Each metadata field includes a description explaining its meaning
2. **Structured Responses**: Consistent JSON schemas for predictable parsing
3. **Actionable Items**: Pre-identified tasks ready for workflow automation
4. **Clear Error Handling**: Structured error responses with codes and details
5. **Filtering Options**: Query parameters for precise data retrieval

## Rate Limiting & Best Practices

- The API currently has no rate limiting, but consider implementing it for production
- Use the health endpoint to verify connectivity before making requests
- Cache document IDs for repeated metadata/actions queries
- Handle errors gracefully and check error codes for appropriate responses
- Consider pagination for large result sets in production deployments

## Setup Requirements

Before using the API, ensure:
1. **Environment Setup**: Python 3.9+ with required dependencies installed
2. **Environment Configuration**: Properly configured `.env` file with all required variables
3. **API Key Configuration**: Valid `GEMINI_API_KEY` in `.env` file
4. **Model Configuration**: Appropriate `GEMINI_MODEL` selection for your use case
5. **Server Running**: API server started with `python run_api.py`

### Quick Environment Setup

```bash
# 1. Create environment configuration
python create_env.py

# 2. Edit .env file with your actual API key
# Replace YOUR_GEMINI_API_KEY_HERE with your real API key

# 3. (Optional) Adjust model and other settings in .env file

# 4. Start the API server
python run_api.py
```

## Common API Issues & Solutions

### 1. Environment Configuration Issues

**Missing .env file:**
```
ValueError: GEMINI_API_KEY not found in .env file
```
**Solution**: Run `python create_env.py` to create the environment configuration file

**Invalid API Key:**
```json
{
  "code": "LLM_API_ERROR",
  "message": "Failed to get response from LLM API after multiple retries."
}
```
**Solutions**:
- Verify your Gemini API key is valid and has sufficient quota
- Check that API key in `.env` is not the placeholder value `YOUR_GEMINI_API_KEY_HERE`
- Ensure no extra spaces or quotes around the API key value

### 2. Model Configuration Issues

**Invalid Model Name:**
```
404 models/invalid-model is not found for API version v1beta
```
**Solution**: Use supported model names in `GEMINI_MODEL` environment variable:
- `gemini-1.5-flash` (recommended)
- `gemini-1.5-pro`
- `gemini-pro`

**Performance Issues:**
- For faster processing: Use `GEMINI_MODEL="gemini-1.5-flash"`
- For higher accuracy: Use `GEMINI_MODEL="gemini-1.5-pro"`
- Adjust `LLM_TEMPERATURE` for more focused (lower) or creative (higher) responses

### 3. File Upload Issues

**No file uploaded:**
```json
{
  "code": "INVALID_INPUT",
  "message": "No file uploaded. Please include a file in the 'file' field of the multipart/form-data request."
}
```
**Solution**: Use multipart/form-data with 'file' field, not JSON with base64

**Invalid file format:**
```json
{
  "code": "INVALID_INPUT",
  "message": "Only PDF files are supported."
}
```
**Solution**: Ensure uploaded files are valid PDF documents

### 4. Document Processing Issues

**PDF Reading Errors:**
```json
{
  "code": "DOCUMENT_PROCESSING_FAILED",
  "message": "Failed to read PDF file"
}
```
**Solution**: Ensure PDF files are not corrupted and contain extractable text (not just images)

**"Other" Document Classification:**
- Documents classified as "other" are not errors - this is expected for non-standard document types
- "Other" documents may have different metadata fields than predefined types
- Confidence scores for "other" documents are typically lower (0.3-0.8) - this is normal

### 5. JSON Response Parsing Issues (Fixed in latest version)

**Markdown-wrapped JSON:**
```json
{
  "code": "LLM_API_ERROR", 
  "message": "Failed to parse LLM classification response"
}
```
**Solution**: The API now automatically handles markdown-wrapped JSON responses

### 6. Performance and Caching Issues

**Slow API responses:**
- Check `CACHE_ENABLED="true"` in `.env` for faster repeated requests
- Consider using `gemini-1.5-flash` for faster processing
- Reduce `LLM_MAX_TOKENS` if responses are too long

**Cache not working:**
- Verify `CACHE_ENABLED="true"` in environment variables
- Check disk space for cache directory (`.cache/`)
- Ensure write permissions for cache directory

### 7. Import and Dependency Issues

**Missing dependencies:**
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

**Python version compatibility:**
```
SyntaxError: invalid syntax
```
**Solution**: Ensure you're using Python 3.9+ (`python --version`)

### Getting Help

1. **Check Environment**: Run `python create_env.py` to validate your configuration
2. **Check Logs**: Review `app.log` for detailed error information
3. **Test API Key**: Verify your Gemini API key works outside the application
4. **Check Quota**: Ensure your Gemini API has sufficient quota/credits
5. **Network**: Verify internet connectivity for LLM API calls

### Configuration Validation

```bash
# Test your environment configuration
python -c "
from config.settings import *
print(f'✅ API Key: {\"Set\" if GEMINI_API_KEY and GEMINI_API_KEY != \"YOUR_GEMINI_API_KEY_HERE\" else \"❌ Not set\"}')
print(f'✅ Model: {LLM_MODEL}')
print(f'✅ Temperature: {LLM_TEMPERATURE}')
print(f'✅ Max Tokens: {LLM_MAX_TOKENS}')
print(f'✅ Cache Enabled: {CACHE_ENABLED}')
"
```

---

# Part 3: Talking Points

## 1. Design Decisions Explained

### Modular Architecture
The system follows a clear separation of concerns with distinct modules:
- **Configuration Layer** (`config/`): Centralizes all settings, API keys, and document type definitions
- **Core Business Logic** (`core/`): Contains the main processing logic, LLM interface, and data models
- **API Layer** (`api/`): Handles HTTP requests and responses with proper error handling
- **Utilities** (`utils/`): Provides cross-cutting concerns like logging and exceptions

### Facade Pattern Implementation
The `DocumentProcessor` class acts as a facade, providing a simple interface for complex document processing operations:
- **Simplifies Client Interaction**: Clients only need to interact with one main class
- **Encapsulates Complexity**: Hides the complexity of PDF parsing, LLM calls, and caching
- **Promotes Loose Coupling**: Internal components can be modified without affecting clients
- **Enables Easy Testing**: Clear interface makes mocking and testing straightforward

### Pydantic Models for Data Validation
Using Pydantic ensures robust data handling:
- **Automatic Validation**: Input/output data is automatically validated against schemas
- **Clear API Contracts**: Well-defined data structures make the API predictable for AI agents
- **Type Safety**: Reduces runtime errors through compile-time type checking
- **Documentation**: Models serve as self-documenting API specifications

### Centralized Error Handling
Custom exceptions with Flask error handlers provide:
- **Consistent Error Responses**: All errors follow the same JSON format
- **Appropriate HTTP Status Codes**: Different error types return appropriate status codes
- **Detailed Error Information**: Structured error details help with debugging
- **Graceful Degradation**: System continues operating even when individual components fail

### Configuration-Driven Document Types
Document types are defined in configuration rather than hard-coded:
- **Extensibility**: New document types can be added without code changes
- **Maintainability**: Metadata fields and descriptions can be updated easily
- **Semantic Descriptions**: Each field includes AI-friendly descriptions
- **Flexible Processing**: Different document types can have different processing rules

### In-Memory Document Storage
For this assignment, processed documents are stored in memory:
- **Simplicity**: No database setup required for demonstration
- **Fast Access**: Immediate retrieval of processed documents
- **Production Note**: In production, this would be replaced with persistent storage (NoSQL/SQL)

## 2. Proposed AI-Powered Features for Factify

### Feature 1: Intelligent Contract Clause Comparison & Risk Assessment

**Description**: Allow users to upload two contract documents (or new versions of the same contract) and automatically identify differences in clauses, highlighting potential risks or deviations from standard legal language.

**Technical Approach**:
- **Metadata Leverage**: Utilize the `key_terms` extracted during initial contract processing
- **LLM for Comparison & Semantic Diff**:
  - Extract full text of relevant clauses from both documents
  - Prompt LLM: "Compare these two contract clauses and list all differences, then identify any terms that seem unusual or high-risk for a standard commercial agreement, explaining why."
  - Use few-shot examples of risky clauses if available
  - Employ structured JSON response for differences and risk flags
- **Visualization**: Present side-by-side comparison with highlighted differences and risk scores

**Business Value**:
- **Accelerated Contract Review**: Reduces time legal teams spend on manual contract comparison
- **Risk Mitigation**: Automatically flags potentially problematic clauses
- **Improved Compliance**: Ensures contracts align with internal standards and policies
- **Cost Savings**: Reduces reliance on extensive manual legal review hours

**Implementation Considerations**:
- New API endpoint: `POST /documents/compare` accepting two document IDs
- Enhanced risk assessment using legal domain-specific prompts
- Integration with legal clause databases for standard comparisons

### Feature 2: Automated Workflow Triggering and Intelligent Routing

**Description**: Based on extracted document metadata and actionable items, automatically trigger workflows in other business systems (ERP, CRM) or intelligently route documents/tasks to appropriate departments/personnel.

**Technical Approach**:
- **Event-Driven Architecture**: After document processing, publish events containing `DocumentResult`
- **Rule Engine/LLM for Decision Making**:
  - Evaluate `DocumentResult` (document type, amount, due date, vendor, etc.)
  - Example rule: "If document.type is 'invoice' AND metadata.amount > $5000 AND metadata.vendor is 'CloudProviderX', then trigger 'HighValueInvoiceApproval' workflow"
  - LLM for intelligent routing: "Based on this document's content and metadata, which department (Finance, Legal, Sales, HR) should be notified for review?"
- **Integration Layer**: Use webhooks/APIs to integrate with external systems
  - Jira for task creation
  - Salesforce for CRM updates
  - ERP systems for payment initiation
  - Slack/Teams for notifications

**Business Value**:
- **Increased Operational Efficiency**: Automates repetitive tasks, reducing manual intervention
- **Faster Processing Cycles**: Documents move through workflows quicker
- **Improved Accuracy**: Reduces errors from manual data entry and routing
- **Better Resource Utilization**: Frees employees for higher-value activities

**Implementation Considerations**:
- Event system using message queues (Redis/RabbitMQ)
- Configurable workflow rules in database
- API integrations with common business systems
- Audit trail for all automated actions

## 3. Production Considerations

### Handling LLM API Failures

**Current Implementations**:
- ✅ **Retry Logic with Exponential Backoff**: Implemented in `LLMInterface._call_gemini_api` with 3 retries and exponential backoff
- ✅ **Graceful Fallback Mechanisms**: 
  - If classification fails, document is marked as "unknown" with partial processing
  - If metadata extraction fails for specific fields, returns null values rather than failing entirely
  - System logs warnings and continues processing when possible

**Future Enhancements**:
- **Circuit Breaker Pattern**: If LLM service consistently fails, temporarily stop requests to allow recovery
- **Fallback to Rule-Based Processing**: For classification, fall back to keyword matching if LLM fails
- **Asynchronous Processing & Queues**: 
  - `POST /documents/analyze` returns 202 Accepted with processing ID
  - Actual processing happens asynchronously using Celery + Redis/RabbitMQ
  - Clients poll `GET /documents/{id}` for status and results
- **Health Monitoring**: Implement comprehensive monitoring for LLM API latency, error rates, and availability

### Simple Caching Strategy to Reduce API Calls

**Current Implementation**:
- **File-Based Caching**: LLM responses cached in `.cache/` directory using MD5 hash keys
- **Cache Key Generation**: Based on prompt content and JSON schema for consistent hashing
- **Automatic Expiration**: Configurable expiration time (default 1 hour) ensures data freshness
- **Cache Pruning**: Automatic cleanup of expired cache files on initialization

**Benefits Achieved**:
- **Reduced API Costs**: Fewer calls to Gemini API, directly lowering operational expenses
- **Improved Latency**: Faster response times for repeated or similar queries
- **Rate Limit Avoidance**: Reduces traffic to LLM provider's API

**Production Enhancements**:
- **Distributed Caching**: Replace file-based cache with Redis for multi-instance deployments
- **Cache Warming**: Pre-populate cache with common document patterns
- **Cache Analytics**: Monitor cache hit rates and optimize key generation strategies
- **Intelligent Cache Invalidation**: Smart invalidation based on document types and content changes

### Cost Estimation Per Document Processing

**Current Calculation** (based on Gemini 1.5-flash pricing):

**Assumptions**:
- Average document: 5 pages, 2000 characters per page = 10,000 characters
- 10000 characters / 4 characters per token = 2500 tokens
- Two LLM calls per document: classification + metadata extraction
- Input pricing: $0.075 per 1M tokens
- Output pricing: $0.15 per 1M tokens

**Detailed Breakdown**:

1. **Classification Call**:
   - Input: 2500 tokens (document + instructions) = $0.075 * 2500 / 1000000 = $0.0001875
   - Output: 100 chars -> 25 tokens (JSON response) = $0.15 * 25 / 1000000 = $0.00000375
   - **Subtotal**: $0.00019125

2. **Metadata Extraction Call**:
   - Input: 2500 tokens (document + instructions) = $0.075 * 2500 / 1000000 = $0.0001875
   - Output: 500 chars -> 125 tokens (JSON response) = $0.15 * 125 / 1000000 = $0.00001875
   - **Subtotal**: $0.00020625

**Total Estimated Cost**: $0.0003975 per document

**Important Considerations**:
- **Caching Impact**: With 50% cache hit rate, effective cost drops to ~$0.000198 per document
- **Model Variations**: Different Gemini models have different pricing structures
- **Document Size Variance**: Larger documents (legal contracts, reports) will cost proportionally more
- **Token Limits**: Very large documents may require chunking, increasing costs
- **Infrastructure Costs**: Additional costs for compute, storage, and network resources not included
- **Error Retries**: Failed calls with retries will incur additional costs (typically <5% overhead)

**Cost Optimization Strategies**:
- **Effective Caching**: Current file-based cache can reduce costs by 30-70%
- **Document Preprocessing**: Remove unnecessary content before LLM processing
- **Model Selection**: Use most cost-effective model for each task type
- **Batch Processing**: Group similar documents for more efficient processing
- **Smart Chunking**: Optimize text chunking strategies for large documents

**Monitoring & Budgeting**:
- Implement cost tracking per document type and processing volume
- Set up alerts for unusual cost spikes
- Regular analysis of cache effectiveness and model performance
- Monthly cost projections based on document processing volumes 