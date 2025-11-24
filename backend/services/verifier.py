"""
Verification service: compares submitted fields with extracted fields using fuzzy matching.
Uses rapidfuzz for fast and accurate fuzzy matching.
"""

from typing import Dict, List, Tuple, Optional
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger("verifier")

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logger.warning("rapidfuzz not available, falling back to difflib")
    from difflib import SequenceMatcher


def fuzzy_match(str1: Optional[str], str2: Optional[str]) -> float:
    """
    Calculate fuzzy match score between two strings using rapidfuzz.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Match score (0.0 to 1.0)
    """
    if str1 is None or str2 is None:
        return 0.0
    
    str1 = str(str1).lower().strip()
    str2 = str(str2).lower().strip()
    
    if str1 == str2:
        return 1.0
    
    if not str1 or not str2:
        return 0.0
    
    # Use rapidfuzz if available, otherwise fall back to SequenceMatcher
    if RAPIDFUZZ_AVAILABLE:
        ratio = fuzz.ratio(str1, str2) / 100.0
    else:
        ratio = SequenceMatcher(None, str1, str2).ratio()
    
    # Also check for substring matches
    if str1 in str2 or str2 in str1:
        ratio = max(ratio, 0.85)
    
    return ratio


def verify_fields(
    submitted_fields: Dict[str, Optional[str]],
    extracted_fields: Dict[str, Optional[str]]
) -> Dict:
    """
    Verify submitted fields against extracted fields.
    
    Args:
        submitted_fields: User-submitted fields (can contain None or empty values)
        extracted_fields: Fields extracted from OCR
        
    Returns:
        Dict with verification results:
        - matches: dict of field -> match score
        - mismatches: list of mismatched fields
        - overall_score: overall verification score
    """
    matches = {}
    mismatches = []
    
    # Filter out None and empty values from submitted fields for verification
    valid_submitted_fields = {
        k: v for k, v in submitted_fields.items() 
        if v is not None and str(v).strip() != ""
    }
    
    if not valid_submitted_fields:
        return {
            "matches": {},
            "mismatches": [],
            "overall_score": 0.0,
            "verification_passed": False,
            "error": "No valid fields submitted for verification"
        }
    
    for field_name in valid_submitted_fields.keys():
        submitted_value = str(valid_submitted_fields.get(field_name, "")).strip()
        extracted_value = extracted_fields.get(field_name)
        
        if extracted_value:
            extracted_value = str(extracted_value).strip()
        else:
            extracted_value = ""
        
        match_score = fuzzy_match(submitted_value, extracted_value)
        matches[field_name] = match_score
        
        # Threshold for mismatch (adjustable)
        if match_score < 0.8:
            mismatches.append({
                "field": field_name,
                "submitted": submitted_value,
                "extracted": extracted_value,
                "match_score": match_score
            })
    
    # Calculate overall score
    if matches:
        overall_score = sum(matches.values()) / len(matches)
    else:
        overall_score = 0.0
    
    return {
        "matches": matches,
        "mismatches": mismatches,
        "overall_score": overall_score,
        "verification_passed": overall_score >= 0.85 and len(mismatches) == 0
    }


