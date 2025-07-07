#!/usr/bin/env python3
"""
Manual Browser Control Interface
Provides step-by-step browser control without requiring AI/LLM
"""

import asyncio
import gradio as gr
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any
import json

class ManualBrowserController:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    async def start_browser(self, headless: bool = False):
        """Start the browser session"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            return "Browser started successfully!"
        except Exception as e:
            return f"Error starting browser: {e}"
    
    async def navigate_to_url(self, url: str):
        """Navigate to a specific URL"""
        if not self.page:
            return "Browser not started. Please start browser first."
        
        try:
            await self.page.goto(url)
            title = await self.page.title()
            current_url = self.page.url
            return f"Navigated to: {current_url}\nPage title: {title}"
        except Exception as e:
            return f"Error navigating to {url}: {e}"
    
    async def click_element(self, selector: str):
        """Click an element by CSS selector"""
        if not self.page:
            return "Browser not started."
        
        try:
            await self.page.click(selector)
            return f"Clicked element: {selector}"
        except Exception as e:
            return f"Error clicking {selector}: {e}"
    
    async def fill_input(self, selector: str, text: str):
        """Fill an input field"""
        if not self.page:
            return "Browser not started."
        
        try:
            await self.page.fill(selector, text)
            return f"Filled '{selector}' with: {text}"
        except Exception as e:
            return f"Error filling {selector}: {e}"
    
    async def get_page_info(self):
        """Get current page information"""
        if not self.page:
            return "Browser not started."
        
        try:
            title = await self.page.title()
            url = self.page.url
            
            # Get visible elements
            buttons = await self.page.locator('button').all_text_contents()
            links = await self.page.locator('a').all_text_contents()
            inputs = await self.page.locator('input').count()
            
            info = f"""
Current URL: {url}
Page Title: {title}
Buttons found: {len(buttons)}
Links found: {len(links)}
Input fields: {inputs}

First 5 buttons: {buttons[:5]}
First 5 links: {links[:5]}
"""
            return info
        except Exception as e:
            return f"Error getting page info: {e}"
    
    async def take_screenshot(self):
        """Take a screenshot of current page"""
        if not self.page:
            return "Browser not started.", None
        
        try:
            screenshot_path = "current_page.png"
            await self.page.screenshot(path=screenshot_path)
            return f"Screenshot saved to {screenshot_path}", screenshot_path
        except Exception as e:
            return f"Error taking screenshot: {e}", None
    
    async def execute_javascript(self, js_code: str):
        """Execute JavaScript on the page"""
        if not self.page:
            return "Browser not started."
        
        try:
            result = await self.page.evaluate(js_code)
            return f"JavaScript executed. Result: {result}"
        except Exception as e:
            return f"Error executing JavaScript: {e}"
    
    async def close_browser(self):
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            return "Browser closed successfully!"
        except Exception as e:
            return f"Error closing browser: {e}"

# Global controller instance
controller = ManualBrowserController()

# Gradio interface functions
async def start_browser_ui(headless):
    return await controller.start_browser(headless)

async def navigate_ui(url):
    return await controller.navigate_to_url(url)

async def click_ui(selector):
    return await controller.click_element(selector)

async def fill_ui(selector, text):
    return await controller.fill_input(selector, text)

async def page_info_ui():
    return await controller.get_page_info()

async def screenshot_ui():
    message, path = await controller.take_screenshot()
    return message, path

async def js_ui(code):
    return await controller.execute_javascript(code)

async def close_ui():
    return await controller.close_browser()

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Manual Browser Controller") as interface:
        gr.Markdown("# Manual Browser Controller")
        gr.Markdown("Control a browser manually without AI - step by step automation")
        
        with gr.Tab("Browser Control"):
            with gr.Row():
                start_btn = gr.Button("Start Browser")
                headless_check = gr.Checkbox(label="Headless Mode", value=False)
                close_btn = gr.Button("Close Browser")
            
            start_output = gr.Textbox(label="Status", lines=2)
            
            with gr.Row():
                url_input = gr.Textbox(label="URL to Navigate", placeholder="https://example.com")
                nav_btn = gr.Button("Navigate")
            
            nav_output = gr.Textbox(label="Navigation Result", lines=3)
        
        with gr.Tab("Page Interaction"):
            with gr.Row():
                selector_input = gr.Textbox(label="CSS Selector", placeholder="button, #id, .class")
                click_btn = gr.Button("Click Element")
            
            click_output = gr.Textbox(label="Click Result", lines=2)
            
            with gr.Row():
                fill_selector = gr.Textbox(label="Input Selector", placeholder="input[name='search']")
                fill_text = gr.Textbox(label="Text to Fill", placeholder="Enter text here")
                fill_btn = gr.Button("Fill Input")
            
            fill_output = gr.Textbox(label="Fill Result", lines=2)
        
        with gr.Tab("Page Analysis"):
            info_btn = gr.Button("Get Page Info")
            info_output = gr.Textbox(label="Page Information", lines=10)
            
            screenshot_btn = gr.Button("Take Screenshot")
            screenshot_output = gr.Textbox(label="Screenshot Status")
            screenshot_image = gr.Image(label="Current Page Screenshot")
        
        with gr.Tab("JavaScript"):
            js_input = gr.Textbox(
                label="JavaScript Code", 
                placeholder="document.title", 
                lines=5
            )
            js_btn = gr.Button("Execute JavaScript")
            js_output = gr.Textbox(label="JavaScript Result", lines=5)
        
        # Event handlers
        start_btn.click(start_browser_ui, inputs=[headless_check], outputs=[start_output])
        nav_btn.click(navigate_ui, inputs=[url_input], outputs=[nav_output])
        click_btn.click(click_ui, inputs=[selector_input], outputs=[click_output])
        fill_btn.click(fill_ui, inputs=[fill_selector, fill_text], outputs=[fill_output])
        info_btn.click(page_info_ui, outputs=[info_output])
        screenshot_btn.click(screenshot_ui, outputs=[screenshot_output, screenshot_image])
        js_btn.click(js_ui, inputs=[js_input], outputs=[js_output])
        close_btn.click(close_ui, outputs=[start_output])
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=False, server_name="0.0.0.0", server_port=7860)
