#!/usr/bin/env python3
"""
Test the enhanced interface with natural language commands
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_natural_language():
    """Test natural language command processing"""
    print("🧪 Testing Natural Language Interface...")
    
    try:
        # Import the main automation engine
        from playwright_enhanced_automation import automation_engine
        
        print("✅ Automation engine imported successfully")
        
        # Test natural language command processing
        test_commands = [
            "go to google.com",
            "take a screenshot",
            "scroll down"
        ]
        
        print("\n🗣️ Testing Natural Language Commands:")
        for command in test_commands:
            print(f"\nTesting: '{command}'")
            try:
                result = await automation_engine.execute_natural_language_command(command)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n✅ Natural language testing complete!")
        
    except Exception as e:
        print(f"❌ Error testing interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_natural_language())
