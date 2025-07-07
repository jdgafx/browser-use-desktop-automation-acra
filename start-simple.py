#!/usr/bin/env python3
"""
Simple Browser-Use Starter
Launch browser automation with natural language commands
"""

import asyncio
import gradio as gr
import os
import sys
from pathlib import Path

# Add the web-ui directory to Python path
web_ui_path = Path.home() / "browser-use-complete" / "web-ui"
if web_ui_path.exists():
    sys.path.insert(0, str(web_ui_path))
    # Activate virtual environment programmatically
    venv_path = web_ui_path / ".venv" / "lib" / "python3.11" / "site-packages"
    if venv_path.exists():
        sys.path.insert(0, str(venv_path))

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

# Global agent
current_agent = None
command_history = []

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
    """Get LLM instance"""
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    }
    
    if provider == "openai" and api_keys["openai"] and api_keys["openai"] != "your_openai_api_key_here":
        return ChatOpenAI(model="gpt-4", api_key=api_keys["openai"])
    elif provider == "anthropic" and api_keys["anthropic"] and api_keys["anthropic"] != "your_anthropic_api_key_here":
        return ChatAnthropic(model="claude-3-sonnet-20240229", api_key=api_keys["anthropic"])
    else:
        print("⚠️  No valid API key found. Using demo mode.")
        return ChatOpenAI(model="gpt-3.5-turbo", api_key="demo", base_url="http://localhost:1234/v1")

async def execute_command(command, provider="openai"):
    """Execute browser command"""
    global current_agent, command_history
    
    if not command.strip():
        return "❌ Please enter a command", ""
    
    try:
        llm = get_llm(provider)
        
        # Create new agent for each command (simpler approach)
        agent = Agent(
            task=command,
            llm=llm,
            use_vision=True,
            max_failures=3
        )
        
        print(f"🚀 Executing: {command}")
        result = await agent.run()
        
        # Add to history
        command_history.append({
            "command": command,
            "result": str(result),
            "provider": provider
        })
        
        success_msg = f"✅ Command executed: {command}"
        result_msg = f"Result: {result}"
        
        return success_msg, result_msg
        
    except Exception as e:
        error_msg = f"❌ Error executing command: {str(e)}"
        return error_msg, f"Error details: {str(e)}"

def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="Browser-Use AI: Natural Language Browser Automation",
        theme=gr.themes.Soft()
    ) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(45deg, #1e3a8a, #7c3aed); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🚀 Browser-Use AI</h1>
            <h2>Natural Language Browser Automation</h2>
            <p><strong>Tell the browser what to do in plain English!</strong></p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Command input
                gr.HTML("<h3>🧠 Enter Your Command</h3>")
                command_input = gr.Textbox(
                    label="What would you like the browser to do?",
                    placeholder="e.g., 'Go to google.com and search for AI automation'",
                    lines=3
                )
                
                provider_select = gr.Radio(
                    choices=["openai", "anthropic"],
                    value="openai",
                    label="AI Provider"
                )
                
                with gr.Row():
                    execute_btn = gr.Button("🚀 Execute Command", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                
                # Quick examples
                gr.HTML("<h3>💡 Example Commands</h3>")
                examples = [
                    "Go to google.com and search for 'browser automation'",
                    "Navigate to github.com and find trending repositories",
                    "Take a screenshot of the current page",
                    "Find and click the login button",
                    "Scroll down to the bottom of the page"
                ]
                
                for i, example in enumerate(examples):
                    gr.Button(
                        f"Example {i+1}: {example[:50]}...",
                        size="sm"
                    ).click(
                        fn=lambda ex=example: ex,
                        outputs=command_input
                    )
            
            with gr.Column(scale=2):
                # Results
                gr.HTML("<h3>📊 Results</h3>")
                result_output = gr.Textbox(
                    label="Execution Status",
                    lines=5,
                    max_lines=10
                )
                
                detail_output = gr.Textbox(
                    label="Detailed Results",
                    lines=8,
                    max_lines=15
                )
        
        # History
        with gr.Row():
            gr.HTML("<h3>📜 Command History</h3>")
            history_output = gr.JSON(
                label="Previous Commands",
                value=command_history
            )
        
        # Event handlers
        def execute_handler(cmd, prov):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(execute_command(cmd, prov))
                return result[0], result[1], command_history
            finally:
                loop.close()
        
        execute_btn.click(
            fn=execute_handler,
            inputs=[command_input, provider_select],
            outputs=[result_output, detail_output, history_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", ""),
            outputs=[command_input, result_output, detail_output]
        )
    
    return interface

def main():
    """Main function"""
    print("🚀 Starting Browser-Use AI Simple Interface...")
    
    # Load environment variables
    load_env_vars()
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if openai_key == "your_openai_api_key_here" or not openai_key:
        print("⚠️  OpenAI API key not configured")
    else:
        print("✅ OpenAI API key found")
    
    if anthropic_key == "your_anthropic_api_key_here" or not anthropic_key:
        print("⚠️  Anthropic API key not configured")
    else:
        print("✅ Anthropic API key found")
    
    print("\n🌐 Starting web interface...")
    
    # Create and launch interface
    interface = create_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7788,
        share=False,
        debug=False,
        show_error=True
    )

if __name__ == "__main__":
    main()