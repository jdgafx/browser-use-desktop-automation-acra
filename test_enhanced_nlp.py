#!/usr/bin/env python3
"""
Test Enhanced Natural Language Processing
"""

import importlib.util

# Load the natural language processor module
spec = importlib.util.spec_from_file_location("natural_language_processor", "natural-language-processor.py")
nlp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nlp_module)
NaturalLanguageProcessor = nlp_module.NaturalLanguageProcessor

def test_enhanced_nlp():
    """Test the enhanced natural language processor"""
    processor = NaturalLanguageProcessor()
    
    # Test the complex command from the user
    complex_command = "navigate to turing.com and login with google to the enigmatic account, find my quizzes, see what i passed, then take the rest and pass them 100%, we need to take them all please"
    
    print("🧪 Testing Enhanced Natural Language Processing")
    print("=" * 60)
    print(f"Input: {complex_command}")
    print("=" * 60)
    
    actions = processor.process_command(complex_command)
    
    print(f"✅ Parsed {len(actions)} actions:")
    print()
    
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action.action_type.value.upper()}")
        print(f"   Target: {action.target}")
        print(f"   Value: {action.value}")
        print(f"   Description: {action.description}")
        print()
    
    # Test other complex commands
    test_commands = [
        "go to github.com, click on sign in, enter my credentials, then navigate to my repositories",
        "search for python tutorials, click on the first result, take a screenshot",
        "complete all my assignments with 100% score",
        "find my test results and see what I passed"
    ]
    
    print("🔬 Testing Additional Complex Commands:")
    print("=" * 60)
    
    for cmd in test_commands:
        print(f"Command: {cmd}")
        actions = processor.process_command(cmd)
        print(f"Actions: {len(actions)} - {[a.action_type.value for a in actions]}")
        print()

if __name__ == "__main__":
    test_enhanced_nlp()
