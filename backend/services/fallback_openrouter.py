"""
OpenRouter fallback service for OCR text cleanup and correction.
Only used when confidence is low and fallback is enabled.
"""

import os
import json
import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def cleanup_with_openrouter(
    raw_text: str,
    api_key: Optional[str] = None
) -> Optional[Dict[str, str]]:
    """
    Use OpenRouter API to clean and correct OCR text.
    
    Args:
        raw_text: Raw OCR text
        api_key: OpenRouter API key (from env)
        
    Returns:
        Dict with cleaned fields or None if failed
    """
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.warning("OpenRouter API key not found")
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""Clean and correct the following OCR text. Extract and output ONLY the following fields in strict JSON format:
{{
  "name": "",
  "age": "",
  "gender": "",
  "address": "",
  "phone": "",
  "email": ""
}}

OCR Text:
{raw_text}

Rules:
- Extract only information that is clearly present in the text
- Do not hallucinate or invent information
- If a field is not found, use empty string ""
- Output ONLY valid JSON, no other text
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",  # Cost-effective model
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # Extract JSON from response (might have markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        fields = json.loads(content)
        
        # Validate structure
        required_fields = ["name", "age", "gender", "address", "phone", "email"]
        cleaned_fields = {}
        for field in required_fields:
            cleaned_fields[field] = fields.get(field, "") or None
        
        logger.info("OpenRouter fallback successful")
        return cleaned_fields
        
    except Exception as e:
        logger.error(f"OpenRouter fallback failed: {e}")
        return None


