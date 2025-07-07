#!/usr/bin/env python3
"""
Working Browser-Use Interface
Simple, reliable interface for browser automation with Anthropic Claude
Optimized for Turing.com workflows
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Browser-use imports
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    print("Please ensure browser-use is installed: pip install browser-use")
    sys.exit(1)

class WorkingBrowserInterface:
    def __init__(self):
        self.llm = self.setup_anthropic()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "current_url": "",
            "last_screenshot": None
        }
        self.load_env_vars()
    
    def load_env_vars(self):
        """Load environment variables from .env files"""
        env_files = [
            Path.home() / "browser-use-complete" / "web-ui" / ".env",
            Path.cwd() / ".env"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.strip() and not line.startswith("#") and "=" in line:
                            key, value = line.strip().split("=", 1)
                            os.environ[key] = value
                print(f"✅ Loaded environment from {env_file}")
                break
    
    def setup_anthropic(self):
        """Setup Anthropic Claude LLM"""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            return ChatAnthropic(
                model="claude-3-haiku-20240307",  # Fast and efficient
                api_key=anthropic_key,
                temperature=0.3,
                max_tokens=4000
            )
        else:
            print("⚠️  No Anthropic API key found. Please configure it.")
            return None
    
    async def execute_browser_command(self, command, credentials_username="", credentials_password=""):
        """Execute browser automation command"""
        try:
            if not self.llm:
                return "❌ No Anthropic API key configured. Please add it in settings."
            
            # Build enhanced prompt for Turing.com workflows
            enhanced_command = f"""
{command}

SPECIAL INSTRUCTIONS FOR TURING.COM AND COMPLEX WORKFLOWS:
1. If this involves turing.com or any login, handle authentication carefully
2. For turing.com quizzes/assessments:
   - Read questions thoroughly and provide accurate answers
   - Take time to understand what is being asked
   - Provide the best possible answers to achieve high scores
3. If credentials are provided: username="{credentials_username}", password="{credentials_password}"
4. If no credentials provided but login is needed, describe what login fields are available
5. Take screenshots at key points to show progress
6. Handle multi-step workflows methodically and carefully
7. Wait for pages to load completely before proceeding
8. Provide detailed feedback on each step of the process
9. If you encounter CAPTCHAs or 2FA, describe what you see and ask for guidance

Execute this command with attention to detail and provide comprehensive feedback.
"""
            
            print(f"🚀 Executing browser command: {command}")
            
            # Create agent with enhanced settings
            agent = Agent(
                task=enhanced_command,
                llm=self.llm,
                use_vision=True,
                max_failures=3,
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
            
            # Execute the command
            result = await agent.run()
            
            # Store result in session
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "credentials_used": bool(credentials_username)
            })
            
            # Try to get current URL and take screenshot
            try:
                if hasattr(agent, 'browser') and agent.browser:
                    pages = agent.browser.pages
                    if pages:
                        current_page = pages[0]
                        self.session_data["current_url"] = current_page.url
                        
                        # Take screenshot
                        screenshot_path = f"/tmp/browser_screenshot_{int(time.time())}.png"
                        await current_page.screenshot(path=screenshot_path)
                        self.session_data["last_screenshot"] = screenshot_path
                        print(f"📸 Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"Screenshot/URL warning: {e}")
            
            success_msg = "✅ Browser command executed successfully!"
            result_msg = f"Result: {result}"
            
            return f"{success_msg}\n\n{result_msg}"
            
        except Exception as e:
            error_msg = f"❌ Command execution failed: {str(e)}"
            print(error_msg)
            return error_msg
    
    def save_api_key(self, api_key):
        """Save API key and reinitialize LLM"""
        if api_key and api_key.strip():
            os.environ["ANTHROPIC_API_KEY"] = api_key.strip()
            self.llm = self.setup_anthropic()
            return "✅ API key saved and LLM configured"
        else:
            return "❌ Please enter a valid API key"
    
    def store_credentials(self, service, username, password):
        """Store credentials for use in automation"""
        if service and username and password:
            self.session_data["credentials"][service] = {
                "username": username,
                "password": password,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return f"✅ Credentials stored for {service}"
        else:
            return "❌ Please provide service name, username, and password"
    
    def get_stored_credentials(self, service):
        """Get stored credentials for a service"""
        if service in self.session_data["credentials"]:
            creds = self.session_data["credentials"][service]
            return creds["username"], creds["password"]
        return "", ""
    
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(
            title="Browser-Use AI: Turing.com Automation",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                background: linear-gradient(45deg, #1e40af, #3b82f6);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
            }
            .command-section {
                border: 2px solid #3b82f6;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
            .success {
                background: #d1fae5;
                border-left: 4px solid #10b981;
                padding: 10px;
                border-radius: 5px;
            }
            .error {
                background: #fee2e2;
                border-left: 4px solid #ef4444;
                padding: 10px;
                border-radius: 5px;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🤖 Browser-Use AI: Turing.com Automation</h1>
                <h2>Anthropic Claude + Advanced Browser Automation</h2>
                <p><strong>Optimized for complex workflows, authentication, and quiz completion</strong></p>
            </div>
            """)
            
            with gr.Tab("🚀 Browser Automation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎯 Browser Commands</h3>")
                        
                        # Main command input
                        command_input = gr.Textbox(
                            label="Enter Browser Command",
                            placeholder="e.g., 'log into my turing.com account and show me available quizzes'",
                            lines=4,
                            elem_classes="command-section"
                        )
                        
                        # Credentials section
                        gr.HTML("<h4>🔐 Credentials (Optional)</h4>")
                        with gr.Row():
                            cred_username = gr.Textbox(
                                label="Username/Email",
                                placeholder="Enter username if needed for this command"
                            )
                            cred_password = gr.Textbox(
                                label="Password",
                                type="password",
                                placeholder="Enter password if needed for this command"
                            )
                        
                        execute_btn = gr.Button("🚀 Execute Command", variant="primary", size="lg")
                        
                        # Quick command templates
                        gr.HTML("<h4>📋 Quick Templates</h4>")
                        templates = [
                            "Go to google.com and search for browser automation",
                            "Navigate to turing.com and show me the login page",
                            "Log into my turing.com account and navigate to dashboard",
                            "Go to turing.com quizzes and show me available assessments",
                            "Navigate to turing.com profile and show my completed tests",
                            "Search for 'Python developer jobs' on turing.com",
                            "Take a screenshot of the current page"
                        ]
                        
                        for i, template in enumerate(templates):
                            btn = gr.Button(f"{i+1}. {template}", size="sm")
                            btn.click(
                                fn=lambda t=template: t,
                                outputs=command_input
                            )
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Execution Results</h3>")
                        
                        result_output = gr.Textbox(
                            label="Command Results",
                            lines=15,
                            max_lines=25,
                            interactive=False
                        )
                        
                        # Current session info
                        gr.HTML("<h4>🌐 Current Session</h4>")
                        current_url = gr.Textbox(
                            label="Current URL",
                            interactive=False
                        )
                        
                        # Screenshot display
                        screenshot_display = gr.Image(
                            label="Latest Screenshot",
                            interactive=False
                        )
            
            with gr.Tab("🔐 Credentials & Settings"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>🔑 API Configuration</h3>")
                        
                        api_key_input = gr.Textbox(
                            label="Anthropic API Key",
                            type="password",
                            placeholder="Enter your Anthropic API key"
                        )
                        
                        save_key_btn = gr.Button("💾 Save API Key")
                        api_status = gr.HTML("API key status: Not configured")
                        
                        gr.HTML("<h3>🔐 Credential Storage</h3>")
                        
                        service_name = gr.Textbox(
                            label="Service Name",
                            placeholder="e.g., turing, github, linkedin"
                        )
                        
                        stored_username = gr.Textbox(
                            label="Username/Email",
                            placeholder="Username for this service"
                        )
                        
                        stored_password = gr.Textbox(
                            label="Password",
                            type="password",
                            placeholder="Password for this service"
                        )
                        
                        store_creds_btn = gr.Button("💾 Store Credentials")
                        creds_status = gr.HTML("No credentials stored")
                    
                    with gr.Column():
                        gr.HTML("<h3>📊 Session Data</h3>")
                        
                        session_display = gr.JSON(
                            label="Current Session",
                            value={}
                        )
                        
                        refresh_session_btn = gr.Button("🔄 Refresh Session Data")
                        
                        gr.HTML("<h3>📜 Command History</h3>")
                        
                        history_display = gr.JSON(
                            label="Execution History",
                            value=[]
                        )
            
            # Event handlers
            def execute_command_handler(command, username, password):
                if not command.strip():
                    return "❌ Please enter a command", "", None
                
                try:
                    # Run async command
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.execute_browser_command(command, username, password)
                    )
                    loop.close()
                    
                    # Return result, current URL, and screenshot
                    current_url_val = self.session_data.get("current_url", "")
                    screenshot_path = self.session_data.get("last_screenshot")
                    
                    return result, current_url_val, screenshot_path
                    
                except Exception as e:
                    return f"❌ Error: {str(e)}", "", None
            
            def save_api_key_handler(api_key):
                result = self.save_api_key(api_key)
                if "✅" in result:
                    return result, "<div class='success'>✅ API key configured successfully</div>"
                else:
                    return result, "<div class='error'>❌ Failed to configure API key</div>"
            
            def store_credentials_handler(service, username, password):
                return self.store_credentials(service, username, password)
            
            def refresh_session_handler():
                # Remove sensitive data from display
                display_data = dict(self.session_data)
                if "credentials" in display_data:
                    display_data["credentials"] = {
                        k: {"username": v["username"], "stored": True}
                        for k, v in display_data["credentials"].items()
                    }
                return display_data, display_data.get("conversation_history", [])
            
            # Wire up events
            execute_btn.click(
                fn=execute_command_handler,
                inputs=[command_input, cred_username, cred_password],
                outputs=[result_output, current_url, screenshot_display]
            )
            
            save_key_btn.click(
                fn=save_api_key_handler,
                inputs=api_key_input,
                outputs=[creds_status, api_status]
            )
            
            store_creds_btn.click(
                fn=store_credentials_handler,
                inputs=[service_name, stored_username, stored_password],
                outputs=creds_status
            )
            
            refresh_session_btn.click(
                fn=refresh_session_handler,
                outputs=[session_display, history_display]
            )
        
        return interface

def main():
    """Main function"""
    print("🚀 Starting Browser-Use AI Interface...")
    print("🤖 Using Anthropic Claude for AI reasoning")
    print("🎯 Optimized for Turing.com workflows and complex automation")
    print("🔐 Supports credential management and multi-step authentication")
    print()
    
    try:
        # Create browser interface
        browser_interface = WorkingBrowserInterface()
        
        # Create and launch interface
        interface = browser_interface.create_interface()
        
        print("🌐 Starting web interface...")
        print("📍 Access at: http://127.0.0.1:7788")
        print("💡 Features:")
        print("   • Complex Turing.com workflow automation")
        print("   • Credential management and secure storage")
        print("   • Screenshot capture and progress tracking")
        print("   • Multi-step authentication handling")
        print("   • Quiz and assessment completion")
        print()
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7788,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error starting interface: {e}")

if __name__ == "__main__":
    main()