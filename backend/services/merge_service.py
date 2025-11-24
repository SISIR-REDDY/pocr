"""
Service to merge TrOCR results with optional fallback results.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def merge_results(
    trocr_fields: Dict[str, Optional[str]],
    trocr_confidence: float,
    fallback_fields: Optional[Dict[str, Optional[str]]] = None,
    field_confidences: Optional[Dict[str, float]] = None
) -> Dict[str, Optional[str]]:
    """
    Merge TrOCR and fallback results based on confidence thresholds.
    
    Rules:
    - If trocr_conf >= 0.75: keep OCR result
    - Else if fallback exists: use fallback
    - Else: normalize OCR result
    
    Args:
        trocr_fields: Fields extracted from TrOCR
        trocr_confidence: TrOCR confidence score
        fallback_fields: Optional fallback fields
        field_confidences: Optional field-level confidences
        
    Returns:
        Merged fields dict
    """
    if trocr_confidence >= 0.75:
        logger.info("Using TrOCR results (high confidence)")
        return trocr_fields
    
    if fallback_fields:
        logger.info("Using fallback results (low TrOCR confidence)")
        # Merge: prefer fallback for empty/missing fields
        merged = {}
        for key in trocr_fields.keys():
            trocr_val = trocr_fields.get(key)
            fallback_val = fallback_fields.get(key)
            
            # Use fallback if TrOCR is empty or confidence is low
            if not trocr_val or trocr_val.strip() == "":
                merged[key] = fallback_val
            elif field_confidences and field_confidences.get(key, 0) < 0.65:
                merged[key] = fallback_val if fallback_val else trocr_val
            else:
                merged[key] = trocr_val
        
        return merged
    
    # Normalize OCR result (keep as-is)
    logger.info("Normalizing TrOCR results (no fallback)")
    return trocr_fields


