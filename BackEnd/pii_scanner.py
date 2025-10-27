import re
from typing import List, Dict, Tuple

# Regular expressions and AI based pattern recognition for detecting different types of sensitive information
# These patterns look for specific formats of personal data based on each field type

# Social Security Number: XXX-XX-XXXX or XXXXXXXXX
SSN_PATTERN = r'\b\d{3}-?\d{2}-?\d{4}\b'

# Phone Number: Various formats like (123) 456-7890, 123-456-7890, 1234567890
PHONE_PATTERN = r'\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'

# Email: standard email format
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Credit Card: 13-16 digits, possibly with spaces or dashes
CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{3,4}\b'

# Date of Birth: MM/DD/YYYY or MM-DD-YYYY or similar
DOB_PATTERN = r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b'

# Driver's License: Varies by state, but often letters followed by numbers
# This is a simplified pattern
DRIVERS_LICENSE_PATTERN = r'\b[A-Z]{1,2}\d{6,8}\b'

# ZIP Code: 5 digits or 5+4 format
ZIP_PATTERN = r'\b\d{5}(-\d{4})?\b'

def scan_text_for_pii(text_content: str) -> List[Dict]:
    """
    Main function to scan text for all types of personally identifiable information
    Returns a list of found entities with their type, value, and position
    """
    
    found_entities = []
    
    # Scan for each type of sensitive information
    # Each function adds what it finds to the found_entities list
    
    found_entities.extend(find_social_security_numbers(text_content))
    found_entities.extend(find_phone_numbers(text_content))
    found_entities.extend(find_email_addresses(text_content))
    found_entities.extend(find_credit_cards(text_content))
    found_entities.extend(find_dates_of_birth(text_content))
    found_entities.extend(find_drivers_licenses(text_content))
    found_entities.extend(find_zip_codes(text_content))
    
    # AI-based detection (simplified for demo - in real app would use NLP)
    found_entities.extend(find_names_ai_style(text_content))
    found_entities.extend(find_addresses_ai_style(text_content))
    
    return found_entities

def find_social_security_numbers(text: str) -> List[Dict]:
    """
    Looks for Social Security Numbers in the text
    SSNs are in format: XXX-XX-XXXX
    """
    entities = []
    matches = re.finditer(SSN_PATTERN, text)
    
    for match in matches:
        # Check if it looks like a valid SSN (not all zeros, etc.)
        ssn = match.group()
        digits_only = re.sub(r'\D', '', ssn)
        
        # Basic validation - not all same digit
        if len(set(digits_only)) > 1:
            entities.append({
                "type": "ssn",
                "value": ssn,
                "start": match.start(),
                "end": match.end(),
                "risk": "critical"
            })
    
    return entities

def find_phone_numbers(text: str) -> List[Dict]:
    """
    Looks for phone numbers in various formats
    Examples: (123) 456-7890, 123-456-7890, 1234567890
    """
    entities = []
    matches = re.finditer(PHONE_PATTERN, text)
    
    for match in matches:
        phone = match.group()
        # Extract just the digits to validate
        digits = re.sub(r'\D', '', phone)
        
        # Must be 10 or 11 digits (with country code)
        if len(digits) >= 10 and len(digits) <= 11:
            entities.append({
                "type": "phone",
                "value": phone.strip(),
                "start": match.start(),
                "end": match.end(),
                "risk": "high"
            })
    
    return entities

def find_email_addresses(text: str) -> List[Dict]:
    """
    Looks for email addresses
    Example: user@example.com
    """
    entities = []
    matches = re.finditer(EMAIL_PATTERN, text)
    
    for match in matches:
        entities.append({
            "type": "email",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "risk": "medium"
        })
    
    return entities

def find_credit_cards(text: str) -> List[Dict]:
    """
    Looks for credit card numbers
    Usually 13-16 digits
    """
    entities = []
    matches = re.finditer(CREDIT_CARD_PATTERN, text)
    
    for match in matches:
        card_num = match.group()
        digits = re.sub(r'\D', '', card_num)
        
        # Basic Luhn algorithm check (simplified)
        if len(digits) >= 13 and len(digits) <= 16 and luhn_check(digits):
            entities.append({
                "type": "credit_card",
                "value": card_num,
                "start": match.start(),
                "end": match.end(),
                "risk": "critical"
            })
    
    return entities

def luhn_check(card_number: str) -> bool:
    """
    Validates credit card number using Luhn algorithm
    This is the checksum that credit card companies use
    """
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10 == 0

def find_dates_of_birth(text: str) -> List[Dict]:
    """
    Looks for dates that might be birthdays
    Format: MM/DD/YYYY or MM-DD-YYYY
    """
    entities = []
    matches = re.finditer(DOB_PATTERN, text)
    
    for match in matches:
        # Additional check: birth dates should be in reasonable range
        date_str = match.group()
        year = int(date_str.split('/')[-1] if '/' in date_str else date_str.split('-')[-1])
        
        # Only flag dates that could be birth dates (1940-2015 range for current teens/adults)
        if 1940 <= year <= 2015:
            entities.append({
                "type": "dob",
                "value": date_str,
                "start": match.start(),
                "end": match.end(),
                "risk": "medium"
            })
    
    return entities

def find_drivers_licenses(text: str) -> List[Dict]:
    """
    Looks for driver's license numbers
    Format varies by state - this is a simplified version
    """
    entities = []
    matches = re.finditer(DRIVERS_LICENSE_PATTERN, text)
    
    for match in matches:
        entities.append({
            "type": "drivers_license",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "risk": "high"
        })
    
    return entities

def find_zip_codes(text: str) -> List[Dict]:
    """
    Looks for ZIP codes (part of address detection)
    """
    entities = []
    matches = re.finditer(ZIP_PATTERN, text)
    
    for match in matches:
        entities.append({
            "type": "zip",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "risk": "low"
        })
    
    return entities

def find_names_ai_style(text: str) -> List[Dict]:
    """
    Simplified AI-style detection for full names
    For now, we use pattern matching to find capitalized words that look like names
    """
    entities = []
    
    # Pattern: Capital letter followed by lowercase, then space, then another capital word
    # Example: "John Smith", "Mary Johnson"
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    
    matches = re.finditer(name_pattern, text)
    
    for match in matches:
        name = match.group()
        
        # Filter out common words that aren't names
        common_words = ['The', 'This', 'That', 'With', 'From', 'Have', 'Been']
        if not any(word in name.split() for word in common_words):
            entities.append({
                "type": "name",
                "value": name,
                "start": match.start(),
                "end": match.end(),
                "risk": "medium"
            })
    
    return entities

def find_addresses_ai_style(text: str) -> List[Dict]:
    """
    Simplified AI-style detection for physical addresses
    Looks for street addresses with number, street name, city, state pattern
    """
    entities = []
    
    # Pattern for street addresses: number + street name
    # Example: "123 Main Street", "456 Oak Ave"
    address_pattern = r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way)\b'
    
    matches = re.finditer(address_pattern, text, re.IGNORECASE)
    
    for match in matches:
        entities.append({
            "type": "address",
            "value": match.group(),
            "start": match.start(),
            "end": match.end(),
            "risk": "high"
        })
    
    return entities

def calculate_risk_level(found_entities: List[Dict]) -> Tuple[str, int]:
    """
    Calculates overall risk level based on what sensitive information was found
    Returns risk level (string) and risk score (0-100)
    """
    
    if len(found_entities) == 0:
        return "Safe", 0
    
    # Different types of information have different risk weights
    risk_weights = {
        "ssn": 30,           # Social Security = highest risk
        "credit_card": 30,   # Credit card = highest risk
        "drivers_license": 20,
        "phone": 15,
        "address": 15,
        "email": 10,
        "dob": 10,
        "name": 5,
        "zip": 5
    }
    
    # Calculate total risk score
    total_score = 0
    for entity in found_entities:
        entity_type = entity["type"]
        if entity_type in risk_weights:
            total_score += risk_weights[entity_type]
    
    # Cap at 100
    total_score = min(total_score, 100)
    
    # Determine risk level based on score
    if total_score >= 60:
        risk_level = "Critical"
    elif total_score >= 40:
        risk_level = "High"
    elif total_score >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return risk_level, total_score

def mask_sensitive_data(original_text: str, found_entities: List[Dict]) -> str:
    """
    Creates a masked version of the text where sensitive info is hidden
    Different masking strategies for different types of information
    """
    
    # Sort entities by position (last to first) so we can replace without messing up positions
    sorted_entities = sorted(found_entities, key=lambda x: x["start"], reverse=True)
    
    masked_text = original_text
    
    for entity in sorted_entities:
        entity_type = entity["type"]
        original_value = entity["value"]
        start_pos = entity["start"]
        end_pos = entity["end"]
        
        # Apply masking based on type
        if entity_type == "email":
            masked_value = mask_email(original_value)
        elif entity_type == "phone":
            masked_value = mask_phone(original_value)
        elif entity_type == "ssn":
            masked_value = mask_ssn(original_value)
        elif entity_type == "credit_card":
            masked_value = mask_credit_card(original_value)
        elif entity_type == "drivers_license":
            masked_value = mask_drivers_license(original_value)
        elif entity_type == "name":
            masked_value = mask_name(original_value)
        elif entity_type == "address":
            masked_value = "<ADDRESS>"
        elif entity_type == "zip":
            masked_value = "<ZIP>"
        elif entity_type == "dob":
            masked_value = "mm/dd/yyyy"
        else:
            masked_value = "<REDACTED>"
        
        # Replace in text
        masked_text = masked_text[:start_pos] + masked_value + masked_text[end_pos:]
    
    return masked_text

def mask_email(email: str) -> str:
    """
    Masks email: keep first letter and domain
    Example: john@example.com -> j***@example.com
    """
    parts = email.split('@')
    if len(parts) == 2:
        username = parts[0]
        domain = parts[1]
        if len(username) > 0:
            masked_username = username[0] + '***'
            return f"{masked_username}@{domain}"
    return "***@***.com"

def mask_phone(phone: str) -> str:
    """
    Masks phone number: keep last 2 digits with formatting
    Example: (123) 456-7890 -> (***) ***-**90
    """
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 2:
        last_two = digits[-2:]
        # Keep similar format but mask most digits
        if '(' in phone:
            return f"(***) ***-**{last_two}"
        elif '-' in phone:
            return f"***-***-**{last_two}"
        else:
            return f"********{last_two}"
    return "***-***-****"

def mask_ssn(ssn: str) -> str:
    """
    Masks SSN: keep last 2 digits
    Example: 123-45-6789 -> ***-**-**89
    """
    digits = re.sub(r'\D', '', ssn)
    if len(digits) >= 2:
        last_two = digits[-2:]
        if '-' in ssn:
            return f"***-**-**{last_two}"
        else:
            return f"*******{last_two}"
    return "***-**-****"

def mask_credit_card(card: str) -> str:
    """
    Masks credit card: keep last 2 digits
    Example: 1234 5678 9012 3456 -> **** **** **** **56
    """
    digits = re.sub(r'\D', '', card)
    if len(digits) >= 2:
        last_two = digits[-2:]
        if ' ' in card:
            return f"**** **** **** **{last_two}"
        elif '-' in card:
            return f"****-****-****-**{last_two}"
        else:
            return f"**************{last_two}"
    return "****-****-****-****"

def mask_drivers_license(license_num: str) -> str:
    """
    Masks driver's license: replace all digits with X
    Example: AB1234567 -> ABXXXXXXX
    """
    return re.sub(r'\d', 'X', license_num)

def mask_name(name: str) -> str:
    """
    Masks name: keep first letter of each word
    Example: John Smith -> J*** S***
    """
    words = name.split()
    masked_words = []
    for word in words:
        if len(word) > 0:
            masked_word = word[0] + '***'
            masked_words.append(masked_word)
    return ' '.join(masked_words)
