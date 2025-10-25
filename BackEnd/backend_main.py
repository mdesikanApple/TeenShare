from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

# Import our PII scanner module
from pii_scanner import scan_text_for_pii, mask_sensitive_data, calculate_risk_level

# Create the FastAPI app
app = FastAPI(
    title="SafeShare Privacy Scanner API",
    description="API for detecting and masking PII in text content",
    version="1.0.0"
)

# Allow frontend to connect from different domain (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model - what we expect from the frontend
class ScanRequest(BaseModel):
    text_content: str
    has_attachment: bool = False
    attachment_name: Optional[str] = None

# Response model - what we send back to frontend
class ScanResponse(BaseModel):
    found_entities: List[Dict]
    risk_level: str
    risk_score: int
    educational_info: Dict
    masked_text: str
    attachment_findings: Optional[List[Dict]] = None

# Health check endpoint - to verify API is running
@app.get("/")
def read_root():
    return {
        "message": "SafeShare Privacy Scanner API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

# Main scanning endpoint
@app.post("/api/scan", response_model=ScanResponse)
def scan_content(request: ScanRequest):
    """
    Scans text content for personally identifiable information (PII)
    
    This endpoint:
    1. Checks the text for sensitive information
    2. Calculates how risky the content is
    3. Provides educational information about the risks
    4. Returns a masked version of the text
    """
    
    # Validate text length (100KB limit)
    max_length = 100 * 1024  # 100KB in characters
    if len(request.text_content) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Text content too large. Maximum size is {max_length} characters."
        )
    
    # Step 1: Scan the text for PII
    found_entities = scan_text_for_pii(request.text_content)
    
    # Step 2: Calculate risk level based on what we found
    risk_level, risk_score = calculate_risk_level(found_entities)
    
    # Step 3: Create masked version of the text
    masked_text = mask_sensitive_data(request.text_content, found_entities)
    
    # Step 4: Generate educational information
    educational_info = generate_educational_content(found_entities)
    
    # Step 5: Mock attachment scanning if file was uploaded
    attachment_findings = None
    if request.has_attachment:
        attachment_findings = mock_attachment_scan(request.attachment_name)
    
    # Return all the results
    return ScanResponse(
        found_entities=found_entities,
        risk_level=risk_level,
        risk_score=risk_score,
        educational_info=educational_info,
        masked_text=masked_text,
        attachment_findings=attachment_findings
    )

def generate_educational_content(found_entities: List[Dict]) -> Dict:
    """
    Creates educational messages based on what sensitive data was found
    Helps teens understand why certain information is risky to share
    """
    
    # Information about each type of sensitive data
    education_database = {
        "email": {
            "title": "Email Address Risk",
            "risk": "Medium",
            "why_risky": "Your email can be used to spam you, hack your accounts, or track you online.",
            "tips": [
                "Never share your email on public posts",
                "Use a separate email for signing up to websites",
                "Be careful who you give your email to"
            ]
        },
        "phone": {
            "title": "Phone Number Risk",
            "risk": "High",
            "why_risky": "Your phone number can be used to call or text you, track your location, or steal your identity.",
            "tips": [
                "Only share your number with people you trust",
                "Be aware of scam calls and texts",
                "Consider using messaging apps instead of giving out your number"
            ]
        },
        "ssn": {
            "title": "Social Security Number Risk",
            "risk": "Critical",
            "why_risky": "Your SSN can be used to steal your identity, open credit cards in your name, or commit fraud.",
            "tips": [
                "NEVER share your SSN online or with strangers",
                "Only provide it to trusted organizations when absolutely necessary",
                "Monitor your credit report for suspicious activity"
            ]
        },
        "credit_card": {
            "title": "Credit Card Risk",
            "risk": "Critical",
            "why_risky": "Someone can use your credit card number to make unauthorized purchases and steal money.",
            "tips": [
                "Never post pictures of your credit card",
                "Only enter card info on secure websites (https://)",
                "Report lost or stolen cards immediately"
            ]
        },
        "drivers_license": {
            "title": "Driver's License Risk",
            "risk": "High",
            "why_risky": "Your license number can be used for identity theft and contains personal information.",
            "tips": [
                "Don't post photos of your license on social media",
                "Cover your license number in photos",
                "Keep your physical license secure"
            ]
        },
        "name": {
            "title": "Full Name Risk",
            "risk": "Low-Medium",
            "why_risky": "Your name can be used to find more information about you online and track your activities.",
            "tips": [
                "Consider using a nickname on public profiles",
                "Be aware that your name is often publicly visible",
                "Combined with other info, names increase identity theft risk"
            ]
        },
        "address": {
            "title": "Physical Address Risk",
            "risk": "High",
            "why_risky": "Your address reveals where you live, which can lead to stalking, burglary, or unwanted visitors.",
            "tips": [
                "Never share your home address publicly",
                "Be careful about check-ins that reveal your location",
                "Consider using a P.O. box for online purchases"
            ]
        },
        "dob": {
            "title": "Date of Birth Risk",
            "risk": "Medium",
            "why_risky": "Your birthday is often used to verify your identity and can help hackers answer security questions.",
            "tips": [
                "Limit who can see your birthday on social media",
                "Don't use your real birthday for security questions",
                "Be aware that age can be calculated from your DOB"
            ]
        }
    }
    
    # Collect relevant educational info for found entities
    relevant_info = []
    entity_types_found = set()
    
    for entity in found_entities:
        entity_type = entity["type"]
        if entity_type not in entity_types_found:
            entity_types_found.add(entity_type)
            if entity_type in education_database:
                relevant_info.append(education_database[entity_type])
    
    # Create summary message
    if len(found_entities) == 0:
        summary = "Great job! No sensitive information detected in your content."
    elif len(found_entities) == 1:
        summary = "We found 1 piece of sensitive information. Review it below before sharing."
    else:
        summary = f"We found {len(found_entities)} pieces of sensitive information. Review them below before sharing."
    
    return {
        "summary": summary,
        "details": relevant_info,
        "total_items_found": len(found_entities)
    }

def mock_attachment_scan(filename: Optional[str]) -> List[Dict]:
    """
    Simulates scanning a document attachment
    In a real app, this would parse PDF/Word files
    For demo purposes, we return mock findings
    """
    
    # Create fake findings for demo purposes
    mock_findings = [
        {
            "type": "name",
            "value": "Jennifer Martinez",
            "location": "Page 1, Line 3",
            "risk": "Medium"
        },
        {
            "type": "address",
            "value": "456 Oak Street, Boston, MA 02101",
            "location": "Page 1, Line 8",
            "risk": "High"
        },
        {
            "type": "phone",
            "value": "(617) 555-1234",
            "location": "Page 2, Line 2",
            "risk": "High"
        },
        {
            "type": "email",
            "value": "jennifer.martinez@email.com",
            "location": "Page 2, Line 5",
            "risk": "Medium"
        },
        {
            "type": "dob",
            "value": "03/15/2008",
            "location": "Page 1, Line 12",
            "risk": "Medium"
        }
    ]
    
    return mock_findings

# Run the server when this file is executed directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload when code changes during development
    )