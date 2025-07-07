#!/usr/bin/env python3
"""
Enhanced Browser-Use Web Interface
Designed for direct natural language and voice command execution
No safety checks - pure command execution as requested
"""

import asyncio
import gradio as gr
import speech_recognition as sr
import threading
import queue
import time
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import tempfile

# Try to import browser_use components
try:
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI
except ImportError:
    print("⚠️  Browser-use library not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "browser-use"])
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI

# Global state
current_agent = None
voice_handler = None
conversation_history = []
session_state = {
    "current_llm": "openai",
    "voice_enabled": False,
    "auto_execute": True,
    "last_screenshot": None
}

class EnhancedVoiceHandler:
    """Enhanced voice command handler with continuous listening"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.command_queue = queue.Queue()
        self.wake_words = ["hey browser", "browser", "execute", "do this", "run this"]
        
        # Calibrate microphone
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎙️  Voice handler initialized successfully")
        except Exception as e:
            print(f"⚠️  Voice handler initialization warning: {e}")
    
    def start_listening(self):
        """Start continuous voice recognition"""
        self.listening = True
        thread = threading.Thread(target=self._listen_continuously, daemon=True)
        thread.start()
        return thread
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.listening = False
    
    def _listen_continuously(self):
        """Continuously listen for voice commands"""
        while self.listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
                try:
                    # Recognize speech using Google Web Speech API
                    command = self.recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words or direct execution
                    if any(wake_word in command for wake_word in self.wake_words) or session_state.get("auto_execute", True):
                        # Remove wake words and clean command
                        for wake_word in self.wake_words:
                            command = command.replace(wake_word, "").strip()
                        
                        if command:  # Only queue non-empty commands
                            self.command_queue.put(command)
                            print(f"🎙️  Voice command received: {command}")
                        
                except sr.UnknownValueError:
                    # Could not understand audio - continue listening
                    pass
                except sr.RequestError as e:
                    print(f"Voice recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                # No speech detected - continue listening
                pass
            except Exception as e:
                print(f"Voice listening error: {e}")
                time.sleep(1)
    
    def get_command(self) -> Optional[str]:
        """Get the next voice command from queue"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

def get_llm_instance(provider: str = "openai"):
    """Get LLM instance based on provider"""
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"), 
        "google": os.getenv("GOOGLE_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY")
    }
    
    if provider == "openai" and api_keys["openai"]:
        return ChatOpenAI(model="gpt-4o", api_key=api_keys["openai"], temperature=0.7)
    elif provider == "anthropic" and api_keys["anthropic"]:
        return ChatAnthropic(model="claude-3-sonnet-20240229", api_key=api_keys["anthropic"], temperature=0.7)
    elif provider == "google" and api_keys["google"]:
        return ChatGoogleGenerativeAI(model="gemini-pro", api_key=api_keys["google"], temperature=0.7)
    elif provider == "deepseek" and api_keys["deepseek"]:
        # DeepSeek uses OpenAI-compatible API
        return ChatOpenAI(
            model="deepseek-chat", 
            api_key=api_keys["deepseek"],
            base_url="https://api.deepseek.com/v1",
            temperature=0.7
        )
    else:
        # Fallback to first available
        for prov, key in api_keys.items():
            if key:
                return get_llm_instance(prov)
        
        # If no API keys, use local/free option
        print("⚠️  No API keys found, using local model")
        return ChatOpenAI(model="gpt-3.5-turbo", api_key="dummy", base_url="http://localhost:1234/v1")

async def execute_browser_command(command: str, llm_provider: str = "openai") -> tuple[str, str]:
    """Execute browser command directly with no safety checks"""
    global current_agent, conversation_history
    
    try:
        # Get LLM instance
        llm = get_llm_instance(llm_provider)
        
        # Create or reuse agent
        if not current_agent:
            current_agent = Agent(
                task=command,
                llm=llm,
                # Remove any safety constraints
                use_vision=True,
                save_conversation_path=None,  # Don't save conversations
                max_failures=10,  # Allow more failures
                retry_delay=1,
                # Enable all capabilities
                enable_memory=True,
                max_memory_entries=1000
            )
        else:
            # Update task for existing agent
            current_agent.task = command
            current_agent.llm = llm
        
        # Execute the command directly
        print(f"🚀 Executing: {command}")
        result = await current_agent.run()
        
        # Add to conversation history
        conversation_history.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "command": command,
            "result": str(result),
            "llm_provider": llm_provider
        })
        
        # Take screenshot after execution
        try:
            if current_agent.browser:
                screenshot_path = f"/tmp/browser_screenshot_{int(time.time())}.png"
                await current_agent.browser.screenshot(path=screenshot_path)
                session_state["last_screenshot"] = screenshot_path
        except Exception as e:
            print(f"Screenshot capture warning: {e}")
        
        return f"✅ Command executed successfully", f"Result: {result}"
        
    except Exception as e:
        error_msg = f"❌ Execution failed: {str(e)}"
        print(error_msg)
        return error_msg, f"Error details: {str(e)}"

def process_voice_commands():
    """Background process to handle voice commands"""
    global voice_handler
    
    if not voice_handler:
        return "Voice handler not initialized"
    
    command = voice_handler.get_command()
    if command:
        # Execute voice command immediately
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                execute_browser_command(command, session_state["current_llm"])
            )
            return f"🎙️  Voice: {command}\n{result[0]}\n{result[1]}"
        finally:
            loop.close()
    
    return None

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="Browser-Use AI: Direct Command Execution",
        theme=gr.themes.Dark(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .main-header {
            text-align: center;
            background: linear-gradient(45deg, #1e3a8a, #7c3aed);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .command-box {
            border: 2px solid #3b82f6;
            border-radius: 10px;
            padding: 10px;
        }
        .voice-indicator {
            background: #ef4444;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
        }
        """
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>🚀 Browser-Use AI: Direct Command Execution</h1>
            <p>Natural Language & Voice Browser Automation</p>
            <p><strong>⚡ No safety checks - Pure command execution</strong></p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Command input
                with gr.Group():
                    gr.HTML("<h3>🧠 Natural Language Commands</h3>")
                    command_input = gr.Textbox(
                        label="Enter your command",
                        placeholder="e.g., 'Go to google.com and search for AI automation'",
                        lines=3,
                        elem_classes="command-box"
                    )
                    
                    with gr.Row():
                        execute_btn = gr.Button("🚀 Execute Command", variant="primary", size="lg")
                        clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                
                # LLM Provider selection
                with gr.Group():
                    gr.HTML("<h3>🤖 AI Provider</h3>")
                    llm_provider = gr.Dropdown(
                        choices=["openai", "anthropic", "google", "deepseek"],
                        value="openai",
                        label="Select AI Provider"
                    )
                
                # Voice controls
                with gr.Group():
                    gr.HTML("<h3>🎙️ Voice Commands</h3>")
                    with gr.Row():
                        voice_toggle = gr.Checkbox(
                            label="Enable Voice Commands",
                            value=False
                        )
                        auto_execute = gr.Checkbox(
                            label="Auto-execute voice commands",
                            value=True
                        )
                    
                    voice_status = gr.HTML("<span class='voice-indicator'>🔴 Voice Disabled</span>")
            
            with gr.Column(scale=3):
                # Results area
                with gr.Group():
                    gr.HTML("<h3>📊 Execution Results</h3>")
                    result_output = gr.Textbox(
                        label="Command Result",
                        lines=10,
                        max_lines=20,
                        interactive=False
                    )
                    
                    details_output = gr.Textbox(
                        label="Execution Details",
                        lines=5,
                        max_lines=10,
                        interactive=False
                    )
                
                # Screenshot display
                with gr.Group():
                    gr.HTML("<h3>📸 Browser Screenshot</h3>")
                    screenshot_display = gr.Image(
                        label="Current Browser State",
                        height=300
                    )
        
        # Conversation history
        with gr.Row():
            with gr.Column():
                gr.HTML("<h3>📜 Command History</h3>")
                history_output = gr.JSON(
                    label="Conversation History",
                    value=conversation_history
                )
        
        # Real-time voice processing
        voice_output = gr.Textbox(
            label="Voice Command Output",
            visible=False
        )
        
        # Event handlers
        async def execute_command_handler(command, llm_prov):
            """Handle command execution"""
            if not command.strip():
                return "❌ Please enter a command", "", None, conversation_history
            
            result, details = await execute_browser_command(command, llm_prov)
            
            # Update screenshot if available
            screenshot = None
            if session_state.get("last_screenshot") and os.path.exists(session_state["last_screenshot"]):
                screenshot = session_state["last_screenshot"]
            
            return result, details, screenshot, conversation_history
        
        def toggle_voice_handler(enabled, auto_exec):
            """Toggle voice command handling"""
            global voice_handler
            
            session_state["voice_enabled"] = enabled
            session_state["auto_execute"] = auto_exec
            
            if enabled and not voice_handler:
                try:
                    voice_handler = EnhancedVoiceHandler()
                    voice_handler.start_listening()
                    status = "<span class='voice-indicator'>🟢 Voice Active - Listening...</span>"
                except Exception as e:
                    status = f"<span class='voice-indicator'>🔴 Voice Error: {e}</span>"
            elif not enabled and voice_handler:
                voice_handler.stop_listening()
                voice_handler = None
                status = "<span class='voice-indicator'>🔴 Voice Disabled</span>"
            else:
                status = "<span class='voice-indicator'>🟢 Voice Active</span>" if enabled else "<span class='voice-indicator'>🔴 Voice Disabled</span>"
            
            return status
        
        def clear_inputs():
            """Clear input fields"""
            return "", "", ""
        
        def update_llm_provider(provider):
            """Update current LLM provider"""
            session_state["current_llm"] = provider
            return f"🤖 Provider updated to: {provider}"
        
        # Wire up events
        execute_btn.click(
            fn=execute_command_handler,
            inputs=[command_input, llm_provider],
            outputs=[result_output, details_output, screenshot_display, history_output]
        )
        
        clear_btn.click(
            fn=clear_inputs,
            outputs=[command_input, result_output, details_output]
        )
        
        voice_toggle.change(
            fn=toggle_voice_handler,
            inputs=[voice_toggle, auto_execute],
            outputs=[voice_status]
        )
        
        llm_provider.change(
            fn=update_llm_provider,
            inputs=[llm_provider],
            outputs=[result_output]
        )
        
        # Periodic voice command checking
        def check_voice_commands():
            """Check for new voice commands"""
            if session_state.get("voice_enabled", False):
                return process_voice_commands()
            return None
        
        # Auto-refresh for voice commands
        interface.load(
            fn=check_voice_commands,
            outputs=[voice_output],
            every=1  # Check every second
        )
        
        voice_output.change(
            fn=lambda x: (x, x, None, conversation_history) if x else (None, None, None, None),
            inputs=[voice_output],
            outputs=[result_output, details_output, screenshot_display, history_output]
        )
    
    return interface

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env")
    else:
        print("⚠️  No .env file found. Please configure API keys.")

def main():
    """Main application entry point"""
    print("🚀 Starting Enhanced Browser-Use Web Interface...")
    
    # Load environment
    load_environment()
    
    # Check for required dependencies
    try:
        import speech_recognition
        print("✅ Speech recognition available")
    except ImportError:
        print("⚠️  Installing speech recognition...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "speechrecognition", "pyaudio"])
    
    # Create and launch interface
    interface = create_interface()
    
    print("✅ Interface created successfully")
    print("🌐 Starting web server...")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7788,
        share=False,
        debug=True,
        show_error=True,
        favicon_path=None,
        ssl_verify=False,
        quiet=False
    )

if __name__ == "__main__":
    main()