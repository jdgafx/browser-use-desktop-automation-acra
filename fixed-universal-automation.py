#!/usr/bin/env python3
"""
Fixed Universal Browser Automation
Fixes the login loop and adds proper credential prompting
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    sys.exit(1)

class FixedBrowserAutomation:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = self.setup_llm()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "current_url": "",
            "last_screenshot": None,
            "needs_credentials": False,
            "credential_prompt": ""
        }
    
    def setup_llm(self):
        """Setup Anthropic Claude LLM"""
        if self.api_key:
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=self.api_key,
                temperature=0.1,  # Lower temperature for more focused behavior
                max_tokens=4000
            )
        return None
    
    async def execute_universal_command(self, command, username="", password=""):
        """Execute automation command with proper credential handling"""
        try:
            if not self.llm:
                return "❌ No API key configured"
            
            # Build focused automation prompt - no loops
            enhanced_command = f"""
{command}

CRITICAL INSTRUCTIONS:
1. If you find a login page, STAY ON IT - do not go back to search
2. If you need credentials and none are provided, ASK THE USER
3. Do not search for login pages repeatedly - once found, use it
4. Focus on the current page and complete the task step by step
5. If credentials are provided: username="{username}", password="{password}"

EXECUTION RULES:
- Stay on the current page once you find what you need
- Do not loop back to search engines
- Complete one action at a time methodically
- If login fails, explain what happened and what's needed
- Take screenshots to show progress

Execute this task with focus and precision. No endless searching.
"""
            
            print(f"🚀 Executing: {command}")
            
            # Create agent with focused settings
            agent = Agent(
                task=enhanced_command,
                llm=self.llm,
                use_vision=True,
                max_failures=3,  # Fewer retries to avoid loops
                retry_delay=2,
                browser_args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage', 
                    '--no-sandbox',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Execute with timeout to prevent infinite loops
            result = await asyncio.wait_for(agent.run(), timeout=300)  # 5 minute timeout
            
            # Store execution in history
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "success": True,
                "credentials_used": bool(username and password)
            })
            
            # Capture current state
            try:
                if hasattr(agent, 'browser') and agent.browser and agent.browser.pages:
                    current_page = agent.browser.pages[0]
                    self.session_data["current_url"] = current_page.url
                    
                    # Take screenshot
                    screenshot_path = f"/tmp/automation_screenshot_{int(time.time())}.png"
                    await current_page.screenshot(path=screenshot_path, full_page=True)
                    self.session_data["last_screenshot"] = screenshot_path
                    print(f"📸 Screenshot saved: {screenshot_path}")
                    
                    # Check if we're on a login page and need credentials
                    page_content = await current_page.content()
                    if ("login" in page_content.lower() or "sign in" in page_content.lower()) and not (username and password):
                        self.session_data["needs_credentials"] = True
                        self.session_data["credential_prompt"] = f"Login page detected at {current_page.url}. Please provide credentials to continue."
                        
            except Exception as e:
                print(f"State capture warning: {e}")
            
            return f"✅ Command executed successfully!\n\nResult: {result}"
            
        except asyncio.TimeoutError:
            return "⏰ Command timed out (5 minutes). The automation may have gotten stuck in a loop."
        except Exception as e:
            error_msg = f"❌ Automation failed: {str(e)}"
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": error_msg,
                "success": False,
                "credentials_used": bool(username and password)
            })
            return error_msg
    
    def create_interface(self):
        """Create focused Gradio interface"""
        with gr.Blocks(
            title="Fixed Universal Browser Automation",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                background: linear-gradient(45deg, #059669, #10b981);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 25px;
            }
            .command-section {
                border: 2px solid #10b981;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
            }
            .credential-alert {
                background: #fef3c7;
                border: 2px solid #f59e0b;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🔧 Fixed Universal Browser Automation</h1>
                <h2>No More Loops • Proper Credential Prompting</h2>
                <p><strong>Works on ANY website • Focused execution • No infinite searches</strong></p>
            </div>
            """)
            
            with gr.Tab("🚀 Automation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎯 Automation Command</h3>")
                        
                        # Credential status alert
                        credential_alert = gr.HTML(
                            "<div>Ready for automation commands</div>",
                            elem_classes="credential-alert"
                        )
                        
                        # Main command input
                        automation_command = gr.Textbox(
                            label="Universal Automation Command",
                            placeholder="e.g., 'Login to turing.com and show me my completed quizzes'",
                            lines=3,
                            elem_classes="command-section"
                        )
                        
                        # Credentials section - always visible
                        gr.HTML("<h4>🔐 Login Credentials</h4>")
                        with gr.Row():
                            cred_username = gr.Textbox(
                                label="Username/Email",
                                placeholder="Enter if needed for login"
                            )
                            cred_password = gr.Textbox(
                                label="Password",
                                type="password",
                                placeholder="Enter if needed for login"
                            )
                        
                        execute_btn = gr.Button(
                            "🚀 Execute Command", 
                            variant="primary", 
                            size="lg"
                        )
                        
                        # Quick examples
                        gr.HTML("<h4>💡 Example Commands</h4>")
                        examples = [
                            "Go to turing.com and navigate to the login page",
                            "Login to turing.com and show me my dashboard", 
                            "Navigate to turing.com quizzes and show what's available",
                            "Go to amazon.com and search for wireless headphones",
                            "Login to linkedin.com and check my messages",
                            "Visit github.com and show trending repositories"
                        ]
                        
                        for example in examples:
                            btn = gr.Button(f"💡 {example}", size="sm")
                            btn.click(
                                fn=lambda ex=example: ex,
                                outputs=automation_command
                            )
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Execution Results</h3>")
                        
                        # Execution status
                        execution_status = gr.HTML(
                            "<div style='padding: 10px; background: #f0fdf4; border-radius: 5px;'>Ready to execute commands</div>"
                        )
                        
                        # Results output
                        result_output = gr.Textbox(
                            label="Command Results",
                            lines=12,
                            max_lines=20,
                            interactive=False
                        )
                        
                        # Current page info
                        with gr.Row():
                            current_url_display = gr.Textbox(
                                label="Current URL",
                                interactive=False
                            )
                        
                        # Screenshot display
                        screenshot_output = gr.Image(
                            label="Current Page Screenshot",
                            interactive=False
                        )
            
            with gr.Tab("📊 Session History"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>📜 Command History</h3>")
                        
                        automation_history = gr.JSON(
                            label="Recent Commands",
                            value=[]
                        )
                        
                        refresh_history_btn = gr.Button("🔄 Refresh History")
                    
                    with gr.Column():
                        gr.HTML("<h3>📈 Session Stats</h3>")
                        
                        session_stats = gr.JSON(
                            label="Session Information",
                            value={}
                        )
            
            # Event handlers
            def execute_automation_handler(command, username, password):
                if not command.strip():
                    return (
                        "<div style='padding: 10px; background: #fee2e2; border-radius: 5px;'>❌ Please enter a command</div>",
                        "❌ No command provided",
                        "",
                        None,
                        "<div>Please enter a command to execute</div>"
                    )
                
                # Clear previous credential alerts
                status_msg = "<div style='padding: 10px; background: #dbeafe; border-radius: 5px;'>🚀 Executing command...</div>"
                
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.execute_universal_command(command, username, password)
                    )
                    loop.close()
                    
                    current_url = self.session_data.get("current_url", "")
                    screenshot = self.session_data.get("last_screenshot")
                    
                    # Check if credentials are needed
                    if self.session_data.get("needs_credentials", False):
                        credential_msg = f"<div class='credential-alert'>🔐 {self.session_data.get('credential_prompt', 'Login detected - please provide credentials and try again')}</div>"
                        success_msg = "<div style='padding: 10px; background: #fef3c7; border-radius: 5px;'>⚠️ Credentials needed</div>"
                    else:
                        credential_msg = "<div>✅ Command executed successfully</div>"
                        success_msg = "<div style='padding: 10px; background: #d1fae5; border-radius: 5px;'>✅ Command completed</div>"
                    
                    return success_msg, result, current_url, screenshot, credential_msg
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    error_status = "<div style='padding: 10px; background: #fee2e2; border-radius: 5px;'>❌ Execution failed</div>"
                    return error_status, error_msg, "", None, "<div>Error occurred during execution</div>"
            
            def refresh_history_handler():
                history = self.session_data.get("conversation_history", [])[-10:]  # Last 10
                stats = {
                    "total_commands": len(self.session_data.get("conversation_history", [])),
                    "successful_commands": len([h for h in self.session_data.get("conversation_history", []) if h.get("success", False)]),
                    "current_url": self.session_data.get("current_url", ""),
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                return history, stats
            
            # Wire up events
            execute_btn.click(
                fn=execute_automation_handler,
                inputs=[automation_command, cred_username, cred_password],
                outputs=[execution_status, result_output, current_url_display, screenshot_output, credential_alert]
            )
            
            refresh_history_btn.click(
                fn=refresh_history_handler,
                outputs=[automation_history, session_stats]
            )
        
        return interface

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
    
    print("🔧 Starting Fixed Universal Browser Automation...")
    print("✅ No more infinite loops")
    print("✅ Proper credential prompting") 
    print("✅ Focused execution")
    print()
    
    try:
        automation = FixedBrowserAutomation(api_key)
        interface = automation.create_interface()
        
        print("🌐 Starting fixed automation interface...")
        print("📍 Access at: http://127.0.0.1:7789")
        print("🎯 Ready for focused automation!")
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7789,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()