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
    Premium OCR error correction: Comprehensive dictionary of common mistakes.
    Fixes place names, common words, and character confusions.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Text with common OCR errors corrected
    """
    if not text:
        return ""
    
    try:
        # Comprehensive OCR error correction dictionary
        # Format: (incorrect, correct) - case-insensitive word replacements
        word_corrections = {
            # Place names (Indian states/cities)
            'kamataha': 'Karnataka',
            'kamataka': 'Karnataka',
            'kamatakha': 'Karnataka',
            'karnatakha': 'Karnataka',
            'karnatka': 'Karnataka',
            'bangalor': 'Bangalore',
            'bangalore': 'Bangalore',
            'bengaluru': 'Bangalore',
            'mumbai': 'Mumbai',
            'mumbay': 'Mumbai',
            'delhi': 'Delhi',
            'delh': 'Delhi',
            'chennai': 'Chennai',
            'madras': 'Chennai',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune',
            'puna': 'Pune',
            
            # Common words
            'layeut': 'Layout',
            'layaut': 'Layout',
            'layot': 'Layout',
            'adebress': 'Address',
            'aderess': 'Address',
            'adress': 'Address',
            'adres': 'Address',
            'linet': 'Line',
            'linet1': 'Line1',
            'linet2': 'Line2',
            'grender': 'Gender',
            'gendr': 'Gender',
            'midde': 'Middle',
            'middl': 'Middle',
            'mmber': 'Number',
            'numb': 'Number',
            'numbber': 'Number',
            'phome': 'Phone',
            'phne': 'Phone',
            'emal': 'Email',
            'emai': 'Email',
            'emial': 'Email',
            'read': 'Road',
            'rood': 'Road',
            'strt': 'Street',
            'stret': 'Street',
            'stree': 'Street',
            'streeet': 'Street',
            
            # Common OCR character mistakes
            'rn': 'm',  # rn -> m (in context)
            'vv': 'w',  # vv -> w
            'ii': 'n',  # ii -> n (context-dependent)
        }
        
        # Apply word-level corrections (case-insensitive)
        words = text.split()
        corrected_words = []
        for word in words:
            # Remove punctuation for matching, keep it for replacement
            word_lower = word.lower().strip('.,!?;:()[]{}"\'')
            if word_lower in word_corrections:
                # Preserve original case pattern if possible
                if word.isupper():
                    corrected = word_corrections[word_lower].upper()
                elif word[0].isupper():
                    corrected = word_corrections[word_lower].capitalize()
                else:
                    corrected = word_corrections[word_lower].lower()
                
                # Replace the word, preserving punctuation
                if word != word_lower:
                    # Has punctuation - preserve it
                    corrected = word.replace(word_lower, corrected)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        text = ' '.join(corrected_words)
        
        # Pattern-based corrections (for character-level mistakes)
        pattern_corrections = [
            # Fix common character confusions in context
            (r'\b([A-Z])0([a-z])', r'\1O\2'),  # Capital letter + 0 -> O
            (r'([a-z])0([A-Z])', r'\1O\2'),  # 0 between letters -> O
            (r'\b0([A-Z][a-z]+)', r'O\1'),  # 0 at word start before capital -> O
            (r'([a-z]+)0\b', r'\1O'),  # 0 at word end after lowercase -> O
            
            # Fix spacing issues
            (r'([a-z])([A-Z])', r'\1 \2'),  # Add space between lowercase and uppercase
            (r'([A-Z])([A-Z][a-z])', r'\1 \2'),  # Add space between two words
            
            # Fix common OCR mistakes in numbers
            (r'(\d)\s+(\d)', r'\1\2'),  # Remove spaces in numbers
            (r'([a-z])(\d)', r'\1 \2'),  # Add space before number
            (r'(\d)([a-z])', r'\1 \2'),  # Add space after number
        ]
        
        for pattern, replacement in pattern_corrections:
            text = re.sub(pattern, replacement, text)
        
        # Fix repeated characters (common OCR error)
        text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text)  # aaa -> aa
        
        return text.strip()
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
        # Skip language detection for speed - use provided language or default to 'en'
        # Language detection is now done once at the field extraction level
        if not language:
            language = 'en'  # Default to English for speed
        
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


def extract_date_of_birth(text: str) -> Optional[str]:
    """Extract date of birth from text."""
    try:
        patterns = [
            r'(?:date\s+of\s+birth|dob|birth\s+date|d\.o\.b\.?)[:\s\-]+(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            r'(?:date\s+of\s+birth|dob|birth\s+date|d\.o\.b\.?)[:\s\-]+(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
            r'\b(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b',  # Generic date format
            r'\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\b',  # YYYY-MM-DD format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob = match.group(1).strip()
                # Basic validation - should contain numbers and separators
                if re.match(r'\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}', dob):
                    logger.info(f"[DOB] Extracted: {dob}")
                    return dob
        
        return None
    except Exception as e:
        logger.warning(f"DOB extraction failed: {e}")
        return None


def extract_pin_code(text: str) -> Optional[str]:
    """Extract PIN/ZIP code from text."""
    try:
        patterns = [
            r'(?:pin\s+code|pincode|zip\s+code|postal\s+code|zip)[:\s\-]+(\d{4,10})',
            r'(?:pin|pincode|zip)[:\s\-]+(\d{4,10})',
            r'\b(\d{4,10})\b(?=\s*(?:phone|email|state|country|$))',  # Standalone 4-10 digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pin = match.group(1).strip()
                # Validate length (4-10 digits for various countries)
                if 4 <= len(pin) <= 10 and pin.isdigit():
                    logger.info(f"[PIN] Extracted: {pin}")
                    return pin
        
        return None
    except Exception as e:
        logger.warning(f"PIN extraction failed: {e}")
        return None


def extract_aadhaar(text: str) -> Optional[str]:
    """Extract Aadhaar number from text (Indian ID)."""
    try:
        patterns = [
            r'(?:aadhaar|aadhar|uid)[:\s\-]+(\d{4}\s?\d{4}\s?\d{4})',
            r'(?:aadhaar|aadhar|uid)[:\s\-]+(\d{12})',
            r'\b(\d{4}\s?\d{4}\s?\d{4})\b',  # Format: XXXX XXXX XXXX
            r'\b(\d{12})\b',  # 12 digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                aadhaar = match.group(1).strip().replace(' ', '')
                # Validate: should be 12 digits
                if len(aadhaar) == 12 and aadhaar.isdigit():
                    # Format as XXXX XXXX XXXX
                    formatted = f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"
                    logger.info(f"[AADHAAR] Extracted: {formatted}")
                    return formatted
        
        return None
    except Exception as e:
        logger.warning(f"Aadhaar extraction failed: {e}")
        return None


def extract_pan(text: str) -> Optional[str]:
    """Extract PAN (Permanent Account Number) from text (Indian tax ID)."""
    try:
        # PAN format: ABCDE1234F (5 letters, 4 digits, 1 letter)
        pattern = r'(?:pan|permanent\s+account\s+number)[:\s\-]+([A-Z]{5}\d{4}[A-Z])'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pan = match.group(1).upper()
            logger.info(f"[PAN] Extracted: {pan}")
            return pan
        
        # Also try without label
        pattern = r'\b([A-Z]{5}\d{4}[A-Z])\b'
        match = re.search(pattern, text)
        if match:
            pan = match.group(1).upper()
            logger.info(f"[PAN] Extracted (no label): {pan}")
            return pan
        
        return None
    except Exception as e:
        logger.warning(f"PAN extraction failed: {e}")
        return None


def extract_passport(text: str) -> Optional[str]:
    """Extract passport number from text."""
    try:
        patterns = [
            r'(?:passport|passport\s+no|passport\s+number)[:\s\-]+([A-Z0-9]{6,12})',
            r'\b([A-Z]{1,2}\d{6,9})\b',  # Common passport formats
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                passport = match.group(1).upper()
                # Basic validation
                if 6 <= len(passport) <= 12:
                    logger.info(f"[PASSPORT] Extracted: {passport}")
                    return passport
        
        return None
    except Exception as e:
        logger.warning(f"Passport extraction failed: {e}")
        return None


def extract_occupation(text: str) -> Optional[str]:
    """Extract occupation/profession from text."""
    try:
        patterns = [
            r'(?:occupation|profession|job|designation)[:\s\-]+([A-Z][a-zA-Z\s]+?)(?:\s+(?:Phone|Email|Address|Age|Gender|$))',
            r'(?:occupation|profession|job|designation)[:\s\-]+([^\n:]{2,50})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                occupation = match.group(1).strip()
                # Clean up trailing fields
                occupation = re.sub(r'\s+(Phone|Email|Address|Age|Gender).*$', '', occupation, flags=re.IGNORECASE)
                if len(occupation) > 2:
                    logger.info(f"[OCCUPATION] Extracted: {occupation}")
                    return normalize_text(occupation)
        
        return None
    except Exception as e:
        logger.warning(f"Occupation extraction failed: {e}")
        return None


def extract_address(text: str) -> Optional[str]:
    """Extract address (multi-line) from text with improved patterns. Handles Address Line1 and Line2."""
    try:
        logger.info(f"[ADDRESS] Extracting from text: {text[:300]}")
        
        # First, try to extract Address Line1 and Line2 separately
        # Handle OCR errors like "Adebress Linet", "Aderess Linet", "Address Linet" instead of "Address Line1"
        address_line1_patterns = [
            r'(?:address\s+line\s*1|address\s+linet|adebress\s+linet|aderess\s+linet|address\s+linet1)[:\s]+([^\n:]+?)(?:\s+Address\s+Line\s*2|City|State|Country|Pin|Phone|Email|$)',
            r'(?:address\s+line\s*1|address\s+linet)[:\s]+([^\n:]+?)(?:\n|Address\s+Line\s*2|City|State|Country|Pin|Phone|Email|$)',
        ]
        address_line1_match = None
        for pattern in address_line1_patterns:
            address_line1_match = re.search(pattern, text, re.IGNORECASE)
            if address_line1_match:
                break
        
        address_line2_patterns = [
            r'(?:address\s+line\s*2|address\s+linet2)[:\s]+([^\n:]+?)(?:\s+City|State|Country|Pin|Phone|Email|$)',
            r'(?:address\s+line\s*2)[:\s]+([^\n:]+?)(?:\n|City|State|Country|Pin|Phone|Email|$)',
        ]
        address_line2_match = None
        for pattern in address_line2_patterns:
            address_line2_match = re.search(pattern, text, re.IGNORECASE)
            if address_line2_match:
                break
        
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
            "fields": {},  # Empty dict - no fields extracted
            "confidence_scores": {},
            "language_detected": language or 'en'
        }
    
    try:
        # Fast language detection - only if not provided, and use small sample
        if not language:
            # Use only first 200 chars for fast detection
            language = detect_language(text[:200] if len(text) > 200 else text, sample_size=200)
            logger.debug(f"[DEBUG] Language detected: {language} (from sample)")
        else:
            logger.debug(f"[DEBUG] Using provided language: {language}")
        
        # Normalize text first
        normalized_text = normalize_text(text)
        logger.info(f"[DEBUG] Normalized text length: {len(normalized_text)}")
        
        # Extract standard fields with multilingual patterns
        fields = {
            "name": extract_name(normalized_text, language),
            "age": extract_age(normalized_text),
            "gender": extract_gender(normalized_text),
            "phone": extract_phone(normalized_text),
            "email": extract_email(normalized_text),
            "address": extract_address(normalized_text)
        }
        
        # Extract additional common fields
        additional_fields = {
            "date_of_birth": extract_date_of_birth(normalized_text),
            "pin_code": extract_pin_code(normalized_text),
            "aadhaar": extract_aadhaar(normalized_text),
            "pan": extract_pan(normalized_text),
            "passport": extract_passport(normalized_text),
            "occupation": extract_occupation(normalized_text)
        }
        
        # Merge additional fields into main fields dict
        fields.update(additional_fields)
        
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
        
        # Filter out None/null fields - only keep extracted fields
        extracted_fields = {k: v for k, v in fields.items() if v is not None}
        
        # Calculate confidence scores only for extracted fields
        confidence_scores = {}
        for field_name, field_value in extracted_fields.items():
            # Basic confidence: 0.8 if found, can be enhanced with actual OCR confidence
            confidence_scores[field_name] = 0.8
        
        # Log extraction results
        extracted = list(extracted_fields.keys())
        logger.info(f"Extracted fields: {', '.join(extracted) if extracted else 'none'}")
        
        # Log what was extracted for debugging
        for field_name, field_value in extracted_fields.items():
            logger.info(f"[FIELD] {field_name}: {field_value}")
        
        return {
            "fields": extracted_fields,  # Only return fields that were actually extracted
            "confidence_scores": confidence_scores,
            "language_detected": language
        }
        
    except Exception as e:
        logger.error(f"Field extraction failed: {e}", exc_info=True)
        # Return empty fields on error (no fields extracted)
        return {
            "fields": {},  # Empty dict - no fields extracted
            "confidence_scores": {},
            "language_detected": language or 'en'
        }
