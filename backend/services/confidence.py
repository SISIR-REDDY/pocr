"""
Confidence calculation for extracted fields and overall document.
"""

from typing import Dict, Optional, List


def calculate_field_confidence(field_value: Optional[str], field_type: str) -> float:
    """
    Calculate confidence for a single field.
    
    Args:
        field_value: Extracted field value
        field_type: Type of field (name, age, etc.)
        
    Returns:
        Confidence score (0.0 to 1.0)
    """
    if field_value is None or field_value.strip() == "":
        return 0.0
    
    # Base confidence based on field type
    base_confidences = {
        "name": 0.7,
        "age": 0.8,
        "gender": 0.75,
        "phone": 0.85,
        "email": 0.9,
        "address": 0.65
    }
    
    base = base_confidences.get(field_type, 0.7)
    
    # Adjust based on value quality
    if field_type == "email":
        if "@" in field_value and "." in field_value:
            return min(0.95, base + 0.1)
    
    if field_type == "phone":
        digits = sum(c.isdigit() for c in field_value)
        if 10 <= digits <= 15:
            return min(0.95, base + 0.1)
    
    if field_type == "age":
        try:
            age = int(field_value)
            if 1 <= age <= 150:
                return min(0.95, base + 0.1)
        except:
            pass
    
    if field_type == "name":
        words = field_value.split()
        if len(words) >= 2:
            return min(0.9, base + 0.1)
    
    return base


def calculate_document_confidence(
    fields: Dict[str, Optional[str]],
    ocr_confidence: float,
    field_confidences: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate overall document confidence.
    
    Args:
        fields: Extracted fields dict
        ocr_confidence: OCR model confidence
        field_confidences: Optional pre-calculated field confidences
        
    Returns:
        Overall confidence score (0.0 to 1.0)
    """
    if field_confidences is None:
        field_confidences = {
            k: calculate_field_confidence(v, k)
            for k, v in fields.items()
        }
    
    # Weighted average
    # OCR confidence: 40%
    # Field extraction: 60%
    
    field_avg = sum(field_confidences.values()) / len(field_confidences) if field_confidences else 0.0
    
    # Count how many fields were extracted
    extracted_count = sum(1 for v in fields.values() if v is not None and v.strip() != "")
    total_fields = len(fields)
    extraction_rate = extracted_count / total_fields if total_fields > 0 else 0.0
    
    # Combine: OCR confidence, field confidence, extraction rate
    overall = (
        ocr_confidence * 0.4 +
        field_avg * 0.4 +
        extraction_rate * 0.2
    )
    
    return min(1.0, max(0.0, overall))


def get_field_confidences(fields: Dict[str, Optional[str]]) -> Dict[str, float]:
    """
    Get confidence scores for all fields.
    
    Args:
        fields: Extracted fields dict
        
    Returns:
        Dict mapping field names to confidence scores
    """
    return {
        k: calculate_field_confidence(v, k)
        for k, v in fields.items()
    }


