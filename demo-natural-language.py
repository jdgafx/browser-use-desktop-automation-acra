#!/usr/bin/env python3
"""
Demo of Natural Language Browser Automation
Shows how the natural language processing works
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
import importlib.util

def load_module(module_name, file_path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load natural language processor
nlp_module = load_module("natural_language_processor", "natural-language-processor.py")
NaturalLanguageProcessor = nlp_module.NaturalLanguageProcessor

def demo_natural_language_processing():
    """Demo the natural language processing capabilities"""
    print("🎭 Natural Language Browser Automation Demo")
    print("=" * 50)
    
    # Initialize processor
    nlp = NaturalLanguageProcessor()
    
    # Test commands
    test_commands = [
        "go to google.com",
        "click on the search button",
        "type 'python tutorials' in the search box",
        "take a screenshot",
        "scroll down",
        "wait 5 seconds",
        "search for 'machine learning'",
        "login to the website",
        "fill the form with my details",
        "go to youtube.com and search for 'playwright tutorial'",
        "click on login button and then enter my credentials",
        "navigate to github.com, click on sign in, and wait for the page to load"
    ]
    
    print("\n🗣️ Processing Natural Language Commands:")
    print("-" * 40)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Command: '{command}'")
        
        # Process the command
        actions = nlp.process_command(command)
        
        if actions:
            print(f"   ✅ Parsed into {len(actions)} action(s):")
            for j, action in enumerate(actions, 1):
                print(f"      {j}. {action.action_type.value}: {action.description}")
                if action.target:
                    print(f"         Target: {action.target}")
                if action.value:
                    print(f"         Value: {action.value}")
        else:
            print("   ❌ Could not parse command")
            suggestions = nlp.get_action_suggestions(command)
            if suggestions:
                print(f"   💡 Suggestions: {', '.join(suggestions[:3])}")
    
    print("\n" + "=" * 50)
    print("🎯 Natural Language Features:")
    print("• Understands compound commands (with 'and', 'then')")
    print("• Supports navigation, clicking, typing, screenshots")
    print("• Handles login, form filling, searching")
    print("• Provides suggestions for unclear commands")
    print("• No AI/API keys required - uses pattern matching")
    
    print("\n🚀 Ready for browser automation!")
    print("Start the main interface with: ./start_playwright_enhanced.sh")

if __name__ == "__main__":
    demo_natural_language_processing()
