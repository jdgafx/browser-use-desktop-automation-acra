#!/usr/bin/env python3
"""
Simple Voice-Enhanced Browser-Use Interface
Uses system voice libraries and Anthropic Claude
Focused on simplicity and reliability
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add the web-ui directory to Python path
web_ui_path = Path.home() / "browser-use-complete" / "web-ui"
if web_ui_path.exists():
    sys.path.insert(0, str(web_ui_path))

# Browser-use imports
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    sys.exit(1)

class SimpleSpeechInterface:
    """Simple speech interface using system speech tools"""
    
    def __init__(self):
        self.check_speech_tools()
        self.llm = self.setup_anthropic()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "voice_enabled": True
        }
    
    def check_speech_tools(self):
        """Check for available speech tools"""
        self.has_espeak = subprocess.run(['which', 'espeak'], capture_output=True).returncode == 0
        self.has_festival = subprocess.run(['which', 'festival'], capture_output=True).returncode == 0
        self.has_arecord = subprocess.run(['which', 'arecord'], capture_output=True).returncode == 0
        
        print(f"Speech tools available:")
        print(f"  espeak (TTS): {'✅' if self.has_espeak else '❌'}")
        print(f"  festival (TTS): {'✅' if self.has_festival else '❌'}")
        print(f"  arecord (recording): {'✅' if self.has_arecord else '❌'}")
        
        if not (self.has_espeak or self.has_festival):
            print("⚠️  Installing speech tools...")
            try:
                subprocess.run(['sudo', 'apt', 'install', '-y', 'espeak', 'festival', 'alsa-utils'], check=True)
                self.has_espeak = True
                self.has_festival = True
                self.has_arecord = True
                print("✅ Speech tools installed")
            except subprocess.CalledProcessError:
                print("❌ Could not install speech tools")
    
    def setup_anthropic(self):
        """Setup Anthropic Claude LLM"""
        # Load environment variables
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
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=anthropic_key,
                temperature=0.3,
                max_tokens=4000
            )
        else:
            print("⚠️  No Anthropic API key found. Please configure it in .env file")
            return None
    
    def speak(self, text):
        """Convert text to speech using system tools"""
        try:
            if self.has_espeak:
                # Use espeak for fast, simple TTS
                subprocess.run(['espeak', '-s', '150', '-v', 'en+f3', text], 
                             check=False, capture_output=True)
            elif self.has_festival:
                # Use festival as fallback
                process = subprocess.Popen(['festival', '--tts'], 
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                process.communicate(input=text.encode())
            else:
                print(f"🗣️ Would say: {text}")
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    def record_audio(self, duration=5):
        """Record audio using arecord"""
        if not self.has_arecord:
            return None
        
        try:
            audio_file = "/tmp/voice_command.wav"
            print(f"🎙️ Recording for {duration} seconds...")
            
            # Record audio
            subprocess.run([
                'arecord', 
                '-f', 'cd',  # CD quality
                '-t', str(duration),
                audio_file
            ], check=True, capture_output=True)
            
            return audio_file
        except subprocess.CalledProcessError as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def simple_speech_to_text(self, audio_file):
        """Simple speech to text using online services or return placeholder"""
        # For now, return a placeholder - user can type the command
        return "Please type your command in the text box below"
    
    async def execute_browser_command(self, command):
        """Execute browser automation command"""
        try:
            if not self.llm:
                return "❌ No Anthropic API key configured. Please add it to .env file."
            
            # Enhanced prompt for Turing.com workflows
            enhanced_command = f"""
{command}

SPECIAL INSTRUCTIONS FOR TURING.COM WORKFLOWS:
1. If this involves turing.com, handle authentication carefully
2. For quizzes/assessments, read questions thoroughly and provide accurate answers
3. Take screenshots at key points to show progress
4. If credentials are needed, ask the user to provide them
5. Handle multi-step workflows methodically
6. Provide detailed feedback on progress
7. Be methodical and careful with form submissions
8. Wait for pages to load completely before proceeding

Execute this command with attention to detail and provide comprehensive feedback.
"""
            
            # Create and run agent
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
                    '--window-size=1920,1080'
                ]
            )
            
            print(f"🚀 Executing: {command}")
            result = await agent.run()
            
            # Store result
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "type": "browser_command"
            })
            
            success_msg = f"✅ Command completed successfully!"
            result_msg = f"Result: {result}"
            
            # Provide voice feedback
            self.speak("Command completed successfully")
            
            return f"{success_msg}\n\n{result_msg}"
            
        except Exception as e:
            error_msg = f"❌ Command failed: {str(e)}"
            self.speak("Command failed")
            return error_msg
    
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(
            title="Simple Voice Browser-Use AI",
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
            .voice-button {
                background: linear-gradient(45deg, #10b981, #059669);
                color: white;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🎙️ Simple Voice Browser-Use AI</h1>
                <h2>Anthropic Claude + System Speech Tools</h2>
                <p><strong>Optimized for Turing.com workflows and complex automation</strong></p>
            </div>
            """)
            
            with gr.Tab("🚀 Browser Commands"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎙️ Voice & Text Commands</h3>")
                        
                        # Voice recording section
                        with gr.Group(elem_classes="command-section"):
                            gr.HTML("<h4>🎙️ Voice Commands</h4>")
                            
                            record_btn = gr.Button(
                                "🎙️ Record Voice Command (5s)", 
                                variant="primary",
                                elem_classes="voice-button"
                            )
                            
                            voice_status = gr.HTML("Ready to record voice commands")
                        
                        # Text command section
                        with gr.Group(elem_classes="command-section"):
                            gr.HTML("<h4>📝 Text Commands</h4>")
                            
                            text_command = gr.Textbox(
                                label="Enter Command",
                                placeholder="e.g., 'log into my turing.com account and show me available quizzes'",
                                lines=3
                            )
                            
                            execute_btn = gr.Button("🚀 Execute Command", variant="primary")
                        
                        # Quick templates
                        gr.HTML("<h4>📋 Quick Command Templates</h4>")
                        templates = [
                            "Go to google.com and search for AI automation",
                            "Navigate to turing.com and show me the login page",
                            "Log into my turing.com account (will prompt for credentials)",
                            "Navigate to turing.com quizzes and show me available options",
                            "Go to turing.com dashboard and check my profile"
                        ]
                        
                        for i, template in enumerate(templates):
                            btn = gr.Button(f"Template {i+1}: {template[:40]}...", size="sm")
                            btn.click(
                                fn=lambda t=template: t,
                                outputs=text_command
                            )
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Execution Results</h3>")
                        
                        result_output = gr.Textbox(
                            label="Command Results",
                            lines=12,
                            max_lines=20,
                            interactive=False
                        )
                        
                        # Voice feedback
                        gr.HTML("<h4>🔊 Voice Feedback</h4>")
                        voice_feedback = gr.Checkbox(
                            label="Enable voice feedback",
                            value=True
                        )
            
            with gr.Tab("📊 Session Info"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>📜 Command History</h3>")
                        
                        history_display = gr.JSON(
                            label="Execution History",
                            value=[]
                        )
                        
                        refresh_history_btn = gr.Button("🔄 Refresh History")
                    
                    with gr.Column():
                        gr.HTML("<h3>🔧 Configuration</h3>")
                        
                        api_key_input = gr.Textbox(
                            label="Anthropic API Key",
                            type="password",
                            placeholder="Enter your Anthropic API key"
                        )
                        
                        save_key_btn = gr.Button("💾 Save API Key")
                        
                        config_status = gr.HTML("Configuration ready")
            
            # Event handlers
            def record_voice_command():
                try:
                    self.speak("Recording voice command")
                    audio_file = self.record_audio(5)
                    
                    if audio_file:
                        # For now, just inform user to use text input
                        self.speak("Please type your command in the text box")
                        return "🎙️ Voice recorded. Please type your command in the text box for now."
                    else:
                        return "❌ Could not record audio. Please use text input."
                        
                except Exception as e:
                    return f"❌ Recording error: {e}"
            
            def execute_command(command):
                if not command.strip():
                    return "❌ Please enter a command"
                
                try:
                    # Run async command
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.execute_browser_command(command))
                    loop.close()
                    return result
                except Exception as e:
                    return f"❌ Error executing command: {str(e)}"
            
            def get_history():
                return self.session_data["conversation_history"]
            
            def save_api_key(api_key):
                if api_key and api_key.strip():
                    os.environ["ANTHROPIC_API_KEY"] = api_key.strip()
                    self.llm = self.setup_anthropic()
                    return "✅ API key saved and configured"
                else:
                    return "❌ Please enter a valid API key"
            
            # Wire up events
            record_btn.click(
                fn=record_voice_command,
                outputs=voice_status
            )
            
            execute_btn.click(
                fn=execute_command,
                inputs=text_command,
                outputs=result_output
            )
            
            refresh_history_btn.click(
                fn=get_history,
                outputs=history_display
            )
            
            save_key_btn.click(
                fn=save_api_key,
                inputs=api_key_input,
                outputs=config_status
            )
        
        return interface

def main():
    """Main function"""
    print("🚀 Starting Simple Voice Browser-Use AI...")
    print("🎙️ Using system speech tools + Anthropic Claude")
    print("🎯 Optimized for Turing.com workflows")
    print()
    
    try:
        # Create speech interface
        speech_interface = SimpleSpeechInterface()
        
        # Create and launch interface
        interface = speech_interface.create_interface()
        
        print("🌐 Starting web interface...")
        print("📍 Access at: http://127.0.0.1:7790")
        print("💡 Features: Voice recording, text commands, Turing.com optimization")
        print()
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7790,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()