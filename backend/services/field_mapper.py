"""
Field extraction from OCR text using improved regex and keyword rules.
Enhanced with OCR error correction and flexible patterns.
Supports multilingual extraction: English, Hindi (Devanagari), Arabic.
Extracts: name, age, gender, phone, email, address.
"""

import re
from typing import Dict, Optional, List
import sys
import os

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger
from utils.language_detector import detect_language

logger = setup_logger("field_mapper")

# Multilingual keywords
NAME_KEYWORDS = {
    'en': ['name', 'full name', 'applicant name', 'your name', 'first name', 'last name'],
    'hi': ['नाम', 'पूरा नाम', 'आवेदक का नाम', 'आपका नाम'],
    'ar': ['الإسم', 'الاسم الكامل', 'اسم مقدم الطلب', 'اسمك']
}

ADDRESS_KEYWORDS = {
    'en': ['address', 'residence', 'location', 'addr', 'street', 'city', 'state', 'country'],
    'hi': ['पता', 'निवास', 'स्थान', 'शहर', 'राज्य', 'देश'],
    'ar': ['العنوان', 'السكن', 'الموقع', 'المدينة', 'الدولة', 'البلد']
}

EMAIL_KEYWORDS = {
    'en': ['email', 'e-mail', 'mail'],
    'hi': ['ईमेल', 'मेल'],
    'ar': ['البريد', 'البريد الإلكتروني', 'إيميل']
}

PHONE_KEYWORDS = {
    'en': ['phone', 'mobile', 'tel', 'contact', 'ph'],
    'hi': ['फोन', 'मोबाइल', 'संपर्क', 'टेलीफोन'],
    'ar': ['الهاتف', 'الجوال', 'التليفون', 'اتصل']
}

GENDER_KEYWORDS = {
    'en': ['gender', 'sex'],
    'hi': ['लिंग'],
    'ar': ['الجنس']
}

AGE_KEYWORDS = {
    'en': ['age', 'years old', 'yrs', 'yo'],
    'hi': ['उम्र', 'वर्ष', 'आयु'],
    'ar': ['العمر', 'سنوات', 'سنة']
}


def fix_ocr_errors(text: str) -> str:
    """
    Fix common OCR errors in text.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Text with common OCR errors corrected
    """
    if not text:
        return ""
    
    try:
        # Common OCR mistakes
        corrections = {
            # Number/letter confusions
            r'\b0([a-z])': r'O\1',  # 0 -> O at word start
            r'([a-z])0\b': r'\1O',  # 0 -> O at word end
            r'\b1([a-z])': r'I\1',  # 1 -> I at word start (context-dependent)
            r'([a-z])1\b': r'\1l',  # 1 -> l at word end
            
            # Common character confusions
            r'rn': 'm',  # rn often misread as m
            r'vv': 'w',  # vv often misread as w
            r'ii': 'n',  # ii sometimes misread as n
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    except Exception as e:
        logger.warning(f"OCR error correction failed: {e}")
        return text


def normalize_text(text: str) -> str:
    """
    Enhanced normalization: strip noise, fix repeated characters, remove symbols.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    try:
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix repeated characters (e.g., "naaaame" -> "name")
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)
        
        # Fix common OCR errors
        text = fix_ocr_errors(text)
        
        # Remove special symbols but keep basic punctuation
        text = re.sub(r'[^\w\s@.\-+()]', ' ', text)
        
        # Fix broken words (common OCR errors)
        words = text.split()
        cleaned_words = []
        for word in words:
            if len(word) > 1 or word.isalnum():
                cleaned_words.append(word)
        text = ' '.join(cleaned_words)
        
        return text.strip()
    except Exception as e:
        logger.warning(f"Normalization failed: {e}")
        return text


def extract_name(text: str, language: str = 'en') -> Optional[str]:
    """Extract name from text with multilingual support. Handles First/Middle/Last name patterns."""
    try:
        # Detect language if not provided
        if not language or language == 'multi':
            language = detect_language(text)
        
        # First, try to extract multi-part names (First, Middle, Last)
        # Handle OCR errors like "mame" instead of "name", "norme" instead of "name"
        first_name_match = re.search(r'(?:first\s+(?:name|mame|norme))[:\s]+([A-Z][a-zA-Z]+)', text, re.IGNORECASE)
        middle_name_match = re.search(r'(?:middle\s+(?:name|mame|norme))[:\s]+([A-Z][a-zA-Z]+)', text, re.IGNORECASE)
        last_name_match = re.search(r'(?:last\s+name)[:\s]+([A-Z][a-zA-Z]+)', text, re.IGNORECASE)
        
        if first_name_match or last_name_match:
            name_parts = []
            if first_name_match:
                name_parts.append(first_name_match.group(1))
            if middle_name_match:
                name_parts.append(middle_name_match.group(1))
            if last_name_match:
                name_parts.append(last_name_match.group(1))
            
            if name_parts:
                full_name = ' '.join(name_parts)
                logger.info(f"[NAME] Extracted multi-part name: {full_name}")
                return full_name
        
        # Build multilingual patterns
        keywords = NAME_KEYWORDS.get(language, NAME_KEYWORDS['en'])
        keyword_pattern = '|'.join(keywords)
        
        # Enhanced patterns for name extraction (handle OCR errors)
        patterns = [
            # Explicit labels with colon (most specific) - handle OCR errors like "mame"
            r'(?:name|full\s+name|applicant\s+name|your\s+name|mame|norme)[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+?)(?:\s+(?:Age|Gender|Phone|Email|Address|City|State|Country|Date|Birth)|$)',
            
            # Explicit labels (multilingual) - but limit to reasonable length
            rf'(?:{keyword_pattern})[:\s]+([^\n:]{2,50}?)(?:\s+(?:Age|Gender|Phone|Email|Address|City|State|Country|Date|Birth|$))',
            
            # English-specific: capitalized names with proper boundaries
            r'(?:name|full\s+name|applicant\s+name|your\s+name|mame|norme)[:\s\-]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            
            # First line pattern (often the name) - but only if it looks like a name
            r'^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)(?:\s|$)',
            
            # Pattern: Name on its own line
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+)\s*$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean up - remove any trailing labels that might have been captured
                name = re.sub(r'\s+(Age|Gender|Phone|Email|Address|City|State|Country|Date|Birth).*$', '', name, flags=re.IGNORECASE)
                name = name.strip()
                
                # Validate it's a reasonable name (2-4 words, each starting with capital for English)
                if language == 'en':
                    words = name.split()
                    if 2 <= len(words) <= 4 and all(w and w[0].isupper() and len(w) > 1 for w in words):
                        logger.info(f"[NAME] Extracted name: {name}")
                        return normalize_text(name)
                else:
                    # For other languages, validate it's not too long
                    if 2 <= len(name.split()) <= 4:
                        logger.info(f"[NAME] Extracted name: {name}")
                        return normalize_text(name)
        
        # Fallback: look for capitalized words in first few lines (English)
        if language == 'en':
            lines = text.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if not line:
                    continue
                words = line.split()
                # Look for 2-3 capitalized words (likely a name)
                if 2 <= len(words) <= 4:
                    if all(w and w[0].isupper() and len(w) > 1 for w in words[:2]):
                        name = ' '.join(words[:2])
                        logger.info(f"[NAME] Extracted name (fallback): {name}")
                        return normalize_text(name)
        
        logger.warning("[NAME] No name found")
        return None
    except Exception as e:
        logger.warning(f"Name extraction failed: {e}")
        return None


def extract_age(text: str) -> Optional[str]:
    """Extract age from text with improved patterns."""
    try:
        patterns = [
            # Explicit labels
            r'(?:age|years?\s+old|yrs?\.?)[:\s\-]+(\d{1,3})',
            r'\b(\d{1,3})\s*(?:years?\s+old|yrs?\.?|y\.?o\.?)',
            
            # Pattern: Age: 25
            r'age[:\s]+(\d{1,3})',
            
            # Standalone age (2 digits, reasonable range)
            r'\b([1-9][0-9])\b',  # 10-99
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    age = int(match)
                    if 1 <= age <= 150:
                        return str(age)
                except ValueError:
                    continue
        
        return None
    except Exception as e:
        logger.warning(f"Age extraction failed: {e}")
        return None


def extract_gender(text: str) -> Optional[str]:
    """Extract gender from text with improved patterns."""
    try:
        patterns = [
            # Explicit labels
            r'(?:gender|sex)[:\s\-]+(male|female|other|m|f|m\.|f\.)',
            r'(?:gender|sex)[:\s\-]+([MF])',
            
            # Standalone mentions
            r'\b(male|female|other)\b',
            r'\b([MF])\b',  # Single letter
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender = match.group(1).lower().strip('.')
                if gender in ['m', 'male']:
                    return 'Male'
                elif gender in ['f', 'female']:
                    return 'Female'
                elif gender == 'other':
                    return 'Other'
        
        return None
    except Exception as e:
        logger.warning(f"Gender extraction failed: {e}")
        return None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text with improved patterns."""
    try:
        logger.info(f"[PHONE] Extracting from text: {text[:200]}")
        
        # Enhanced phone patterns
        patterns = [
            # With labels (most specific first) - handles "Phone number: 555-12345" or "Phone number 555-12345"
            r'(?:phone|mobile|tel|contact|ph\.?)[:\s\-]*(?:number)?[:\s\-]*(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})',
            
            # Pattern: Phone number: 555-12345 (with dash) - more specific for short formats
            r'(?:phone|mobile|tel|contact|ph\.?)[:\s\-]*(?:number)?[:\s\-]*(\d{3,4}[-.\s]?\d{4,8})',
            
            # International format
            r'(\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})',
            
            # Standard formats
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',  # US format: 555-123-4567
            r'(\d{3,4}[-.\s]?\d{4,8})',  # Format: 555-12345 or 5555-1234
            r'(\d{4}[-.\s]?\d{3}[-.\s]?\d{3})',  # Alternative format
            r'(\d{7,15})',  # Generic 7-15 digits (no separators)
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            logger.info(f"[PHONE] Pattern {i} matches: {matches}")
            for match in matches:
                # Clean up the phone number but keep original format for display
                phone_clean = re.sub(r'[-.\s()]', '', match)
                logger.info(f"[PHONE] Match: {match}, Cleaned: {phone_clean}, Length: {len(phone_clean)}")
                # Validate length (7-15 digits is reasonable)
                if 7 <= len(phone_clean) <= 15:
                    # Return with original formatting if it had separators
                    if any(c in match for c in ['-', '.', ' ', '(']):
                        logger.info(f"[PHONE] Extracted: {match.strip()}")
                        return match.strip()
                    logger.info(f"[PHONE] Extracted: {phone_clean}")
                    return phone_clean
        
        logger.warning(f"[PHONE] No valid phone number found in text")
        return None
    except Exception as e:
        logger.warning(f"Phone extraction failed: {e}")
        return None


def extract_email(text: str) -> Optional[str]:
    """Extract email from text with improved patterns. Handles spaces in email addresses."""
    try:
        logger.info(f"[EMAIL] Extracting from text: {text[:200]}")
        
        # Enhanced email patterns - handle spaces in email (OCR error)
        patterns = [
            # With labels - handle spaces in email
            r'(?:email|e-mail|mail|email\s+id)[:\s\-]*([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
            
            # Standard email with spaces
            r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
            
            # Standard email without spaces
            r'(?:email|e-mail|mail|email\s+id)[:\s\-]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            
            # Standalone email
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            
            # Handle common OCR errors in emails
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:com|net|org|edu|gov|in|co))',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle patterns with separate groups (for emails with spaces)
                if len(match.groups()) == 3:
                    email = f"{match.group(1)}@{match.group(2)}.{match.group(3)}"
                else:
                    email = match.group(1)
                
                email = email.lower().replace(' ', '')  # Remove any spaces
                # Fix common OCR errors
                email = email.replace('0', 'o').replace('1', 'l')
                # Basic validation
                if '@' in email and '.' in email.split('@')[1]:
                    logger.info(f"[EMAIL] Extracted: {email}")
                    return email
        
        logger.warning("[EMAIL] No email found")
        return None
    except Exception as e:
        logger.warning(f"Email extraction failed: {e}")
        return None


def extract_address(text: str) -> Optional[str]:
    """Extract address (multi-line) from text with improved patterns. Handles Address Line1 and Line2."""
    try:
        logger.info(f"[ADDRESS] Extracting from text: {text[:300]}")
        
        # First, try to extract Address Line1 and Line2 separately
        # Handle OCR errors like "Adebress Linet" instead of "Address Line1"
        address_line1_match = re.search(r'(?:address\s+line\s*1|address\s+linet|adebress\s+linet)[:\s]+([^\n:]+?)(?:\s+Address\s+Line\s*2|City|State|Country|$)', text, re.IGNORECASE)
        address_line2_match = re.search(r'(?:address\s+line\s*2)[:\s]+([^\n:]+?)(?:\s+City|State|Country|Pin|Phone|Email|$)', text, re.IGNORECASE)
        
        address_parts = []
        if address_line1_match:
            addr1 = address_line1_match.group(1).strip()
            # Clean up OCR errors
            addr1 = re.sub(r'\s+(Address\s+Line\s*2|City|State|Country|Pin|Phone|Email).*$', '', addr1, flags=re.IGNORECASE)
            if addr1:
                address_parts.append(addr1)
                logger.info(f"[ADDRESS] Line1: {addr1}")
        
        if address_line2_match:
            addr2 = address_line2_match.group(1).strip()
            # Clean up trailing fields
            addr2 = re.sub(r'\s+(City|State|Country|Pin|Code|Phone|Email).*$', '', addr2, flags=re.IGNORECASE)
            if addr2:
                address_parts.append(addr2)
                logger.info(f"[ADDRESS] Line2: {addr2}")
        
        if address_parts:
            full_address = ', '.join(address_parts)
            logger.info(f"[ADDRESS] Extracted full address: {full_address}")
            return normalize_text(full_address)
        
        # Enhanced address patterns - be more specific to stop at next field
        patterns = [
            # With labels - stop at City/State/Country (most specific)
            r'(?:address|residence|location|addr\.?)[:\s]+([^\n:]+?)(?:\s+City|\s+State|\s+Country|$)',
            
            # Street address pattern - stop at City/State/Country
            r'(\d+\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Circle|Ct|Court|Parkway|Pkwy|Place|Pl))(?:\s+City|\s+State|\s+Country|$)',
            
            # With labels - multi-line version
            r'(?:address|residence|location|addr\.?)[:\s\-]+(.+?)(?:\n\n|\n(?:phone|email|name|age|gender|contact)|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                addr = match.group(1).strip()
                # Clean up - remove any trailing field labels or email addresses
                addr = re.sub(r'\s+(City|State|Country|Phone|Email|Name|Age|Gender).*$', '', addr, flags=re.IGNORECASE)
                # Remove email addresses that might have been captured
                addr = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr)
                addr = addr.strip()
                # Clean up multiple newlines
                addr = re.sub(r'\n+', ' ', addr)  # Convert newlines to spaces for single-line addresses
                # Remove extra whitespace
                addr = re.sub(r'\s+', ' ', addr)
                if len(addr) > 5 and not addr.lower().startswith('email'):  # Valid address should be longer than 5 chars and not start with "email"
                    return normalize_text(addr[:200])  # Limit length
        
        # Fallback: look for lines with numbers and street names
        lines = text.split('\n')
        address_lines = []
        for i, line in enumerate(lines):
            # Check if line contains address-like content
            if re.search(r'\d+.*(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|address|addr)', line, re.IGNORECASE):
                # Collect this line and next 2-3 lines
                address_lines = lines[i:min(i+4, len(lines))]
                break
        
        if address_lines:
            addr = '\n'.join([l.strip() for l in address_lines if l.strip()])
            return normalize_text(addr)
        
        return None
    except Exception as e:
        logger.warning(f"Address extraction failed: {e}")
        return None


def extract_all_fields(text: str, language: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Extract all fields from OCR text with multilingual support.
    
    Args:
        text: Raw OCR text
        language: Optional language code ('en', 'hi', 'ar', 'multi')
        
    Returns:
        Dict with extracted fields and confidence scores
    """
    if not text:
        logger.warning("Empty text provided for field extraction")
        return {
            "fields": {
                "name": None,
                "age": None,
                "gender": None,
                "phone": None,
                "email": None,
                "address": None,
                "address_line1": None,
                "address_line2": None,
                "city": None,
                "state": None,
                "country": None
            },
            "confidence_scores": {},
            "language_detected": language or 'en'
        }
    
    try:
        # Detect language if not provided
        if not language:
            language = detect_language(text)
        
        # Normalize text first
        normalized_text = normalize_text(text)
        logger.info(f"[DEBUG] Normalized text length: {len(normalized_text)}")
        logger.info(f"[DEBUG] Language detected: {language}")
        
        # Extract fields with multilingual patterns
        fields = {
            "name": extract_name(normalized_text, language),
            "age": extract_age(normalized_text),
            "gender": extract_gender(normalized_text),
            "phone": extract_phone(normalized_text),
            "email": extract_email(normalized_text),
            "address": extract_address(normalized_text)
        }
        
        # Parse address into components if available
        address = fields.get("address")
        if address:
            # Clean address - remove email if it got captured
            address = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', address)
            address = re.sub(r'\s+', ' ', address).strip()
            fields["address"] = address if address else None
            
            # Try to split address by comma or newline
            if ',' in address:
                address_lines = [a.strip() for a in address.split(',')]
            else:
                address_lines = address.split('\n')
            
            fields["address_line1"] = address_lines[0] if len(address_lines) > 0 and address_lines[0] else None
            fields["address_line2"] = address_lines[1] if len(address_lines) > 1 and address_lines[1] else None
        
        # Also try to extract Address Line1 and Line2 directly from text if not already set
        if not fields.get("address_line1") or not fields.get("address_line2"):
            # Use original text (before normalization) to extract address lines
            address_line1_match = re.search(r'(?:address\s+line\s*1|address\s+linet|adebress\s+linet)[:\s]+([^\n:]+?)(?:\s+Address\s+Line\s*2|City|State|Country|$)', text, re.IGNORECASE)
            address_line2_match = re.search(r'(?:address\s+line\s*2)[:\s]+([^\n:]+?)(?:\s+City|State|Country|Pin|Phone|Email|$)', text, re.IGNORECASE)
            
            if address_line1_match and not fields.get("address_line1"):
                addr1 = address_line1_match.group(1).strip()
                addr1 = re.sub(r'\s+(Address\s+Line\s*2|City|State|Country|Pin|Phone|Email).*$', '', addr1, flags=re.IGNORECASE)
                fields["address_line1"] = normalize_text(addr1) if addr1 else None
            
            if address_line2_match and not fields.get("address_line2"):
                addr2 = address_line2_match.group(1).strip()
                addr2 = re.sub(r'\s+(City|State|Country|Pin|Code|Phone|Email).*$', '', addr2, flags=re.IGNORECASE)
                fields["address_line2"] = normalize_text(addr2) if addr2 else None
        
        # Extract city, state, country from the original normalized text (not from address field)
        # Look for "City: X" pattern - stop at State, Pin Code, or Phone
        city_match = re.search(r'(?:city|city\s*:)[:\s]+([A-Z][a-zA-Z]+)(?:\s+(?:State|Pin|Phone|Email|Code)|$)', normalized_text, re.IGNORECASE)
        if city_match:
            city = city_match.group(1).strip()
            # Remove any trailing state/country names
            city = re.sub(r'\s+(State|Country|Pin|Code|Phone|Email).*$', '', city, flags=re.IGNORECASE)
            fields["city"] = city.strip()
            logger.info(f"[CITY] Extracted: {fields['city']}")
        
        # Look for "State: X" pattern - stop at Pin Code, Phone, or Email
        state_match = re.search(r'(?:state|state\s*:)[:\s]+([A-Z][a-zA-Z]+)(?:\s+(?:Pin|Phone|Email|Code|Country)|$)', normalized_text, re.IGNORECASE)
        if state_match:
            state = state_match.group(1).strip()
            # Remove any trailing pin code or other fields
            state = re.sub(r'\s+(Pin|Code|Phone|Email|Country).*$', '', state, flags=re.IGNORECASE)
            fields["state"] = state.strip()
            logger.info(f"[STATE] Extracted: {fields['state']}")
        
        # Look for "Country: X" pattern
        country_match = re.search(r'(?:country|country\s*:)[:\s]+([A-Z][a-zA-Z]+)(?:\s+(?:Pin|Phone|Email|Code|State)|$)', normalized_text, re.IGNORECASE)
        if country_match:
            country = country_match.group(1).strip()
            fields["country"] = country.strip()
            logger.info(f"[COUNTRY] Extracted: {fields['country']}")
        
        # Calculate confidence scores (simplified - can be enhanced)
        confidence_scores = {}
        for field_name, field_value in fields.items():
            if field_value:
                # Basic confidence: 0.8 if found, can be enhanced with actual OCR confidence
                confidence_scores[field_name] = 0.8
            else:
                confidence_scores[field_name] = 0.0
        
        # Log extraction results
        extracted = [k for k, v in fields.items() if v is not None]
        logger.info(f"Extracted fields: {', '.join(extracted) if extracted else 'none'}")
        
        # Log what was extracted for debugging
        for field_name, field_value in fields.items():
            if field_value:
                logger.info(f"[FIELD] {field_name}: {field_value}")
        
        return {
            "fields": fields,
            "confidence_scores": confidence_scores,
            "language_detected": language
        }
        
    except Exception as e:
        logger.error(f"Field extraction failed: {e}", exc_info=True)
        # Return empty fields on error
        return {
            "fields": {
                "name": None,
                "age": None,
                "gender": None,
                "phone": None,
                "email": None,
                "address": None,
                "address_line1": None,
                "address_line2": None,
                "city": None,
                "state": None,
                "country": None
            },
            "confidence_scores": {},
            "language_detected": language or 'en'
        }
