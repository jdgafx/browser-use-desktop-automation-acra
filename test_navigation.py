#!/usr/bin/env python3
"""
Test Navigation with Enhanced Timeouts
"""

import asyncio
import importlib.util
from playwright.async_api import async_playwright

# Load the natural language processor module
spec = importlib.util.spec_from_file_location("natural_language_processor", "natural-language-processor.py")
nlp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nlp_module)
NaturalLanguageProcessor = nlp_module.NaturalLanguageProcessor

# Load the executor module
spec = importlib.util.spec_from_file_location("natural_language_executor", "natural-language-executor.py")
executor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(executor_module)
NaturalLanguageExecutor = executor_module.NaturalLanguageExecutor

async def test_navigation():
    """Test navigation with enhanced timeouts"""
    print("🧪 Testing Navigation with Enhanced Timeouts")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create executor
        executor = NaturalLanguageExecutor(page)
        
        # Test navigation to turing.com
        print("🌐 Testing navigation to turing.com...")
        
        # Create navigation action
        AutomationAction = nlp_module.AutomationAction
        ActionType = nlp_module.ActionType
        nav_action = AutomationAction(
            action_type=ActionType.NAVIGATE,
            target="https://turing.com",
            description="Navigate to turing.com"
        )
        
        try:
            result = await executor._execute_navigate(nav_action)
            
            if result['success']:
                print(f"✅ Navigation successful!")
                print(f"   URL: {result['url']}")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Navigation failed!")
                print(f"   Error: {result['message']}")
                
        except Exception as e:
            print(f"❌ Exception during navigation: {str(e)}")
        
        # Wait a bit to see the page
        await asyncio.sleep(3)
        
        # Close browser
        await browser.close()
        print("\n🏁 Test completed")

if __name__ == "__main__":
    asyncio.run(test_navigation())
