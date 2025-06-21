import google.generativeai as genai
import json
import time
from typing import Dict, Any, Optional, List
from config.settings import GEMINI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, CACHE_ENABLED
from utils.logger import setup_logging
from utils.exceptions import LLMAPIError
from core.cache_manager import CacheManager

logger = setup_logging(__name__)

class LLMInterface:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(LLM_MODEL)
        self.cache_manager = CacheManager()

    def _call_gemini_api(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> str:
        """
        Internal method to call the Gemini API with retry logic and caching.
        Handles API failures gracefully.
        """
        # Generate a cache key from the prompt and schema
        cache_key = self.cache_manager.generate_cache_key(prompt, schema)

        # Check cache first
        if CACHE_ENABLED:
            cached_response = self.cache_manager.get(cache_key)
            if cached_response:
                logger.info("LLM response retrieved from cache.")
                return cached_response

        retries = 3
        for i in range(retries):
            try:
                # Prepare generation config
                generation_config = genai.types.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                    max_output_tokens=LLM_MAX_TOKENS
                )
                
                # If schema is provided, add JSON response format to prompt and configure for JSON
                if schema:
                    prompt_with_schema = f"{prompt}\n\nPlease respond with valid JSON only."
                    response = self.model.generate_content(prompt_with_schema, generation_config=generation_config)
                else:
                    response = self.model.generate_content(prompt, generation_config=generation_config)

                # Access the text from the response
                if response and response.text:
                    response_text = response.text
                    if CACHE_ENABLED:
                        self.cache_manager.set(cache_key, response_text)
                    return response_text
                else:
                    raise LLMAPIError(f"LLM API returned an empty response")

            except Exception as e:
                logger.warning(f"LLM API call failed (attempt {i+1}/{retries}): {e}")
                if i < retries - 1:
                    time.sleep(2 ** i)  # Exponential backoff
                else:
                    raise LLMAPIError("Failed to get response from LLM API after multiple retries.", original_error=e)

    def _clean_json_response(self, response: str) -> str:
        """
        Clean up LLM response by removing markdown code blocks and extra whitespace.
        """
        # Remove markdown code blocks
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]  # Remove ```json
        elif response.startswith('```'):
            response = response[3:]   # Remove ```
        
        if response.endswith('```'):
            response = response[:-3]  # Remove trailing ```
        
        return response.strip()

    def classify_document(self, text_content: str, document_types: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses LLM for zero-shot or few-shot document type classification.
        Returns the document type and confidence score.
        """
        # Separate "other" from specific types for better prompt construction
        specific_types = [t for t in document_types.keys() if t != "other"]
        specific_types_str = ", ".join(specific_types)
        
        prompt = (
            f"Classify the following document content into one of these specific types: {specific_types_str}, "
            f"or 'other' if it doesn't clearly fit any of the specific categories.\n\n"
            f"Guidelines:\n"
            f"- Choose a specific type only if the document clearly matches that category\n"
            f"- Use 'other' for documents like letters, memos, presentations, manuals, forms, or any general business documents\n"
            f"- Provide high confidence (0.8+) for clear matches, medium confidence (0.5-0.7) for likely matches, "
            f"and lower confidence (0.3-0.5) for uncertain classifications\n\n"
            f"Provide your answer as a JSON object with 'type' and 'confidence' (0.0 to 1.0).\n\n"
            f"Document Content:\n```\n{text_content[:2000]}...\n```"
        )

        # Define the JSON schema for classification response
        classification_schema = {
            "type": "OBJECT",
            "properties": {
                "type": {"type": "STRING"},
                "confidence": {"type": "NUMBER"}
            },
            "required": ["type", "confidence"]
        }

        try:
            raw_response = self._call_gemini_api(prompt, schema=classification_schema)
            # Clean up response - remove markdown code blocks if present
            cleaned_response = self._clean_json_response(raw_response)
            classification_data = json.loads(cleaned_response)
            # Basic validation
            if "type" not in classification_data or "confidence" not in classification_data:
                raise ValueError("LLM classification response missing 'type' or 'confidence'.")
            if classification_data["confidence"] < 0 or classification_data["confidence"] > 1:
                 logger.warning(f"LLM returned out-of-range confidence: {classification_data['confidence']}. Clamping to [0,1].")
                 classification_data["confidence"] = max(0.0, min(1.0, classification_data["confidence"]))

            # Handle unknown types by defaulting to "other"
            if classification_data["type"] not in document_types:
                logger.info(f"LLM classified document as unrecognized type '{classification_data['type']}'. Defaulting to 'other'.")
                classification_data["type"] = "other"
                classification_data["confidence"] = max(0.3, min(0.6, classification_data["confidence"]))  # Moderate confidence for fallback

            logger.info(f"Document classified as: {classification_data['type']} with confidence: {classification_data['confidence']:.2f}")
            return classification_data
        except (json.JSONDecodeError, ValueError) as e:
            raise LLMAPIError(f"Failed to parse LLM classification response: {e}. Raw response: {raw_response}", original_error=e)
        except LLMAPIError:
            raise # Re-raise LLMAPIError from _call_gemini_api

    def extract_metadata(self, text_content: str, doc_type: str, metadata_fields: List[str]) -> Dict[str, Any]:
        """
        Uses LLM to extract semantic metadata based on document type.
        Handles cases where expected fields might be missing gracefully by LLM.
        """
        field_list_str = ", ".join(metadata_fields)
        prompt = (
            f"Extract the following key information from the {doc_type} document content provided: "
            f"{field_list_str}. "
            f"Provide your answer as a JSON object. For each field, provide the extracted value. "
            f"If a field is not found, include it with a null value. "
            f"Document Content:\n```\n{text_content[:4000]}...\n```" # Adjust as needed for token limits
        )

        # Dynamically create JSON schema for metadata extraction
        metadata_schema = {
            "type": "OBJECT",
            "properties": {field: {"type": "STRING"} for field in metadata_fields},
            "required": [] # No fields are strictly required, LLM should return null if not found
        }
        # Special handling for 'line_items' if it's an expected field (example)
        if "line_items" in metadata_fields:
            metadata_schema["properties"]["line_items"] = {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "description": {"type": "STRING"},
                        "quantity": {"type": "NUMBER"},
                        "unit_price": {"type": "NUMBER"},
                        "total": {"type": "NUMBER"}
                    },
                    "required": ["description"] # Example: only description is always required for line items
                }
            }


        try:
            raw_response = self._call_gemini_api(prompt, schema=metadata_schema)
            # Clean up response - remove markdown code blocks if present
            cleaned_response = self._clean_json_response(raw_response)
            extracted_data = json.loads(cleaned_response)

            # Ensure all expected fields are present, even if null, for consistency
            for field in metadata_fields:
                extracted_data.setdefault(field, None)

            logger.info(f"Extracted metadata for {doc_type}: {extracted_data}")
            return extracted_data
        except (json.JSONDecodeError, ValueError) as e:
            raise LLMAPIError(f"Failed to parse LLM metadata extraction response: {e}. Raw response: {raw_response}", original_error=e)
        except LLMAPIError:
            raise # Re-raise LLMAPIError from _call_gemini_api

    def extract_dynamic_metadata_for_other(self, text_content: str) -> Dict[str, Any]:
        """
        For 'other' document types, first identify the most relevant metadata fields,
        then extract them. This provides more intelligent metadata extraction for unknown document types.
        """
        # First, ask the LLM to identify relevant metadata fields
        analysis_prompt = (
            f"Analyze this document and identify the 3-5 most important pieces of information "
            f"that should be extracted as metadata. Consider things like: titles, authors, dates, "
            f"key topics, purposes, important names, deadlines, or other significant details.\n\n"
            f"Respond with a JSON object containing:\n"
            f"1. 'suggested_fields': a list of field names that would be most valuable to extract\n"
            f"2. 'document_summary': a brief 1-2 sentence summary of what this document is about\n\n"
            f"Document Content:\n```\n{text_content[:3000]}...\n```"
        )

        analysis_schema = {
            "type": "OBJECT",
            "properties": {
                "suggested_fields": {"type": "ARRAY", "items": {"type": "STRING"}},
                "document_summary": {"type": "STRING"}
            },
            "required": ["suggested_fields", "document_summary"]
        }

        try:
            # Get field suggestions
            raw_analysis = self._call_gemini_api(analysis_prompt, schema=analysis_schema)
            cleaned_analysis = self._clean_json_response(raw_analysis)
            analysis_data = json.loads(cleaned_analysis)
            
            suggested_fields = analysis_data.get("suggested_fields", [])
            document_summary = analysis_data.get("document_summary", "")
            
            # Limit to reasonable number of fields and add our standard ones
            standard_fields = ["document_title", "author", "date_created", "subject"]
            all_fields = list(set(standard_fields + suggested_fields[:4]))  # Limit suggested fields
            
            logger.info(f"Dynamic metadata extraction for 'other' document. Fields: {all_fields}")
            
            # Now extract metadata for the identified fields
            extraction_prompt = (
                f"Extract the following information from this document: {', '.join(all_fields)}.\n\n"
                f"Provide your answer as a JSON object. For each field, provide the extracted value. "
                f"If a field is not found or not applicable, include it with a null value.\n\n"
                f"Additional context: {document_summary}\n\n"
                f"Document Content:\n```\n{text_content[:4000]}...\n```"
            )

            extraction_schema = {
                "type": "OBJECT",
                "properties": {field: {"type": "STRING"} for field in all_fields},
                "required": []
            }

            raw_extraction = self._call_gemini_api(extraction_prompt, schema=extraction_schema)
            cleaned_extraction = self._clean_json_response(raw_extraction)
            extracted_data = json.loads(cleaned_extraction)

            # Ensure all fields are present
            for field in all_fields:
                extracted_data.setdefault(field, None)
            
            # Add the document summary as metadata
            extracted_data["document_summary"] = document_summary
            
            logger.info(f"Dynamic metadata extraction completed for 'other' document: {extracted_data}")
            return extracted_data

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Dynamic metadata extraction failed, falling back to standard fields: {e}")
            # Fallback to standard extraction
            return self.extract_metadata(text_content, "other", ["document_title", "author", "date_created", "subject"])
        except LLMAPIError as e:
            logger.warning(f"LLM API error during dynamic extraction, falling back: {e}")
            # Fallback to standard extraction
            return self.extract_metadata(text_content, "other", ["document_title", "author", "date_created", "subject"]) 