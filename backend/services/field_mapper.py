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

# Compile regex patterns for speed (compile once, use many times)
# FIXED: Patterns now handle lowercase/mixed case from OCR errors
_compiled_patterns = {
    'name': [
        # More flexible: allows lowercase start (OCR might lowercase first letter)
        re.compile(r'(?:name|full\s+name|applicant\s+name|your\s+name|mame|norme|neme)[:\s]+([A-Za-z][a-zA-Z.]+(?:\s+[A-Za-z][a-zA-Z]+)+?)(?:\s+(?:Age|Gender|Phone|Email|Address|City|State|Country|Date|Birth|Parents|Occupation|Mobile)|$)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'(?:name|mame|neme)[:\s]+([A-Za-z]\.?\s*[A-Za-z][a-zA-Z]+\s+[A-Za-z][a-zA-Z]+(?:\s+[A-Za-z][a-zA-Z]+)?)', re.IGNORECASE),
    ],
    'phone': [
        re.compile(r'(?:phone|mobile|tel|contact|ph\.?)[:\s\-]*(?:number)?[:\s\-]*(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})', re.IGNORECASE),
        re.compile(r'(\d{7,15})', re.IGNORECASE),
    ],
    'email': [
        re.compile(r'(?:email|e-mail|mail|email\s+id|emailid|emailld)[:\s\-]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
        re.compile(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', re.IGNORECASE),
    ],
    'dob': [
        re.compile(r'(?:date\s+of\s+birth|dob|birth\s+date|d\.o\.b\.?|date\s+st\s+bisth|date\s+st)[:\s\-\.]+(\d{1,2})[/.\-l](\d{1,2})[/.\-l](\d{2,4})', re.IGNORECASE),
        re.compile(r'(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})', re.IGNORECASE),
    ],
    'occupation': [
        # More flexible: allows lowercase start
        re.compile(r'(?:occupation|profession|job|designation|ocupation)[:.\s\-]+([A-Za-z][a-zA-Z\s]+?)(?:\s+(?:Phone|Email|Address|Age|Gender|Mobile|Date|Birth|Mobile|Number|$))', re.IGNORECASE),
    ],
    'parents': [
        # More flexible: allows lowercase start
        re.compile(r'(?:parents\s+name|parent\s+name|parents\s+ame|parent\s+ame)[:\s\.]+([A-Za-z][a-zA-Z.]+(?:\s+[A-Za-z][a-zA-Z]+)+?)(?:\s+(?:Occupation|Phone|Email|Address|Age|Gender|Mobile|Date|Birth|$))', re.IGNORECASE),
    ],
}

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
            
            # Common words and field labels
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
            'numbes': 'Number',
            'phome': 'Phone',
            'phne': 'Phone',
            'emal': 'Email',
            'emai': 'Email',
            'emial': 'Email',
            'emailld': 'EmailId',
            'read': 'Road',
            'rood': 'Road',
            'strt': 'Street',
            'stret': 'Street',
            'stree': 'Street',
            'streeet': 'Street',
            
            # Common OCR mistakes in field labels
            'neme': 'Name',
            'mame': 'Name',
            'norme': 'Name',
            'occupation.': 'Occupation:',
            'ocupation': 'Occupation',
            'ocupation-': 'Occupation:',
            'teachex': 'Teacher',
            # Removed specific name fixes - these should be handled generically
            'parents ame': 'Parents Name',
            'parents': 'Parents',
            'date st bisth': 'Date of Birth',
            'date st': 'Date of Birth',
            'bisth': 'Birth',
            'mobile numbes': 'Mobile Number',
            'mobile': 'Mobile',
            'emailld': 'EmailId',
            'emailid': 'EmailId',
            
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
            
            # Generic OCR character confusions (works for any text)
            # Fix '0'/'O' confusion in words (but keep 0 in numbers)
            (r'\b([A-Za-z]+)0([A-Za-z]+)\b', r'\1O\2'),  # Letter-0-Letter -> Letter-O-Letter
            # Fix 'l'/'I' confusion in dates (l/I often means 1 or /)
            (r'(\d)[lI](\d)', r'\1/\2'),  # Number-l/I-Number -> Number/Number
            
            # Fix spacing issues
            (r'([a-z])([A-Z])', r'\1 \2'),  # Add space between lowercase and uppercase
            (r'([A-Z])\.([A-Z])', r'\1. \2'),  # Fix spacing: "N.Surya" -> "N. Surya"
            (r'([A-Z])([A-Z][a-z])', r'\1 \2'),  # Add space between two words
            
            # Fix common OCR mistakes in numbers
            (r'(\d)\s+(\d)', r'\1\2'),  # Remove spaces in numbers
            (r'([a-z])(\d)', r'\1 \2'),  # Add space before number
            (r'(\d)([a-z])', r'\1 \2'),  # Add space after number
            
            # Fix date OCR errors: 'l', 'I', or '|' in dates -> '/'
            (r'(\d{1,2})[lI|](\d{1,2})[lI|](\d{2,4})', r'\1/\2/\3'),  # "05101l2005" -> "05/10/2005"
            (r'(\d{1,2})[lI|](\d{1,2})', r'\1/\2'),  # Partial date fix
        ]
        
        for pattern, replacement in pattern_corrections:
            text = re.sub(pattern, replacement, text)
        
        # Fix repeated characters (common OCR error)
        text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text)  # aaa -> aa
        
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR error correction failed: {e}")
        return text


def clean_extracted_value(value: str, field_type: str = "generic") -> str:
    """
    Clean and correct extracted field value to ensure accuracy.
    Removes OCR errors, fixes character confusions, and validates format.
    
    Args:
        value: Extracted field value
        field_type: Type of field (name, email, phone, date, etc.)
        
    Returns:
        Cleaned and corrected value
    """
    if not value:
        return ""
    
    try:
        # Start with normalization
        cleaned = normalize_text(value)
        
        # Field-specific cleaning
        if field_type == "name":
            # Remove any numbers from names (OCR might capture)
            cleaned = re.sub(r'\d+', '', cleaned)
            # Fix spacing around periods (initials)
            cleaned = re.sub(r'\.\s*', '. ', cleaned)
            cleaned = re.sub(r'\s+\.', ' .', cleaned)
            # Remove special characters except periods and hyphens
            cleaned = re.sub(r'[^\w\s.\-]', '', cleaned)
            
        elif field_type == "email":
            # Remove spaces in email
            cleaned = cleaned.replace(' ', '')
            # Fix common OCR errors in email
            cleaned = re.sub(r'([a-z])0([a-z])', r'\1o\2', cleaned)  # 0 -> o in email
            cleaned = re.sub(r'([a-z])rn([a-z])', r'\1m\2', cleaned)  # rn -> m
            # Ensure valid email format
            if '@' not in cleaned:
                return ""
            
        elif field_type == "phone":
            # Remove all non-digit characters except +, -, (, )
            cleaned = re.sub(r'[^\d+\-()]', '', cleaned)
            # Remove leading/trailing non-digits
            cleaned = cleaned.strip('+-()')
            
        elif field_type == "date":
            # Fix common date OCR errors
            cleaned = re.sub(r'[lI|]', '/', cleaned)  # l/I/| -> /
            cleaned = re.sub(r'[Oo]', '0', cleaned)  # O/o -> 0 in dates
            # Remove spaces in dates
            cleaned = re.sub(r'\s+', '', cleaned)
            
        elif field_type == "number":
            # Remove all non-digit characters
            cleaned = re.sub(r'[^\d]', '', cleaned)
            
        # Generic cleaning for all fields
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Remove excessive spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing punctuation (except for emails, dates)
        if field_type not in ["email", "date", "phone"]:
            cleaned = cleaned.strip('.,;:!?')
        
        # Remove control characters
        cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
        
        return cleaned.strip()
    except Exception as e:
        logger.warning(f"Value cleaning failed for {field_type}: {e}")
        return value.strip() if value else ""


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


def parse_name_components(full_name: str) -> Dict[str, Optional[str]]:
    """
    Parse full name into first name, middle name, and last name components.
    Works generically for any name format.
    
    Args:
        full_name: Full name string
        
    Returns:
        Dict with 'first_name', 'middle_name', 'last_name' keys
    """
    if not full_name:
        return {
            "first_name": None,
            "middle_name": None,
            "last_name": None
        }
    
    try:
        # Clean and normalize the name
        name = full_name.strip()
        
        # Split by spaces
        words = name.split()
        
        if len(words) == 0:
            return {"first_name": None, "middle_name": None, "last_name": None}
        elif len(words) == 1:
            # Single word - treat as first name
            return {
                "first_name": words[0],
                "middle_name": None,
                "last_name": None
            }
        elif len(words) == 2:
            # Two words - First and Last
            return {
                "first_name": words[0],
                "middle_name": None,
                "last_name": words[1]
            }
        elif len(words) == 3:
            # Three words - could be First Middle Last or First Last Last
            # Check if middle word is an initial (single letter or letter with period)
            middle = words[1]
            if len(middle) <= 2 and (middle.endswith('.') or len(middle) == 1):
                # Middle is an initial - First Middle Last
                return {
                    "first_name": words[0],
                    "middle_name": middle,
                    "last_name": words[2]
                }
            else:
                # Could be First Middle Last or compound last name
                # Common pattern: if last word is common last name pattern, treat middle as middle name
                # Otherwise, treat last two as compound last name
                return {
                    "first_name": words[0],
                    "middle_name": words[1],
                    "last_name": words[2]
                }
        else:
            # Four or more words - First, Middle(s), Last
            # Last word is typically the last name
            # First word is first name
            # Everything in between is middle name(s)
            first_name = words[0]
            last_name = words[-1]
            middle_name = ' '.join(words[1:-1]) if len(words) > 2 else None
            
            return {
                "first_name": first_name,
                "middle_name": middle_name if middle_name else None,
                "last_name": last_name
            }
    except Exception as e:
        logger.warning(f"Name parsing failed: {e}")
        return {
            "first_name": full_name,  # Fallback: use full name as first name
            "middle_name": None,
            "last_name": None
        }


def extract_name(text: str, language: str = 'en') -> Optional[str]:
    """Extract name from text with multilingual support and enhanced OCR error correction."""
    try:
        if not language:
            language = 'en'
        
        # Use compiled patterns for speed
        for pattern in _compiled_patterns['name']:
            match = pattern.search(text)
            if match:
                name = match.group(1).strip()
                # Clean up trailing labels
                name = re.sub(r'\s+(Age|Gender|Phone|Email|Address|City|State|Country|Date|Birth).*$', '', name, flags=re.IGNORECASE)
                name = name.strip()
                
                # Generic OCR error fixes for names (works for any name)
                # Fix spacing: "N.Surya" -> "N. Surya"
                name = re.sub(r'([A-Za-z])\.([A-Za-z])', r'\1. \2', name)
                # Fix missing space after period: "N.Surya" -> "N. Surya"
                name = re.sub(r'([A-Za-z])\.([A-Za-z])', r'\1. \2', name)
                
                # Generic capitalization: Proper case for names (first letter uppercase, rest lowercase)
                words = name.split()
                capitalized_words = []
                for word in words:
                    if word and word[0].isalpha():
                        # Capitalize first letter, lowercase rest (standard name format)
                        if len(word) > 1:
                            capitalized_words.append(word[0].upper() + word[1:].lower())
                        else:
                            capitalized_words.append(word.upper())
                    elif word.startswith('.'):
                        # Handle initials like ".Surya" -> ". Surya"
                        capitalized_words.append(word)
                    else:
                        capitalized_words.append(word)
                name = ' '.join(capitalized_words)
                
                # Generic fix: common OCR character confusions in names
                # Fix 'l'/'I' confusion (but be careful - context dependent)
                # Fix '0'/'O' in names (O is more common in names)
                name = re.sub(r'([A-Za-z])0([A-Za-z])', r'\1O\2', name)
                
                # Validate name format
                words = name.split()
                if 2 <= len(words) <= 5 and all(w and (w[0].isupper() or w[0] == '.') and len(w) > 1 for w in words if w != '.'):
                    # Clean the name before returning
                    cleaned_name = clean_extracted_value(normalize_text(name), "name")
                    return cleaned_name if cleaned_name else normalize_text(name)
        
        # Fallback: first capitalized line
        if language == 'en':
            lines = text.split('\n')
            for line in lines[:3]:  # Check only first 3 lines for speed
                line = line.strip()
                if not line or ':' in line:
                    continue
                words = line.split()
                if 2 <= len(words) <= 4 and all(w and w[0].isupper() and len(w) > 1 for w in words[:2]):
                    return normalize_text(' '.join(words[:2]))
        
        return None
    except Exception as e:
        logger.warning(f"Name extraction failed: {e}")
        return None


def extract_age(text: str) -> Optional[str]:
    """Extract age from text with improved patterns. Also calculates from date of birth."""
    try:
        # First try explicit age patterns
        patterns = [
            # Explicit labels
            r'(?:age|years?\s+old|yrs?\.?)[:\s\-]+(\d{1,3})',
            r'\b(\d{1,3})\s*(?:years?\s+old|yrs?\.?|y\.?o\.?)',
            
            # Pattern: Age: 25
            r'age[:\s]+(\d{1,3})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    age = int(match)
                    if 1 <= age <= 150:
                        logger.info(f"[AGE] Extracted: {age}")
                        return str(age)
                except ValueError:
                    continue
        
        # If no explicit age found, try to calculate from date of birth
        # Look for date of birth patterns
        dob_patterns = [
            r'(?:date\s+of\s+birth|dob|birth\s+date|d\.o\.b\.?|date\s+st\s+bisth)[:\s\-]+(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})',
            r'(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4})[/.\-](\d{1,2})[/.\-](\d{1,2})',  # YYYY/MM/DD
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Try to parse the date
                    parts = match.groups()
                    if len(parts) == 3:
                        # Determine format - if first part is 4 digits, it's YYYY/MM/DD
                        if len(parts[0]) == 4:
                            year = int(parts[0])
                        elif len(parts[2]) == 4:
                            year = int(parts[2])
                        elif len(parts[2]) == 2:
                            # Assume 20XX for 2-digit years
                            year = 2000 + int(parts[2])
                        else:
                            continue
                        
                        # Calculate age (approximate, using 2024 as current year)
                        from datetime import datetime
                        current_year = datetime.now().year
                        age = current_year - year
                        
                        if 1 <= age <= 150:
                            logger.info(f"[AGE] Calculated from DOB year {year}: {age}")
                            return str(age)
                except (ValueError, IndexError):
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
    """Extract phone number from text. Optimized for speed with compiled patterns."""
    try:
        # Use compiled patterns for speed
        for pattern in _compiled_patterns['phone']:
            matches = pattern.findall(text)
            for match in matches:
                # Remove any label text that might have been captured (generic fix)
                # Remove common label words that OCR might capture
                phone_value = match.strip()
                # Remove label words that might be at the start (case-insensitive)
                phone_value = re.sub(r'^(?:phone|mobile|tel|contact|ph|number|numbes|numb|num)\s*[:\-]?\s*', '', phone_value, flags=re.IGNORECASE)
                phone_value = phone_value.strip()
                
                phone_clean = re.sub(r'[-.\s()]', '', phone_value)
                if 7 <= len(phone_clean) <= 15 and phone_clean.isdigit():
                    # Clean the phone before returning
                    cleaned_phone = clean_extracted_value(phone_value, "phone")
                    # Return formatted if original had formatting, otherwise return clean
                    return cleaned_phone if cleaned_phone else (phone_value if any(c in phone_value for c in ['-', '.', ' ', '(']) else phone_clean)
        
        return None
    except Exception as e:
        logger.warning(f"Phone extraction failed: {e}")
        return None


def extract_email(text: str) -> Optional[str]:
    """Extract email from text with improved patterns. Handles spaces in email addresses and incomplete emails."""
    try:
        logger.info(f"[EMAIL] Extracting from text: {text[:200]}")
        
        # Enhanced email patterns - handle spaces in email (OCR error)
        patterns = [
            # With labels - handle spaces in email (most specific) - capture full email including spaces
            r'(?:email|e-mail|mail|email\s+id|emailid|emailld)[:\s\-]*([a-zA-Z0-9._%+-]+(?:\s+[a-zA-Z0-9._%+-]+)*)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
            
            # Standard email with spaces between parts
            r'([a-zA-Z0-9._%+-]+(?:\s+[a-zA-Z0-9._%+-]+)*)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
            
            # Standard email without spaces (most common)
            r'(?:email|e-mail|mail|email\s+id|emailid|emailld)[:\s\-]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            
            # Standalone email (no label)
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            
            # Handle common OCR errors in emails
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:com|net|org|edu|gov|in|co))',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle patterns with separate groups (for emails with spaces)
                if len(match.groups()) == 3:
                    local_part = match.group(1).strip()
                    domain_part = match.group(2).strip()
                    tld = match.group(3).strip()
                    
                    # Remove spaces from local part (OCR error)
                    local_part = local_part.replace(' ', '')
                    
                    # If local part is missing or too short, try to find it from context
                    if not local_part or len(local_part) < 1:
                        # Look for text before @ that might be the email prefix
                        match_pos = match.start()
                        # Look backwards for alphanumeric characters (up to 30 chars before)
                        before_at = text[max(0, match_pos-30):match_pos]
                        # Try to extract potential email prefix (look for alphanumeric text before @)
                        prefix_match = re.search(r'([a-zA-Z0-9._%+-]{1,})\s*@', before_at, re.IGNORECASE)
                        if prefix_match:
                            local_part = prefix_match.group(1).replace(' ', '')
                    
                    if local_part and domain_part and tld:
                        email = f"{local_part}@{domain_part}.{tld}"
                    else:
                        logger.warning(f"[EMAIL] Incomplete email parts: local={local_part}, domain={domain_part}, tld={tld}")
                        continue
                else:
                    email = match.group(1)
                
                email = email.lower().replace(' ', '')  # Remove any spaces
                
                # Generic OCR error fixes for emails
                if email and len(email) > 5:
                    # Remove leading OCR error characters (l, I, 1, d) that are common mistakes
                    while email and len(email) > 1 and email[0] in ['l', 'I', '1', 'd']:
                        test_email = email[1:]
                        if '@' in test_email and test_email.count('@') == 1:
                            logger.info(f"[EMAIL] Removed leading OCR error character '{email[0]}'")
                            email = test_email
                        else:
                            break
                    
                    # Generic fix: common OCR character confusions in email local part
                    # Fix 'o' -> 'r' when followed by numbers (common OCR mistake)
                    # But only in the local part (before @)
                    if '@' in email:
                        local, domain = email.split('@', 1)
                        # Fix common OCR mistakes: 'o' before numbers often should be 'r'
                        # Pattern: letter + 'o' + number -> letter + 'r' + number
                        local = re.sub(r'([a-z])o(\d)', r'\1r\2', local)
                        # Fix 'sto' -> 'str' (common pattern)
                        local = re.sub(r'sto(\d)', r'str\1', local)
                        email = f"{local}@{domain}"
                
                # Fix '0' vs 'o' in email (but be careful - 0 can be valid)
                # Only fix if it's clearly wrong (like '0@gmail.com' -> probably 'o')
                if email.startswith('0') and '@' in email:
                    # Don't auto-fix, but log it
                    logger.info(f"[EMAIL] Email starts with 0: {email}")
                
                # Basic validation
                if '@' in email and '.' in email.split('@')[1]:
                    local, domain = email.split('@')
                    # Validate: local part should have at least 1 char, domain should have at least 3
                    if len(local) >= 1 and len(domain) >= 3:
                        # Clean the email before returning
                        cleaned_email = clean_extracted_value(email, "email")
                        logger.info(f"[EMAIL] Extracted: {cleaned_email}")
                        return cleaned_email if cleaned_email else email
                    else:
                        logger.warning(f"[EMAIL] Invalid email format: {email} (local={len(local)}, domain={len(domain)})")
        
        logger.warning("[EMAIL] No email found")
        return None
    except Exception as e:
        logger.warning(f"Email extraction failed: {e}")
        return None


def extract_date_of_birth(text: str) -> Optional[str]:
    """Extract date of birth from text. Handles OCR errors generically for any date format. Optimized for speed."""
    try:
        # Enhanced patterns that handle OCR errors in date labels and formats
        patterns = [
            # Pattern with label (handles various OCR errors in "Date of Birth")
            r'(?:date\s+of\s+birth|dob|birth\s+date|d\.o\.b\.?|date\s+st\s+bisth|date\s+st\s+biosth|date\s+st|birth|bisth|biosth)[:\s\-\.]+(\d{1,2})[/.\-lI|](\d{1,2})[/.\-lI|](\d{2,4})',
            # Generic date pattern (DD/MM/YYYY or MM/DD/YYYY) - handles various separators
            r'(\d{1,2})[/.\-\s|lI](\d{1,2})[/.\-\s|lI](\d{4})',
            # Date with 2-digit year
            r'(\d{1,2})[/.\-\s|lI](\d{1,2})[/.\-\s|lI](\d{2})\b',
            # Date without separators (DDMMYYYY or MMDDYYYY) - try to parse intelligently
            r'(\d{1,2})(\d{2})(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    day, month, year = match.groups()
                    
                    # Generic OCR error fixes: common character confusions
                    # 'l', 'I', '|' are often OCR mistakes for '1' or '/'
                    day = day.replace('l', '1').replace('I', '1').replace('|', '1').replace('O', '0').replace('o', '0')
                    month = month.replace('l', '1').replace('I', '1').replace('|', '1').replace('O', '0').replace('o', '0')
                    year = year.replace('l', '1').replace('I', '1').replace('|', '1').replace('O', '0').replace('o', '0')
                    
                    # Remove any non-digit characters
                    day = re.sub(r'[^\d]', '', day)
                    month = re.sub(r'[^\d]', '', month)
                    year = re.sub(r'[^\d]', '', year)
                    
                    # Validate digits
                    if not (day.isdigit() and month.isdigit() and year.isdigit()):
                        continue
                    
                    day_int = int(day)
                    month_int = int(month)
                    year_int = int(year)
                    
                    # Validate ranges
                    if not (1 <= day_int <= 31 and 1 <= month_int <= 12):
                        continue
                    
                    # Handle 2-digit year (smart: < 50 = 20XX, >= 50 = 19XX)
                    if len(year) == 2:
                        year_int = 2000 + year_int if year_int < 50 else 1900 + year_int
                        year = str(year_int)
                    
                    # Validate year is reasonable (1900-2100)
                    if 1900 <= year_int <= 2100:
                        return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        return None
    except Exception as e:
        logger.warning(f"DOB extraction failed: {e}")
        return None


def extract_pin_code(text: str, phone_number: Optional[str] = None) -> Optional[str]:
    """Extract PIN/ZIP code from text. Excludes phone numbers."""
    try:
        logger.info(f"[PIN] Extracting from text: {text[:200]}")
        
        # Remove phone number from text if provided to avoid confusion
        text_for_pin = text
        if phone_number:
            # Remove the phone number from text to avoid matching it as PIN
            phone_clean = re.sub(r'[-.\s()]', '', phone_number)
            # Remove all occurrences of the phone number
            text_for_pin = re.sub(re.escape(phone_number), ' ', text_for_pin)
            text_for_pin = re.sub(re.escape(phone_clean), ' ', text_for_pin)
            # Also remove any 10-digit numbers that match the phone pattern
            text_for_pin = re.sub(r'\b' + re.escape(phone_clean) + r'\b', ' ', text_for_pin)
            logger.info(f"[PIN] Removed phone number {phone_number} from text")
        
        patterns = [
            # Most specific: with labels (PIN/ZIP code labels)
            r'(?:pin\s+code|pincode|zip\s+code|postal\s+code|zip|p\.?i\.?n\.?)[:\s\-]+(\d{4,6})\b',
            r'(?:pin|pincode|zip)[:\s\-]+(\d{4,6})\b',
            # Indian PIN codes are 6 digits, US ZIP codes are 5 digits
            # Only match if it's clearly a PIN code (after address keywords, before phone/email)
            r'(?:address|city|state|country|location|pincode)[^\d]*(\d{4,6})(?:\s*(?:phone|email|mobile|tel|$))',
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text_for_pin, re.IGNORECASE)
            logger.info(f"[PIN] Pattern {i} matches: {matches}")
            for match in matches:
                pin = match.strip() if isinstance(match, str) else str(match).strip()
                # Validate: PIN codes are typically 4-6 digits (not 7-15 like phone numbers)
                if 4 <= len(pin) <= 6 and pin.isdigit():
                    # Additional validation: exclude if it's the same as phone number
                    if phone_number:
                        phone_clean = re.sub(r'[-.\s()]', '', phone_number)
                        if pin in phone_clean or phone_clean.startswith(pin) or pin in phone_clean:
                            logger.info(f"[PIN] Skipping {pin} - matches phone number {phone_clean}")
                            continue
                    # Exclude if it's 10 digits (definitely a phone number)
                    if len(pin) >= 7:
                        logger.info(f"[PIN] Skipping {pin} - too long for PIN code")
                        continue
                    logger.info(f"[PIN] Extracted: {pin}")
                    return pin
        
        logger.warning("[PIN] No valid PIN code found")
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


def extract_parents_name(text: str) -> Optional[str]:
    """Extract parents name from text with improved OCR error handling. Optimized for speed."""
    try:
        # Enhanced patterns that handle OCR errors in labels (e.g., "Parents ame:" instead of "Parents Name:")
        enhanced_patterns = [
            # Handle "Parents ame:" (OCR error - missing 'N')
            re.compile(r'(?:parents\s+name|parent\s+name|parents\s+ame|parent\s+ame)[:\s\-\.]+([A-Za-z][a-zA-Z.]+(?:\s+[A-Za-z][a-zA-Z]+)+?)(?:\s+(?:Occupation|Phone|Email|Address|Age|Gender|Mobile|Date|Birth|$))', re.IGNORECASE),
            # Generic pattern
            re.compile(r'(?:parents\s+name|parent\s+name|parents\s+ame|parent\s+ame)[:\s\-\.]+([^\n:]{2,50}?)(?:\s+(?:Occupation|Phone|Email|Address|Age|Gender|Mobile|Date|Birth|$))', re.IGNORECASE),
        ]
        
        # Try enhanced patterns first
        for pattern in enhanced_patterns:
            match = pattern.search(text)
            if match:
                parents_name = match.group(1).strip()
                # Remove label words that might be captured (generic fix)
                parents_name = re.sub(r'^(?:ame|name|parents|parent)\s*[:\-]?\s*', '', parents_name, flags=re.IGNORECASE)
                parents_name = re.sub(r'\s+(Occupation|Phone|Email|Address|Age|Gender|Mobile|Date|Birth).*$', '', parents_name, flags=re.IGNORECASE)
                parents_name = re.sub(r'^\.+', '', parents_name)  # Remove leading periods
                parents_name = re.sub(r'([A-Za-z])\.([A-Za-z])', r'\1. \2', parents_name)  # Fix spacing
                
                # Generic OCR error fixes for parents names (works for any name)
                # Generic capitalization: Proper case for names
                words = parents_name.split()
                capitalized_words = []
                for word in words:
                    if word and word[0].isalpha():
                        if len(word) > 1:
                            capitalized_words.append(word[0].upper() + word[1:].lower())
                        else:
                            capitalized_words.append(word.upper())
                    elif word.startswith('.'):
                        capitalized_words.append(word)
                    else:
                        capitalized_words.append(word)
                parents_name = ' '.join(capitalized_words)
                
                # Generic fix: common OCR character confusions
                parents_name = re.sub(r'([A-Za-z])0([A-Za-z])', r'\1O\2', parents_name)
                
                if len(parents_name) > 2:
                    return normalize_text(parents_name)
        
        # Fallback to compiled patterns
        for pattern in _compiled_patterns['parents']:
            match = pattern.search(text)
            if match:
                parents_name = match.group(1).strip()
                parents_name = re.sub(r'\s+(Occupation|Phone|Email|Address|Age|Gender|Mobile|Date|Birth).*$', '', parents_name, flags=re.IGNORECASE)
                parents_name = re.sub(r'^\.+', '', parents_name)  # Remove leading periods
                parents_name = re.sub(r'([A-Z])\.([A-Z])', r'\1. \2', parents_name)  # Fix spacing
                if len(parents_name) > 2:
                    return normalize_text(parents_name)
        
        return None
    except Exception as e:
        logger.warning(f"Parents name extraction failed: {e}")
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
    """Extract occupation/profession from text with enhanced OCR error correction. Optimized for speed."""
    try:
        # Use compiled patterns for speed
        for pattern in _compiled_patterns['occupation']:
            match = pattern.search(text)
            if match:
                occupation = match.group(1).strip()
                # Remove label words that might be captured
                occupation = re.sub(r'^(?:occupation|ocupation|job|profession)\s*[:\-]?\s*', '', occupation, flags=re.IGNORECASE)
                occupation = re.sub(r'\s+(Phone|Email|Address|Age|Gender|Mobile|Date|Birth|Mobile|Number).*$', '', occupation, flags=re.IGNORECASE)
                occupation = occupation.rstrip('.').strip()
                
                if len(occupation) > 2:
                    # Generic OCR error fixes for occupations
                    # Fix common OCR errors: 'x' at end often should be 'r' (e.g., "teachex" -> "teacher")
                    occupation = re.sub(r'([a-z]+)x\b', r'\1r', occupation, flags=re.IGNORECASE)
                    # Fix 'es' -> 'er' for occupations (e.g., "teaches" -> "teacher")
                    occupation = re.sub(r'([a-z]+)es\b', r'\1er', occupation, flags=re.IGNORECASE)
                    # Capitalize properly (first letter uppercase)
                    occupation = occupation.capitalize()
                    return normalize_text(occupation)
        
        return None
    except Exception as e:
        logger.warning(f"Occupation extraction failed: {e}")
        return None


def extract_address(text: str, phone_number: Optional[str] = None, email: Optional[str] = None) -> Optional[str]:
    """Extract address (multi-line) from text with improved patterns. Handles Address Line1 and Line2."""
    try:
        logger.info(f"[ADDRESS] Extracting from text: {text[:300]}")
        
        # Remove phone and email from text to avoid capturing them in address
        text_for_address = text
        if phone_number:
            phone_clean = re.sub(r'[-.\s()]', '', phone_number)
            text_for_address = re.sub(re.escape(phone_number), '', text_for_address)
            text_for_address = re.sub(re.escape(phone_clean), '', text_for_address)
        if email:
            text_for_address = re.sub(re.escape(email), '', text_for_address)
        
        # First, try to extract Address Line1 and Line2 separately
        # Handle OCR errors like "Adebress Linet", "Aderess Linet", "Address Linet" instead of "Address Line1"
        address_line1_patterns = [
            r'(?:address\s+line\s*1|address\s+linet|adebress\s+linet|aderess\s+linet|address\s+linet1)[:\s]+([^\n:]+?)(?:\s+Address\s+Line\s*2|City|State|Country|Pin|Phone|Email|Mobile|Tel|$)',
            r'(?:address\s+line\s*1|address\s+linet)[:\s]+([^\n:]+?)(?:\n|Address\s+Line\s*2|City|State|Country|Pin|Phone|Email|Mobile|Tel|$)',
        ]
        address_line1_match = None
        for pattern in address_line1_patterns:
            address_line1_match = re.search(pattern, text_for_address, re.IGNORECASE)
            if address_line1_match:
                break
        
        address_line2_patterns = [
            r'(?:address\s+line\s*2|address\s+linet2)[:\s]+([^\n:]+?)(?:\s+City|State|Country|Pin|Phone|Email|Mobile|Tel|$)',
            r'(?:address\s+line\s*2)[:\s]+([^\n:]+?)(?:\n|City|State|Country|Pin|Phone|Email|Mobile|Tel|$)',
        ]
        address_line2_match = None
        for pattern in address_line2_patterns:
            address_line2_match = re.search(pattern, text_for_address, re.IGNORECASE)
            if address_line2_match:
                break
        
        address_parts = []
        if address_line1_match:
            addr1 = address_line1_match.group(1).strip()
            # Clean up OCR errors and trailing fields
            addr1 = re.sub(r'\s+(Address\s+Line\s*2|City|State|Country|Pin|Phone|Email|Mobile|Tel).*$', '', addr1, flags=re.IGNORECASE)
            # Remove phone numbers and emails that might have been captured
            addr1 = re.sub(r'\d{7,15}', '', addr1)  # Remove phone-like numbers
            addr1 = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr1)  # Remove emails
            if addr1 and len(addr1.strip()) > 3:
                address_parts.append(addr1.strip())
                logger.info(f"[ADDRESS] Line1: {addr1}")
        
        if address_line2_match:
            addr2 = address_line2_match.group(1).strip()
            # Clean up trailing fields
            addr2 = re.sub(r'\s+(City|State|Country|Pin|Code|Phone|Email|Mobile|Tel).*$', '', addr2, flags=re.IGNORECASE)
            # Remove phone numbers and emails
            addr2 = re.sub(r'\d{7,15}', '', addr2)
            addr2 = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr2)
            if addr2 and len(addr2.strip()) > 3:
                address_parts.append(addr2.strip())
                logger.info(f"[ADDRESS] Line2: {addr2}")
        
        if address_parts:
            full_address = ', '.join(address_parts)
            logger.info(f"[ADDRESS] Extracted full address: {full_address}")
            return normalize_text(full_address)
        
        # Enhanced address patterns - be more specific to stop at next field
        patterns = [
            # With labels - stop at City/State/Country/Pin/Phone/Email/Mobile (most specific)
            r'(?:address|residence|location|addr\.?)[:\s]+([^\n:]+?)(?:\s+(?:City|State|Country|Pin|Phone|Email|Mobile|Tel|Mobile\s+Numb|Occupation|Date|Birth|Emailld)|$)',
            
            # Street address pattern - stop at City/State/Country/Mobile/Email
            r'(\d+\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Circle|Ct|Court|Parkway|Pkwy|Place|Pl))(?:\s+(?:City|State|Country|Pin|Phone|Email|Mobile|Tel|Mobile\s+Numb|Emailld)|$)',
            
            # With labels - multi-line version (stop at phone/email keywords)
            r'(?:address|residence|location|addr\.?)[:\s\-]+(.+?)(?:\n\n|\n(?:phone|email|mobile|tel|mobile\s+numb|emailld|name|age|gender|contact|occupation|date|birth)|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_for_address, re.IGNORECASE | re.MULTILINE)
            if match:
                addr = match.group(1).strip()
                # Clean up - remove any trailing field labels
                addr = re.sub(r'\s+(City|State|Country|Phone|Email|Name|Age|Gender|Mobile|Tel|Occupation|Date|Birth).*$', '', addr, flags=re.IGNORECASE)
                # Remove email addresses that might have been captured
                addr = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr)
                # Remove phone numbers (7-15 digits)
                addr = re.sub(r'\b\d{7,15}\b', '', addr)
                addr = addr.strip()
                # Clean up multiple newlines
                addr = re.sub(r'\n+', ' ', addr)  # Convert newlines to spaces for single-line addresses
                # Remove extra whitespace
                addr = re.sub(r'\s+', ' ', addr)
                # Validate: should be longer than 5 chars, not start with "email", and not be just numbers
                if len(addr) > 5 and not addr.lower().startswith('email') and not addr.replace(' ', '').isdigit():
                    return normalize_text(addr[:200])  # Limit length
        
        # Fallback: look for lines with numbers and street names
        lines = text_for_address.split('\n')
        address_lines = []
        for i, line in enumerate(lines):
            # Check if line contains address-like content (but not phone/email)
            if re.search(r'\d+.*(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|address|addr)', line, re.IGNORECASE):
                # Skip if it contains phone or email
                if not re.search(r'\d{7,15}|@', line):
                    # Collect this line and next 2-3 lines (but stop if we hit phone/email)
                    for j in range(i, min(i+4, len(lines))):
                        check_line = lines[j]
                        if re.search(r'\d{7,15}|@', check_line):
                            break
                        address_lines.append(check_line)
                    break
        
        if address_lines:
            addr = '\n'.join([l.strip() for l in address_lines if l.strip()])
            # Clean up phone and email from address
            addr = re.sub(r'\d{7,15}', '', addr)
            addr = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr)
            addr = re.sub(r'\s+', ' ', addr).strip()
            if len(addr) > 5:
                return normalize_text(addr)
        
        return None
    except Exception as e:
        logger.warning(f"Address extraction failed: {e}")
        return None


def extract_dynamic_fields(text: str) -> Dict[str, str]:
    """
    Dynamically extract ALL fields from text using generic label:value patterns.
    Works for any document format - extracts ANY field that has a label, not just predefined ones.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Dict with all extracted fields (field_name: field_value)
    """
    dynamic_fields = {}
    
    try:
        # Enhanced patterns to catch ANY field format
        # Pattern 1: "Label: Value" format (most common)
        label_colon_pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s]{1,40}?)[:\s\-\.]+(.+?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        
        # Pattern 2: "Label Value" format (without colon)
        label_space_pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s]{2,40}?)\s+([A-Z0-9@a-z].+?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        
        # Pattern 3: "Label - Value" format
        label_dash_pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s]{1,40}?)\s*-\s*(.+?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        
        # Pattern 4: "Label. Value" format
        label_dot_pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s]{1,40}?)\s*\.\s*(.+?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        
        # Split text into lines for better parsing
        lines = text.split('\n')
        
        # Process each line
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            match = None
            # Try all patterns
            for pattern in [label_colon_pattern, label_space_pattern, label_dash_pattern, label_dot_pattern]:
                match = pattern.match(line)
                if match:
                    break
            
            if match:
                label = match.group(1).strip()
                value = match.group(2).strip()
                
                # Skip if value is too short or looks invalid
                if len(value) < 1 or len(label) < 2:
                    continue
                
                # Skip if value contains only the label (OCR error)
                if value.lower() == label.lower():
                    continue
                
                # Skip if label is too long (probably not a field label)
                if len(label) > 50:
                    continue
                
                # Normalize label name to create field key
                field_name = label.lower().strip()
                # Fix common OCR errors in labels
                field_name = re.sub(r'\s+', '_', field_name)  # Replace spaces with underscore
                field_name = re.sub(r'[^\w]', '', field_name)  # Remove special chars
                
                # Keep original field name for unknown fields (don't force mapping)
                original_field_name = field_name
                
                # Map common OCR errors and variations to standard field names
                field_mapping = {
                    'neme': 'name',
                    'mame': 'name',
                    'norme': 'name',
                    'full_name': 'name',
                    'applicant_name': 'name',
                    'date_of_birth': 'date_of_birth',
                    'dateofbirth': 'date_of_birth',
                    'dateofbisth': 'date_of_birth',
                    'datestbisth': 'date_of_birth',
                    'date_st_bisth': 'date_of_birth',
                    'dob': 'date_of_birth',
                    'birth_date': 'date_of_birth',
                    'parents_name': 'parents_name',
                    'parentsname': 'parents_name',
                    'parentsame': 'parents_name',
                    'parentname': 'parents_name',
                    'parent_name': 'parents_name',
                    'occupation': 'occupation',
                    'ocupation': 'occupation',
                    'profession': 'occupation',
                    'job': 'occupation',
                    'phone': 'phone',
                    'phone_number': 'phone',
                    'phonenumber': 'phone',
                    'mobile': 'phone',
                    'mobile_number': 'phone',
                    'mobilenumber': 'phone',
                    'mobilenumbes': 'phone',
                    'mobilenumb': 'phone',
                    'contact': 'phone',
                    'email': 'email',
                    'email_id': 'email',
                    'emailid': 'email',
                    'emailld': 'email',
                    'e_mail': 'email',
                    'e-mail': 'email',
                    'address': 'address',
                    'addr': 'address',
                    'residence': 'address',
                    'location': 'address',
                    'pin_code': 'pin_code',
                    'pincode': 'pin_code',
                    'zip_code': 'pin_code',
                    'postal_code': 'pin_code',
                    'city': 'city',
                    'state': 'state',
                    'country': 'country',
                    'age': 'age',
                    'gender': 'gender',
                    'sex': 'gender',
                }
                
                # Apply mapping for known fields, but keep original for unknown fields
                mapped_field_name = None
                if field_name in field_mapping:
                    mapped_field_name = field_mapping[field_name]
                elif field_name.endswith('_name') and 'parent' in field_name:
                    mapped_field_name = 'parents_name'
                elif 'phone' in field_name or 'mobile' in field_name or 'contact' in field_name:
                    mapped_field_name = 'phone'
                elif 'email' in field_name or 'mail' in field_name:
                    mapped_field_name = 'email'
                elif 'address' in field_name or 'addr' in field_name:
                    mapped_field_name = 'address'
                elif 'occupation' in field_name or 'job' in field_name or 'profession' in field_name:
                    mapped_field_name = 'occupation'
                elif 'date' in field_name:
                    # Check if value contains birth-related keywords
                    if 'birth' in value.lower() or 'bisth' in value.lower() or 'biosth' in value.lower() or 'dob' in value.lower():
                        mapped_field_name = 'date_of_birth'
                    # Otherwise keep as generic 'date' field
                
                # Use mapped name if available, otherwise use original (for unknown fields)
                final_field_name = mapped_field_name if mapped_field_name else original_field_name
                
                # Generic cleanup: remove label words that might be captured in value
                # Remove common label words from the start of value (OCR might capture them)
                value = re.sub(r'^(?:phone|mobile|tel|contact|ph|number|numbes|numb|num|email|mail|emailld|emailid|address|addr|name|neme|mame|occupation|ocupation|job|date|birth|bisth|biosth|parents|parent|ame)\s*[:\-]?\s*', '', value, flags=re.IGNORECASE)
                
                # Remove trailing labels that might be captured
                value = re.sub(r'\s+(Phone|Email|Address|Age|Gender|Mobile|Date|Birth|Occupation|Name|Parents|City|State|Country|Pin|Number|Id|ID|Code).*$', '', value, flags=re.IGNORECASE)
                value = value.strip()
                
                # Special handling for date field - check if it contains birth date info
                if 'date' in field_name.lower() and ('birth' in value.lower() or 'bisth' in value.lower() or 'biosth' in value.lower()):
                    field_name = 'date_of_birth'
                    # Extract just the date part, remove "St Biosth" etc.
                    date_match = re.search(r'(\d{1,2}[/.\-lI]\d{1,2}[/.\-lI]\d{2,4})', value)
                    if date_match:
                        value = date_match.group(1)
                
                # Clean value - remove trailing labels
                value = re.sub(r'\s+(Phone|Email|Address|Age|Gender|Mobile|Date|Birth|Occupation|Name|Parents|City|State|Country|Pin|Number|Id|ID|Code).*$', '', value, flags=re.IGNORECASE)
                value = value.strip()
                
                # Only add if value is meaningful
                if len(value) > 1 and value not in ['', 'None', 'N/A', 'NA', 'null']:
                    # If field already exists, keep the longer/more complete value
                    if final_field_name not in dynamic_fields or len(value) > len(dynamic_fields[final_field_name]):
                        dynamic_fields[final_field_name] = value
                        logger.debug(f"[DYNAMIC] Extracted field: {final_field_name} = {value[:50]}")
        
        # Also try to extract fields from multi-line patterns (for fields that span multiple lines)
        # Look for patterns like "Field Name:\nValue Line 1\nValue Line 2"
        multiline_pattern = re.compile(r'^([a-zA-Z][a-zA-Z\s]{1,40}?)[:\s\-\.]+\n(.+?)(?=\n(?:[A-Z][a-zA-Z\s]{1,40}?)[:\s\-\.]+|\n*$)', re.IGNORECASE | re.MULTILINE | re.DOTALL)
        multiline_matches = multiline_pattern.finditer(text)
        for match in multiline_matches:
            label = match.group(1).strip()
            value = match.group(2).strip()
            
            if len(value) > 1 and len(label) >= 2:
                field_name = label.lower().strip()
                field_name = re.sub(r'\s+', '_', field_name)
                field_name = re.sub(r'[^\w]', '', field_name)
                
                # Clean multi-line value
                value = re.sub(r'\n+', ' ', value)  # Convert newlines to spaces
                value = re.sub(r'\s+', ' ', value).strip()  # Normalize whitespace
                
                if len(value) > 1:
                    if field_name not in dynamic_fields or len(value) > len(dynamic_fields[field_name]):
                        dynamic_fields[field_name] = value
                        logger.debug(f"[DYNAMIC] Extracted multi-line field: {field_name} = {value[:50]}")
        
        logger.info(f"[DYNAMIC] Extracted {len(dynamic_fields)} dynamic fields: {list(dynamic_fields.keys())}")
        return dynamic_fields
        
    except Exception as e:
        logger.warning(f"Dynamic field extraction failed: {e}")
        return {}


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
            # Use only first 100 chars for faster detection
            language = detect_language(text[:100] if len(text) > 100 else text, sample_size=100)
        
        # IMPORTANT: Extract from both normalized AND original text
        # Normalized text helps with OCR errors, but original preserves structure
        normalized_text = normalize_text(text)
        
        # Extract standard fields with multilingual patterns
        # Extract phone and email first, as they're needed for other extractions
        # Try both normalized and original text for better extraction
        phone_number = extract_phone(normalized_text) or extract_phone(text)
        email_address = extract_email(normalized_text) or extract_email(text)
        
        # Extract full name first
        full_name = extract_name(normalized_text, language) or extract_name(text, language)
        
        # Parse name into components (first, middle, last)
        name_components = {}
        if full_name:
            name_components = parse_name_components(full_name)
        
        # Extract fields - try both normalized and original text for maximum coverage
        fields = {
            "name": full_name,  # Full name
            "first_name": name_components.get("first_name"),
            "middle_name": name_components.get("middle_name"),
            "last_name": name_components.get("last_name"),
            "age": extract_age(normalized_text) or extract_age(text),
            "gender": extract_gender(normalized_text) or extract_gender(text),
            "phone": phone_number,
            "email": email_address,
            "address": extract_address(normalized_text, phone_number=phone_number, email=email_address) or extract_address(text, phone_number=phone_number, email=email_address)
        }
        
        # Extract additional common fields (PIN code needs phone to exclude it)
        # Try both normalized and original text
        additional_fields = {
            "date_of_birth": extract_date_of_birth(normalized_text) or extract_date_of_birth(text),
            "parents_name": extract_parents_name(normalized_text) or extract_parents_name(text),
            "occupation": extract_occupation(normalized_text) or extract_occupation(text),
            "pin_code": extract_pin_code(normalized_text, phone_number=phone_number) or extract_pin_code(text, phone_number=phone_number),
            "aadhaar": extract_aadhaar(normalized_text) or extract_aadhaar(text),
            "pan": extract_pan(normalized_text) or extract_pan(text),
            "passport": extract_passport(normalized_text) or extract_passport(text)
        }
        
        # Merge additional fields into main fields dict
        fields.update(additional_fields)
        
        # Extract dynamic fields (any other fields present in the document)
        # Use BOTH original and normalized text for maximum coverage
        dynamic_fields_raw = extract_dynamic_fields(text)
        dynamic_fields_norm = extract_dynamic_fields(normalized_text)
        
        # Merge both dynamic field sets
        all_dynamic_fields = {}
        all_dynamic_fields.update(dynamic_fields_raw)
        all_dynamic_fields.update(dynamic_fields_norm)
        
        # Merge dynamic fields intelligently
        for field_name, field_value in all_dynamic_fields.items():
            # Clean and normalize the dynamic field value
            cleaned_value = normalize_text(field_value)
            
            if cleaned_value and len(cleaned_value) > 1:
                # If field already exists, compare and keep the better one
                if field_name in fields and fields[field_name]:
                    existing_value = str(fields[field_name])
                    # Keep the longer/more complete value
                    if len(cleaned_value) > len(existing_value):
                        fields[field_name] = cleaned_value
                        logger.info(f"[DYNAMIC] Updated field {field_name} with better value")
                else:
                    # Field doesn't exist, add it (EVEN IF IT'S NOT A PREDEFINED FIELD)
                    # This ensures ALL fields from the document are extracted, not just known ones
                    fields[field_name] = cleaned_value
                    logger.info(f"[DYNAMIC] Added field: {field_name} = {cleaned_value[:50]}")
        
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
        
        # Clean all extracted field values for accuracy and correctness
        cleaned_fields = {}
        for field_name, field_value in fields.items():
            if field_value is not None:
                # Determine field type for proper cleaning
                field_type = "generic"
                if field_name in ["name", "first_name", "middle_name", "last_name", "parents_name"]:
                    field_type = "name"
                elif field_name == "email":
                    field_type = "email"
                elif field_name in ["phone", "mobile"]:
                    field_type = "phone"
                elif field_name in ["date_of_birth", "dob"]:
                    field_type = "date"
                elif field_name in ["age", "pin_code", "aadhaar", "pan", "passport"]:
                    field_type = "number"
                
                # Clean the value to ensure accuracy
                cleaned_value = clean_extracted_value(str(field_value), field_type)
                
                # Only add if cleaned value is meaningful
                if cleaned_value and len(cleaned_value) > 0:
                    cleaned_fields[field_name] = cleaned_value
                elif field_value and len(str(field_value).strip()) > 0:
                    # If cleaning removed everything but original was valid, keep original
                    cleaned_fields[field_name] = str(field_value).strip()
        
        # Filter out None/null/empty fields - only keep extracted fields
        extracted_fields = {k: v for k, v in cleaned_fields.items() if v is not None and v != ""}
        
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
