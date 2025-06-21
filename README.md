# Factify - Intelligent Document Understanding & AI-Ready API

An AI-powered system that understands business documents, extracts intelligent metadata, and exposes this metadata through a well-designed, AI-friendly API.

## Features

- **Document Classification**: Automatically classifies documents (invoices, contracts, reports, and other document types) using Google Gemini AI
- **Smart "Other" Classification**: Dynamically handles unknown document types with intelligent metadata extraction
- **Metadata Extraction**: Extracts semantic metadata specific to each document type
- **AI-Friendly API**: RESTful API designed for AI agent consumption with semantic descriptions
- **Raw File Upload**: Direct PDF file upload via multipart/form-data (no base64 encoding required)
- **Actionable Items**: Identifies and extracts actionable tasks from documents
- **Configurable LLM Models**: Environment-based Gemini model selection and configuration
- **Caching System**: Reduces API costs with intelligent response caching
- **Robust Error Handling**: Comprehensive error handling and logging
- **Modular Architecture**: Clean separation of concerns with facade pattern

## Project Structure

```
factify_v2/
├── .env                      # Environment variables (create from template)
├── env_template.txt          # Environment variables template
├── create_env.py             # Helper script to create .env file
├── main.py                   # Command-line document processing entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── api_docs.md               # Detailed API documentation
├── config/
│   ├── __init__.py
│   └── settings.py           # Application configuration
├── core/
│   ├── __init__.py
│   ├── document_processor.py # Main document processing facade
│   ├── llm_interface.py      # Google Gemini AI integration
│   ├── cache_manager.py      # LLM response caching
│   └── models.py             # Pydantic data models
├── api/
│   ├── __init__.py
│   ├── app.py                # Flask application setup
│   └── routes.py             # API endpoint definitions
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Logging configuration
│   └── exceptions.py         # Custom exceptions and error handling
├── tests/
│   └── __init__.py
├── output/                   # Processed document results
└── documents_to_process/     # Input directory for documents
```

## Setup Instructions

### 1. Environment Setup

Create a conda environment:
```bash
conda create -n factify python=3.9 -y
conda activate factify
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

**Option 1: Use the Helper Script (Recommended)**
```bash
python create_env.py
```

**Option 2: Manual Setup**
Create a `.env` file with your configuration:
```bash
# Copy content from env_template.txt to .env
cp env_template.txt .env
# Then edit .env with your actual values
```

**Required Environment Variables:**
```bash
# --- API Keys ---
GEMINI_API_KEY="your_actual_gemini_api_key_here"

# --- LLM Configuration ---
GEMINI_MODEL="gemini-1.5-flash"        # or gemini-1.5-pro, gemini-pro
LLM_TEMPERATURE="0.3"                  # 0.0-1.0, lower = more focused
LLM_MAX_TOKENS="1024"                  # Maximum response length

# --- Caching Configuration ---
CACHE_ENABLED="true"                   # Enable/disable caching
CACHE_EXPIRATION_TIME_SECONDS="3600"  # Cache expiration (1 hour)
```

**Important**: 
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Replace `"your_actual_gemini_api_key_here"` with your real API key
3. The `.env` file is automatically gitignored for security

**Available Gemini Models:**
- `gemini-1.5-flash` - Fast, cost-effective (recommended)
- `gemini-1.5-pro` - More capable, higher cost
- `gemini-pro` - Legacy model

### 4. Add Sample Documents

Place PDF documents in the `documents_to_process/` directory for processing.

## Usage

### Command Line Processing (Part 1)

Process all documents in the input directory:
```bash
python main.py
```

Process a specific document:
```bash
python main.py --document path/to/your/document.pdf
```

Results will be saved as JSON files in the `output/` directory.

### API Server (Part 2)

Start the Flask API server:
```bash
python run_api.py
```

The API will be available at `http://127.0.0.1:5000`

**Note**: Ensure your `.env` file contains a valid `GEMINI_API_KEY` before starting the server.

#### API Endpoints

1. **Health Check**
   ```
   GET /health
   ```

2. **Analyze Document** (Raw File Upload)
   ```bash
   # Using curl
   curl -X POST http://127.0.0.1:5000/documents/analyze \
     -F "file=@path/to/your/document.pdf"
   ```
   
   ```python
   # Using Python requests
   import requests
   
   with open('invoice.pdf', 'rb') as file:
       files = {'file': ('invoice.pdf', file, 'application/pdf')}
       response = requests.post('http://127.0.0.1:5000/documents/analyze', files=files)
   ```

3. **Get Document Metadata**
   ```
   GET /documents/{document_id}
   ```

4. **Get Actionable Items**
   ```
   GET /documents/{document_id}/actions?status=pending&priority=high
   ```

See `api_docs.md` for detailed API documentation with examples.

## Supported Document Types

- **Invoices**: Extracts vendor, amount, due date, line items
- **Contracts**: Extracts parties, effective date, termination date, key terms
- **Reports**: Extracts reporting period, key metrics, executive summary
- **Other Documents**: Dynamically extracts relevant metadata for letters, memos, presentations, manuals, forms, and other business documents

### Dynamic "Other" Document Handling

For documents that don't fit the predefined categories, the system:
1. **Smart Classification**: Automatically classifies unknown documents as "other"
2. **Dynamic Analysis**: LLM analyzes the document to identify the most relevant metadata fields
3. **Intelligent Extraction**: Extracts metadata for both standard fields (title, author, date) and document-specific fields
4. **Actionable Items**: Generates meaningful actionable items even for generic documents

## Architecture Design Decisions

### 1. Modular Architecture
- **Separation of Concerns**: Each module has a specific responsibility
- **Facade Pattern**: `DocumentProcessor` provides a simple interface for complex operations
- **Dependency Injection**: Components are loosely coupled and easily testable

### 2. Error Handling Strategy
- **Custom Exceptions**: Specific exceptions for different error types
- **Centralized Error Handling**: Flask error handlers provide consistent API responses
- **Graceful Degradation**: Partial processing when possible, with clear error messages

### 3. Caching Strategy
- **File-based Cache**: Simple, persistent caching of LLM responses
- **Hash-based Keys**: Unique cache keys based on prompt and schema
- **Automatic Expiration**: Configurable cache expiration to ensure data freshness

### 4. AI-Friendly Design
- **Semantic Descriptions**: Metadata fields include descriptions for AI agents
- **Structured Output**: Consistent JSON schemas for predictable parsing
- **Actionable Items**: Extracted tasks ready for workflow automation

### 5. Flexible Configuration
- **Environment-Based Settings**: Model and parameters configurable via environment variables
- **Model Selection**: Easy switching between different Gemini models
- **Runtime Configuration**: No code changes needed for different environments

## Proposed AI-Powered Features

### 1. Intelligent Contract Clause Comparison & Risk Assessment
- **Purpose**: Compare contract versions and identify risks automatically
- **Technical Approach**: LLM-powered semantic diff and risk analysis
- **Business Value**: Faster legal review, risk mitigation, cost savings

### 2. Automated Workflow Triggering and Intelligent Routing
- **Purpose**: Auto-trigger business workflows based on document content
- **Technical Approach**: Rule engine + LLM for intelligent decision making
- **Business Value**: Increased efficiency, faster processing, better resource utilization

## Production Considerations

### LLM API Failure Handling
- ✅ Retry logic with exponential backoff (3 retries with 2^n second delays)
- ✅ Proper Gemini API integration using `genai.types.GenerationConfig()`
- ✅ Graceful fallback mechanisms (partial processing on classification failure)
- ✅ Dynamic metadata extraction for unknown document types
- ✅ Comprehensive error logging and structured exception handling
- ✅ Automatic JSON response cleanup (handles markdown-wrapped responses)
- 🔄 Circuit breaker pattern (future enhancement)
- 🔄 Asynchronous processing queues (future enhancement)

### Caching Strategy
- ✅ File-based response caching with configurable expiration
- ✅ Automatic cache pruning on startup
- ✅ Environment-configurable cache settings
- **Benefits**: Reduced API costs, improved latency, rate limit avoidance

### Cost Estimation (Per Document)
Based on Gemini 1.5 Flash pricing (subject to change):
- **Average Document**: 2 LLM calls (classification + metadata extraction)
- **Input Cost**: $0.00020625 (20K chars average)
- **Output Cost**: $0.0000225 (600 chars average)
- **Total Estimate**: $0.0003975 per document
- **With Caching**: ~$0.000198 per document (50% cache hit rate)

*Note: "Other" documents may have slightly higher costs due to dynamic analysis, but caching significantly reduces repeat processing costs.*

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Document Types
1. Update `DOCUMENT_TYPES` in `config/settings.py`
2. Add corresponding Pydantic models in `core/models.py`
3. Update actionable item logic in `core/document_processor.py`

### Changing LLM Configuration
Update your `.env` file and restart the application:
```bash
# Switch to more powerful model
GEMINI_MODEL="gemini-1.5-pro"

# Adjust creativity (0.0 = focused, 1.0 = creative)
LLM_TEMPERATURE="0.3"

# Increase response length
LLM_MAX_TOKENS="2048"
```

### Logging
- Console and file logging configured
- Logs saved to `app.log`
- Configurable log levels

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   ValueError: GEMINI_API_KEY not found in .env file
   ```
   **Solution**: Run `python create_env.py` or create `.env` file with your Gemini API key

2. **Invalid API Key Placeholder**
   ```
   LLMAPIError: Failed to get response from LLM API after multiple retries
   ```
   **Solution**: Replace `"YOUR_GEMINI_API_KEY_HERE"` in `.env` with your actual API key

3. **File Upload Issues**
   ```
   InvalidInputError: No file uploaded
   ```
   **Solution**: Use multipart/form-data with 'file' field, not JSON with base64

4. **Invalid Gemini Model Name**
   ```
   404 models/MODEL_NAME is not found
   ```
   **Solution**: Use supported model names in `GEMINI_MODEL` environment variable

5. **JSON Response Parsing Error** (Fixed in latest version)
   ```
   Failed to parse LLM classification response
   ```
   **Solution**: Automatic cleanup of markdown-wrapped JSON responses now implemented

6. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'google.generativeai'
   ```
   **Solution**: Install dependencies with `pip install -r requirements.txt`

7. **PDF Processing Errors**
   ```
   DocumentProcessingError: Failed to read PDF file
   ```
   **Solution**: Ensure PDF files are not corrupted and are text-extractable

### Getting Help

- Check the logs in `app.log` for detailed error information
- Ensure all dependencies are installed correctly
- Verify your Gemini API key is valid and has sufficient quota
- Use `python create_env.py` to verify your environment configuration

## License

This project is created for the Factify recruitment assignment. 