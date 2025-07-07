#!/usr/bin/env python3
"""
Browser-use with local Ollama LLM (no API key required)
Requires Ollama to be installed and running locally
"""

import asyncio
from langchain_ollama import ChatOllama
from browser_use import Agent

async def browser_automation_with_local_llm():
    """
    Example using browser-use with local Ollama LLM
    
    Prerequisites:
    1. Install Ollama: https://ollama.ai/
    2. Pull a model: ollama pull qwen2.5:7b
    3. Install dependencies: pip install langchain-ollama browser-use
    """
    
    # Initialize local LLM (no API key needed)
    llm = ChatOllama(
        model="qwen2.5:7b",  # or any other model you have pulled
        num_ctx=32000,       # context window
        temperature=0.1
    )
    
    # Test LLM connection
    try:
        response = llm.invoke("Hello, can you help with browser automation?")
        print(f"LLM Response: {response.content}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Make sure Ollama is running and you have pulled a model")
        return
    
    # Create browser agent with local LLM
    agent = Agent(
        task="Go to google.com and search for 'local LLM browser automation'",
        llm=llm,
        use_vision=False  # Most local models don't support vision
    )
    
    try:
        # Run the agent
        result = await agent.run()
        print("Automation completed!")
        
        # Print results
        for action in result.action_results():
            if action.extracted_content:
                print(f"Extracted: {action.extracted_content}")
                
    except Exception as e:
        print(f"Error during automation: {e}")

if __name__ == "__main__":
    print("Browser automation with local Ollama LLM")
    print("Make sure Ollama is running with: ollama serve")
    print("And you have a model pulled: ollama pull qwen2.5:7b")
    asyncio.run(browser_automation_with_local_llm())
