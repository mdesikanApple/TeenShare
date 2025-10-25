"""
Test Suite for SafeShare Backend API
Run with: python test_api.py
"""

import requests
import json

# Configure API endpoint - change this to your deployed URL
API_URL = "http://localhost:8000"

def print_test_header(test_name):
    """Print a nice header for each test"""
    print("\n" + "="*60)
    print(f"TEST: {test_name}")
    print("="*60)

def test_health_check():
    """Test that the API is running"""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_with_email():
    """Test scanning text with an email address"""
    print_test_header("Scan Text with Email")
    
    test_data = {
        "text_content": "Hi! My email is john.doe@example.com if you want to contact me!",
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        print(f"\nFound Entities: {len(result['found_entities'])}")
        for entity in result['found_entities']:
            print(f"  - {entity['type']}: {entity['value']} (Risk: {entity['risk']})")
        
        print(f"\nRisk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}/100")
        
        print(f"\nMasked Text:")
        print(f"  {result['masked_text']}")
        
        if len(result['found_entities']) > 0:
            print("✅ Test passed - Email detected!")
            return True
        else:
            print("❌ Test failed - Email not detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_with_phone():
    """Test scanning text with phone number"""
    print_test_header("Scan Text with Phone Number")
    
    test_data = {
        "text_content": "Call me at (555) 123-4567 anytime!",
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        print(f"Risk Level: {result['risk_level']}")
        print(f"Found {len(result['found_entities'])} sensitive items")
        
        # Check if phone was detected
        phone_found = any(e['type'] == 'phone' for e in result['found_entities'])
        
        if phone_found:
            print("✅ Test passed - Phone number detected!")
            return True
        else:
            print("❌ Test failed - Phone number not detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_with_ssn():
    """Test scanning text with Social Security Number"""
    print_test_header("Scan Text with SSN")
    
    test_data = {
        "text_content": "My social security number is 123-45-6789",
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        print(f"Risk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}/100")
        
        # SSN should result in high/critical risk
        if result['risk_level'] in ['High', 'Critical']:
            print("✅ Test passed - SSN detected as high risk!")
            return True
        else:
            print("❌ Test failed - SSN not flagged as high risk")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_multiple_pii():
    """Test scanning with multiple types of PII"""
    print_test_header("Scan Text with Multiple PII Types")
    
    test_data = {
        "text_content": """
        Hi! I'm Sarah Johnson and I live at 456 Oak Street.
        You can reach me at sarah.j@email.com or call (555) 987-6543.
        My birthday is 03/15/2008.
        """,
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        
        print(f"Risk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"Total items found: {len(result['found_entities'])}")
        
        # Print all found items
        for entity in result['found_entities']:
            print(f"  - {entity['type']}: {entity['value']}")
        
        # Check if multiple types were detected
        entity_types = set(e['type'] for e in result['found_entities'])
        
        if len(entity_types) >= 3:
            print(f"✅ Test passed - Found {len(entity_types)} different types of PII!")
            return True
        else:
            print(f"❌ Test failed - Only found {len(entity_types)} types")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_with_attachment():
    """Test scanning with attachment flag"""
    print_test_header("Scan with Mock Attachment")
    
    test_data = {
        "text_content": "Please review my application.",
        "has_attachment": True,
        "attachment_name": "resume.pdf"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        
        print(f"Risk Level: {result['risk_level']}")
        
        # Check if attachment findings exist
        if result['attachment_findings'] and len(result['attachment_findings']) > 0:
            print(f"Found {len(result['attachment_findings'])} items in attachment")
            for finding in result['attachment_findings']:
                print(f"  - {finding['type']}: {finding['value']} at {finding['location']}")
            print("✅ Test passed - Attachment scanning works!")
            return True
        else:
            print("❌ Test failed - No attachment findings")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scan_safe_content():
    """Test scanning content with no PII"""
    print_test_header("Scan Safe Content")
    
    test_data = {
        "text_content": "The weather is beautiful today! I love coding.",
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        
        print(f"Risk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"Items found: {len(result['found_entities'])}")
        
        # Should be safe
        if result['risk_level'] == 'Safe' or result['risk_score'] == 0:
            print("✅ Test passed - Safe content detected correctly!")
            return True
        else:
            print("❌ Test failed - False positive detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_masking_functionality():
    """Test that masking works correctly"""
    print_test_header("Test Masking Functionality")
    
    test_data = {
        "text_content": "Contact me at john@example.com or call 555-123-4567",
        "has_attachment": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/scan",
            json=test_data
        )
        
        result = response.json()
        original = test_data['text_content']
        masked = result['masked_text']
        
        print(f"Original: {original}")
        print(f"Masked:   {masked}")
        
        # Masked text should be different from original
        if original != masked:
            print("✅ Test passed - Masking is working!")
            return True
        else:
            print("❌ Test failed - Text was not masked")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("SAFESHARE API TEST SUITE")
    print("="*60)
    
    tests = [
        test_health_check,
        test_scan_with_email,
        test_scan_with_phone,
        test_scan_with_ssn,
        test_scan_multiple_pii,
        test_scan_with_attachment,
        test_scan_safe_content,
        test_masking_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    print("Starting SafeShare API Tests...")
    print("Make sure the backend is running on", API_URL)
    
    # Wait for user confirmation
    input("\nPress Enter to start tests...")
    
    run_all_tests()