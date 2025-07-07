#!/usr/bin/env python3
"""
Enhanced Browser-Use Interface
Optimized for complex workflows like Turing.com login, navigation, and quiz completion
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add the web-ui directory to Python path
web_ui_path = Path.home() / "browser-use-complete" / "web-ui"
if web_ui_path.exists():
    sys.path.insert(0, str(web_ui_path))

try:
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI, ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Installing browser-use...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "browser-use"])
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI, ChatAnthropic

# Global state
current_agent = None
session_data = {
    "credentials": {},
    "current_url": "",
    "quiz_data": [],
    "selected_quizzes": [],
    "conversation_history": []
}

def load_env_vars():
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

def get_llm(provider="openai"):
    """Get LLM instance with enhanced settings for complex workflows"""
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    }
    
    if provider == "openai" and api_keys["openai"] and api_keys["openai"] != "your_openai_api_key_here":
        return ChatOpenAI(
            model="gpt-4", 
            api_key=api_keys["openai"],
            temperature=0.3,  # Lower temperature for more consistent behavior
            max_tokens=4000
        )
    elif provider == "anthropic" and api_keys["anthropic"] and api_keys["anthropic"] != "your_anthropic_api_key_here":
        return ChatAnthropic(
            model="claude-3-sonnet-20240229", 
            api_key=api_keys["anthropic"],
            temperature=0.3,
            max_tokens=4000
        )
    else:
        print("⚠️  No valid API key found. Using demo mode.")
        return ChatOpenAI(model="gpt-3.5-turbo", api_key="demo", base_url="http://localhost:1234/v1")

async def execute_complex_workflow(command: str, provider: str = "openai", credentials: Dict = None) -> tuple[str, str, str]:
    """Execute complex multi-step workflows with credential handling"""
    global current_agent, session_data
    
    try:
        llm = get_llm(provider)
        
        # Enhanced task prompt for complex workflows
        enhanced_task = f"""
{command}

IMPORTANT INSTRUCTIONS:
1. If you need credentials (username/password), ask the user to provide them
2. Handle multi-step authentication flows carefully
3. When navigating to quizzes or tests, provide detailed information about what's available
4. For quiz completion, read questions carefully and provide accurate answers
5. Take screenshots at key points to show progress
6. If you encounter multiple choices, describe them clearly for user selection
7. Be methodical and careful with form submissions
8. Wait for pages to load completely before proceeding

Available credentials in session: {list(session_data['credentials'].keys()) if session_data['credentials'] else 'None'}
"""
        
        # Create agent with enhanced settings for complex workflows
        agent = Agent(
            task=enhanced_task,
            llm=llm,
            use_vision=True,
            max_failures=5,  # Allow more retries for complex workflows
            retry_delay=2,   # Longer delay between retries
            # Enhanced browser settings
            browser_args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        )
        
        current_agent = agent
        
        print(f"🚀 Executing complex workflow: {command}")
        
        # Execute with progress tracking
        result = await agent.run()
        
        # Store session data
        session_data["conversation_history"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "command": command,
            "result": str(result),
            "provider": provider
        })
        
        # Take final screenshot
        screenshot_path = None
        try:
            if agent.browser:
                screenshot_path = f"/tmp/workflow_screenshot_{int(time.time())}.png"
                # Get current page info
                page = agent.browser.pages[0] if agent.browser.pages else None
                if page:
                    await page.screenshot(path=screenshot_path)
                    session_data["current_url"] = page.url
        except Exception as e:
            print(f"Screenshot warning: {e}")
        
        success_msg = f"✅ Complex workflow executed successfully"
        result_msg = f"Result: {result}"
        screenshot_msg = f"Screenshot saved: {screenshot_path}" if screenshot_path else "No screenshot available"
        
        return success_msg, result_msg, screenshot_msg
        
    except Exception as e:
        error_msg = f"❌ Workflow execution failed: {str(e)}"
        print(error_msg)
        return error_msg, f"Error details: {str(e)}", "No screenshot due to error"

def handle_credential_input(username: str, password: str, service: str = "turing"):
    """Store credentials securely in session"""
    if username and password:
        session_data["credentials"][service] = {
            "username": username,
            "password": password,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return f"✅ Credentials stored for {service}"
    return "❌ Please provide both username and password"

def create_enhanced_interface():
    """Create enhanced Gradio interface for complex workflows"""
    
    with gr.Blocks(
        title="Browser-Use AI: Complex Workflow Automation",
        theme=gr.themes.Soft(),
        css="""
        .workflow-container {
            border: 2px solid #3b82f6;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .credential-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
        }
        .status-success {
            background: #d1fae5;
            border-left: 4px solid #10b981;
            padding: 10px;
        }
        .status-error {
            background: #fee2e2;
            border-left: 4px solid #ef4444;
            padding: 10px;
        }
        """
    ) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(45deg, #1e3a8a, #7c3aed); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🚀 Browser-Use AI: Complex Workflow Automation</h1>
            <h2>Turing.com Login, Quiz Navigation & Completion</h2>
            <p><strong>Handles authentication, navigation, decision-making, and task completion</strong></p>
        </div>
        """)
        
        with gr.Tab("🎯 Workflow Execution"):
            with gr.Row():
                with gr.Column(scale=1):
                    # Main command input
                    gr.HTML("<h3>🧠 Complex Workflow Command</h3>")
                    workflow_command = gr.Textbox(
                        label="Enter your complex workflow",
                        placeholder="e.g., 'log into my turing.com account, navigate to quizzes, show me available ones, then complete the selected quizzes with 100%'",
                        lines=4,
                        elem_classes="workflow-container"
                    )
                    
                    provider_select = gr.Radio(
                        choices=["openai", "anthropic"],
                        value="openai",
                        label="AI Provider"
                    )
                    
                    execute_btn = gr.Button("🚀 Execute Workflow", variant="primary", size="lg")
                    
                    # Credential management
                    gr.HTML("<h3>🔐 Credential Management</h3>")
                    with gr.Group(elem_classes="credential-box"):
                        service_name = gr.Textbox(
                            label="Service Name",
                            value="turing",
                            placeholder="e.g., turing, github, etc."
                        )
                        username_input = gr.Textbox(
                            label="Username/Email",
                            placeholder="Enter your username or email"
                        )
                        password_input = gr.Textbox(
                            label="Password",
                            type="password",
                            placeholder="Enter your password"
                        )
                        store_creds_btn = gr.Button("💾 Store Credentials", variant="secondary")
                    
                    # Quick workflow templates
                    gr.HTML("<h3>📋 Quick Templates</h3>")
                    templates = [
                        "Log into my turing.com account and show me available quizzes",
                        "Navigate to turing.com quizzes, let me select which ones to complete, then pass them with 100%", 
                        "Go to turing.com, login with my credentials, check my profile and completed assessments",
                        "Access turing.com dashboard, find new available tests, and show me the details",
                        "Complete all pending turing.com assessments with perfect scores"
                    ]
                    
                    for i, template in enumerate(templates):
                        gr.Button(
                            f"Template {i+1}: {template[:60]}...",
                            size="sm"
                        ).click(
                            fn=lambda t=template: t,
                            outputs=workflow_command
                        )
                
                with gr.Column(scale=2):
                    # Results area
                    gr.HTML("<h3>📊 Workflow Results</h3>")
                    result_status = gr.HTML("<div class='status-success'>Ready to execute workflows</div>")
                    
                    result_output = gr.Textbox(
                        label="Execution Status",
                        lines=6,
                        max_lines=10,
                        interactive=False
                    )
                    
                    detail_output = gr.Textbox(
                        label="Detailed Results",
                        lines=8,
                        max_lines=15,
                        interactive=False
                    )
                    
                    screenshot_info = gr.Textbox(
                        label="Screenshot Info",
                        lines=2,
                        interactive=False
                    )
        
        with gr.Tab("📊 Session Data"):
            with gr.Row():
                with gr.Column():
                    gr.HTML("<h3>🔑 Stored Credentials</h3>")
                    credentials_display = gr.JSON(
                        label="Current Session Credentials",
                        value={}
                    )
                    
                    gr.HTML("<h3>🌐 Current Session</h3>")
                    session_display = gr.JSON(
                        label="Session Information",
                        value=session_data
                    )
                
                with gr.Column():
                    gr.HTML("<h3>📜 Workflow History</h3>")
                    history_display = gr.JSON(
                        label="Execution History",
                        value=[]
                    )
        
        with gr.Tab("🛠️ Advanced Settings"):
            gr.HTML("<h3>⚙️ Browser Automation Settings</h3>")
            
            with gr.Row():
                with gr.Column():
                    browser_headless = gr.Checkbox(
                        label="Headless Mode",
                        value=False,
                        info="Run browser in background (no GUI)"
                    )
                    
                    take_screenshots = gr.Checkbox(
                        label="Auto Screenshots",
                        value=True,
                        info="Automatically take screenshots during workflow"
                    )
                    
                    retry_count = gr.Slider(
                        label="Max Retries",
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        info="Number of retries for failed actions"
                    )
                
                with gr.Column():
                    wait_time = gr.Slider(
                        label="Wait Time (seconds)",
                        minimum=1,
                        maximum=10,
                        value=2,
                        step=1,
                        info="Time to wait between actions"
                    )
                    
                    window_size = gr.Dropdown(
                        choices=["1920x1080", "1366x768", "1280x720", "1024x768"],
                        value="1920x1080",
                        label="Browser Window Size"
                    )
        
        # Event handlers
        def execute_workflow_handler(command, provider):
            """Handle workflow execution"""
            if not command.strip():
                return (
                    "<div class='status-error'>❌ Please enter a command</div>",
                    "No command provided",
                    "",
                    "",
                    session_data["credentials"],
                    session_data,
                    session_data["conversation_history"]
                )
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    execute_complex_workflow(command, provider, session_data["credentials"])
                )
                
                status_html = f"<div class='status-success'>✅ Workflow completed</div>"
                
                return (
                    status_html,
                    result[0],
                    result[1], 
                    result[2],
                    session_data["credentials"],
                    session_data,
                    session_data["conversation_history"]
                )
            except Exception as e:
                error_html = f"<div class='status-error'>❌ Error: {str(e)}</div>"
                return (
                    error_html,
                    f"Error: {str(e)}",
                    "",
                    "",
                    session_data["credentials"],
                    session_data,
                    session_data["conversation_history"]
                )
            finally:
                loop.close()
        
        def store_credentials_handler(service, username, password):
            """Handle credential storage"""
            result = handle_credential_input(username, password, service)
            return (
                result,
                session_data["credentials"],
                session_data
            )
        
        # Wire up events
        execute_btn.click(
            fn=execute_workflow_handler,
            inputs=[workflow_command, provider_select],
            outputs=[
                result_status,
                result_output,
                detail_output,
                screenshot_info,
                credentials_display,
                session_display,
                history_display
            ]
        )
        
        store_creds_btn.click(
            fn=store_credentials_handler,
            inputs=[service_name, username_input, password_input],
            outputs=[result_output, credentials_display, session_display]
        )
    
    return interface

def main():
    """Main function"""
    print("🚀 Starting Enhanced Browser-Use AI for Complex Workflows...")
    
    # Load environment variables
    load_env_vars()
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if openai_key and openai_key != "your_openai_api_key_here":
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key not configured - please add to .env file")
    
    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        print("✅ Anthropic API key configured")
    else:
        print("⚠️  Anthropic API key not configured")
    
    print("\n🌐 Starting enhanced web interface...")
    print("📍 Optimized for Turing.com workflows and complex authentication")
    print("🎯 Features: Multi-step auth, credential prompting, quiz completion")
    
    # Create and launch interface
    interface = create_enhanced_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7788,
        share=False,
        debug=False,
        show_error=True,
        favicon_path=None
    )

if __name__ == "__main__":
    main()