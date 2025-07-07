#!/usr/bin/env python3
"""
Direct Playwright browser automation without AI/LLM
This provides scripted browser automation without requiring API keys
"""

import asyncio
from playwright.async_api import async_playwright

async def direct_browser_automation():
    """Example of direct Playwright usage for browser automation"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to a website
            await page.goto('https://www.google.com')
            
            # Find search box and type
            search_box = page.locator('input[name="q"]')
            await search_box.fill('browser automation')
            
            # Press Enter to search
            await search_box.press('Enter')
            
            # Wait for results
            await page.wait_for_selector('div#search')
            
            # Get page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Take screenshot
            await page.screenshot(path='search_results.png')
            
            # Extract some data
            results = await page.locator('h3').all_text_contents()
            print("Search results:")
            for i, result in enumerate(results[:5], 1):
                print(f"{i}. {result}")
                
        finally:
            await browser.close()

async def form_automation_example():
    """Example of form filling automation"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to a form (example)
            await page.goto('https://httpbin.org/forms/post')
            
            # Fill form fields
            await page.fill('input[name="custname"]', 'John Doe')
            await page.fill('input[name="custtel"]', '555-1234')
            await page.fill('input[name="custemail"]', 'john@example.com')
            await page.select_option('select[name="size"]', 'medium')
            
            # Submit form
            await page.click('input[type="submit"]')
            
            # Wait for response
            await page.wait_for_load_state('networkidle')
            
            print("Form submitted successfully!")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    print("Running direct Playwright automation examples...")
    asyncio.run(direct_browser_automation())
    asyncio.run(form_automation_example())
