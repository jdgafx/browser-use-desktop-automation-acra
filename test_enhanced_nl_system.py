#!/usr/bin/env python3
"""
Test script for the enhanced natural language automation system
Tests both stealth configuration and natural language processing
"""

import asyncio
import requests
import time

def test_gradio_interface():
    """Test if the Gradio interface is running"""
    try:
        response = requests.get("http://127.0.0.1:7862", timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced automation interface is running")
            return True
        else:
            print(f"❌ Interface returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Interface not accessible: {e}")
        return False

def test_natural_language_command():
    """Test natural language command processing via API"""
    try:
        # Test with a simple automation-friendly site first
        test_command = "navigate to httpbin.org and take a screenshot"
        
        print(f"🧪 Testing natural language command: '{test_command}'")
        
        # Send command to the natural language endpoint
        response = requests.post(
            "http://127.0.0.1:7862/api/predict",
            json={
                "data": [test_command],
                "fn_index": 0  # Natural language command function
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Natural language command processed successfully")
            print(f"📄 Result: {result}")
            return True
        else:
            print(f"❌ Command failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Natural language test failed: {e}")
        return False

def test_turing_accessibility():
    """Test if turing.com is accessible via different methods"""
    print("🌐 Testing turing.com accessibility...")
    
    # Test with curl-like request
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get("https://turing.com", headers=headers, timeout=10)
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"🍪 Cookies received: {len(response.cookies)}")
        
        # Check for Incapsula protection
        if 'incap_ses' in response.cookies:
            print("🛡️  Incapsula protection detected")
        
        if response.status_code == 200:
            print("✅ turing.com is accessible via HTTP requests")
            return True
        else:
            print("❌ turing.com returned non-200 status")
            return False
            
    except Exception as e:
        print(f"❌ turing.com not accessible: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🧪 Enhanced Natural Language Automation System Tests")
    print("=" * 60)
    
    # Test 1: Interface availability
    print("\n1. Testing Gradio Interface...")
    interface_ok = test_gradio_interface()
    
    if not interface_ok:
        print("❌ Cannot proceed - interface not running")
        return
    
    # Test 2: turing.com accessibility
    print("\n2. Testing turing.com Accessibility...")
    turing_accessible = test_turing_accessibility()
    
    # Test 3: Natural language processing
    print("\n3. Testing Natural Language Processing...")
    nl_ok = test_natural_language_command()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Interface Running: {'✅' if interface_ok else '❌'}")
    print(f"   turing.com Access: {'✅' if turing_accessible else '❌'}")
    print(f"   Natural Language: {'✅' if nl_ok else '❌'}")
    
    if interface_ok and nl_ok:
        print("\n🎉 System is ready for automation!")
        if not turing_accessible:
            print("⚠️  turing.com has aggressive protection - may need proxy or alternative approach")
        print("\n💡 Suggested next steps:")
        print("   1. Test with automation-friendly sites first")
        print("   2. Use residential proxy for turing.com if needed")
        print("   3. Try the enhanced stealth configuration")
    else:
        print("\n💥 System needs troubleshooting before proceeding")

if __name__ == "__main__":
    main()
