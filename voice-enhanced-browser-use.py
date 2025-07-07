#!/usr/bin/env python3
"""
Enhanced Browser-Use with High-Quality Open-Source Voice Libraries
Uses only Anthropic API and the best open-source voice libraries:
- Whisper for Speech-to-Text (OpenAI's open-source model, not API)
- MeloTTS for Text-to-Speech
- Silero VAD for Voice Activity Detection
- Anthropic Claude for AI reasoning
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
import threading
import queue
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Add the web-ui directory to Python path
web_ui_path = Path.home() / "browser-use-complete" / "web-ui"
if web_ui_path.exists():
    sys.path.insert(0, str(web_ui_path))

# Voice libraries
try:
    import whisper
    print("✅ Whisper (STT) loaded successfully")
except ImportError:
    print("❌ Whisper not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    import whisper

try:
    from melo.api import TTS
    print("✅ MeloTTS (TTS) loaded successfully")
except ImportError:
    print("❌ MeloTTS not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "melotts"])
    from melo.api import TTS

try:
    import torch
    import torchaudio
    print("✅ Silero VAD dependencies loaded")
except ImportError:
    print("❌ Silero VAD dependencies not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchaudio"])
    import torch
    import torchaudio

try:
    import pyaudio
    print("✅ PyAudio (microphone) loaded successfully")
except ImportError:
    print("❌ PyAudio not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
    import pyaudio

# Browser-use imports
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    print("🔧 Installing browser-use...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "browser-use"])
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceEnhancedBrowserUse:
    def __init__(self):
        self.whisper_model = None
        self.tts_model = None
        self.vad_model = None
        self.llm = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.session_data = {
            "credentials": {},
            "current_url": "",
            "conversation_history": [],
            "voice_enabled": True
        }
        self.setup_models()
    
    def setup_models(self):
        """Initialize all voice and AI models"""
        try:
            # Load Whisper STT model
            print("🧠 Loading Whisper STT model...")
            self.whisper_model = whisper.load_model("base")  # Good balance of speed/accuracy
            print("✅ Whisper STT model loaded")
            
            # Load MeloTTS model
            print("🗣️ Loading MeloTTS model...")
            self.tts_model = TTS(language='EN', device='cpu')
            print("✅ MeloTTS model loaded")
            
            # Load Silero VAD model
            print("🎙️ Loading Silero VAD model...")
            self.vad_model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.vad_get_speech_timestamps = utils[0]
            print("✅ Silero VAD model loaded")
            
            # Setup Anthropic LLM
            print("🤖 Setting up Anthropic Claude...")
            self.setup_anthropic_llm()
            
        except Exception as e:
            logger.error(f"Error setting up models: {e}")
            raise
    
    def setup_anthropic_llm(self):
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
            self.llm = ChatAnthropic(
                model="claude-3-haiku-20240307",  # Fast and efficient
                api_key=anthropic_key,
                temperature=0.3,
                max_tokens=4000
            )
            print("✅ Anthropic Claude configured")
        else:
            print("⚠️  No Anthropic API key found. Voice commands will work but browser automation will be limited.")
            self.llm = None
    
    def detect_voice_activity(self, audio_data):
        """Detect voice activity using Silero VAD"""
        try:
            # Convert audio to tensor
            audio_tensor = torch.from_numpy(audio_data.astype(np.float32))
            
            # Get speech timestamps
            speech_timestamps = self.vad_get_speech_timestamps(
                audio_tensor,
                self.vad_model,
                sampling_rate=16000
            )
            
            return len(speech_timestamps) > 0
        except Exception as e:
            logger.error(f"Voice activity detection error: {e}")
            return False
    
    def speech_to_text(self, audio_file_path):
        """Convert speech to text using Whisper"""
        try:
            result = self.whisper_model.transcribe(audio_file_path)
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Speech to text error: {e}")
            return ""
    
    def text_to_speech(self, text, output_path="output.wav"):
        """Convert text to speech using MeloTTS"""
        try:
            # Use US English speaker
            speaker_ids = self.tts_model.hps.data.spk2id
            
            # Generate speech
            self.tts_model.tts_to_file(
                text, 
                speaker_ids['EN-US'], 
                output_path,
                speed=1.0
            )
            return output_path
        except Exception as e:
            logger.error(f"Text to speech error: {e}")
            return None
    
    def start_voice_listening(self):
        """Start listening for voice commands"""
        self.is_listening = True
        
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            
            print("🎙️ Voice listening started. Say 'hey browser' to activate...")
            
            frames = []
            silence_count = 0
            recording = False
            
            while self.is_listening:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Detect voice activity
                has_voice = self.detect_voice_activity(audio_data)
                
                if has_voice and not recording:
                    print("🎙️ Voice detected, starting recording...")
                    recording = True
                    frames = []
                    silence_count = 0
                
                if recording:
                    frames.append(data)
                    
                    if not has_voice:
                        silence_count += 1
                        if silence_count > 20:  # ~1 second of silence
                            print("🔇 Silence detected, processing speech...")
                            self.process_voice_command(frames, RATE)
                            recording = False
                            frames = []
                            silence_count = 0
                
                # Limit recording length
                if len(frames) > RATE * 10:  # 10 seconds max
                    print("⏰ Max recording time reached, processing...")
                    self.process_voice_command(frames, RATE)
                    recording = False
                    frames = []
                    
        except Exception as e:
            logger.error(f"Voice listening error: {e}")
        finally:
            try:
                stream.stop_stream()
                stream.close()
                p.terminate()
            except:
                pass
    
    def process_voice_command(self, frames, sample_rate):
        """Process voice command"""
        try:
            # Save audio to temporary file
            import wave
            temp_audio_path = "/tmp/voice_command.wav"
            
            with wave.open(temp_audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            
            # Convert to text
            text = self.speech_to_text(temp_audio_path)
            
            if text:
                print(f"🎙️ Voice command: {text}")
                
                # Check for activation phrase
                if "hey browser" in text.lower() or "browser" in text.lower():
                    # Remove activation phrase
                    command = text.lower().replace("hey browser", "").replace("browser", "").strip()
                    
                    if command:
                        print(f"🤖 Executing command: {command}")
                        
                        # Execute browser command
                        asyncio.create_task(self.execute_browser_command(command))
                        
                        # Provide voice feedback
                        feedback = f"Executing command: {command}"
                        audio_file = self.text_to_speech(feedback)
                        if audio_file:
                            self.play_audio(audio_file)
                    else:
                        print("🎙️ Browser activated. What would you like me to do?")
                        audio_file = self.text_to_speech("Browser activated. What would you like me to do?")
                        if audio_file:
                            self.play_audio(audio_file)
            
        except Exception as e:
            logger.error(f"Voice command processing error: {e}")
    
    def play_audio(self, audio_file):
        """Play audio file"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except ImportError:
            print("❌ pygame not installed. Installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            self.play_audio(audio_file)
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
    
    async def execute_browser_command(self, command):
        """Execute browser automation command"""
        try:
            if not self.llm:
                print("❌ No LLM configured. Please add Anthropic API key.")
                return
            
            # Enhanced prompt for Turing.com workflows
            enhanced_command = f"""
{command}

SPECIAL INSTRUCTIONS FOR TURING.COM WORKFLOWS:
1. If this involves turing.com, handle authentication carefully
2. For quizzes/assessments, read questions thoroughly and provide accurate answers
3. Take screenshots at key points to show progress
4. If credentials are needed, prompt the user appropriately
5. Handle multi-step workflows methodically
6. Provide detailed feedback on progress

Execute this command with care and attention to detail.
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
            
            result = await agent.run()
            
            # Store result
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "type": "voice_command"
            })
            
            # Provide voice feedback
            feedback = f"Command completed successfully"
            audio_file = self.text_to_speech(feedback)
            if audio_file:
                self.play_audio(audio_file)
            
            print(f"✅ Command executed: {result}")
            
        except Exception as e:
            logger.error(f"Browser command execution error: {e}")
            
            # Provide error feedback
            feedback = f"Command failed: {str(e)}"
            audio_file = self.text_to_speech(feedback)
            if audio_file:
                self.play_audio(audio_file)
    
    def stop_voice_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        print("🔇 Voice listening stopped")
    
    def create_gradio_interface(self):
        """Create Gradio web interface"""
        with gr.Blocks(
            title="Voice-Enhanced Browser-Use AI",
            theme=gr.themes.Soft(),
            css="""
            .voice-container {
                border: 2px solid #10b981;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(45deg, #ecfdf5, #f0fdf4);
            }
            .command-box {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(45deg, #059669, #10b981); color: white; border-radius: 10px; margin-bottom: 20px;">
                <h1>🎙️ Voice-Enhanced Browser-Use AI</h1>
                <h2>High-Quality Open-Source Voice + Anthropic Claude</h2>
                <p><strong>Whisper STT • MeloTTS • Silero VAD • Anthropic Claude</strong></p>
            </div>
            """)
            
            with gr.Tab("🎙️ Voice Commands"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎙️ Voice Control</h3>")
                        
                        voice_status = gr.HTML(
                            "<div class='voice-container'>🔇 Voice listening stopped</div>"
                        )
                        
                        with gr.Row():
                            start_voice_btn = gr.Button("🎙️ Start Voice Listening", variant="primary")
                            stop_voice_btn = gr.Button("🔇 Stop Voice Listening", variant="secondary")
                        
                        gr.HTML("""
                        <div class='command-box'>
                            <h4>Voice Commands:</h4>
                            <ul>
                                <li><strong>"Hey browser, go to google.com"</strong></li>
                                <li><strong>"Browser, search for AI automation"</strong></li>
                                <li><strong>"Hey browser, login to my turing.com account"</strong></li>
                                <li><strong>"Browser, navigate to quizzes and show me options"</strong></li>
                                <li><strong>"Hey browser, complete this quiz with 100%"</strong></li>
                            </ul>
                        </div>
                        """)
                        
                        # Text command fallback
                        gr.HTML("<h3>📝 Text Commands</h3>")
                        text_command = gr.Textbox(
                            label="Enter command",
                            placeholder="e.g., 'log into my turing.com account and show me available quizzes'",
                            lines=3
                        )
                        execute_text_btn = gr.Button("🚀 Execute Text Command", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Command Results</h3>")
                        
                        result_display = gr.Textbox(
                            label="Execution Results",
                            lines=10,
                            max_lines=20,
                            interactive=False
                        )
                        
                        gr.HTML("<h3>🎵 Audio Feedback</h3>")
                        audio_output = gr.Audio(
                            label="Voice Response",
                            interactive=False
                        )
            
            with gr.Tab("⚙️ Settings"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("<h3>🔧 Voice Settings</h3>")
                        
                        voice_enabled = gr.Checkbox(
                            label="Enable Voice Commands",
                            value=True
                        )
                        
                        tts_enabled = gr.Checkbox(
                            label="Enable Voice Responses",
                            value=True
                        )
                        
                        gr.HTML("<h3>🤖 AI Settings</h3>")
                        
                        api_key_input = gr.Textbox(
                            label="Anthropic API Key",
                            type="password",
                            placeholder="Enter your Anthropic API key"
                        )
                        
                        save_settings_btn = gr.Button("💾 Save Settings")
                    
                    with gr.Column():
                        gr.HTML("<h3>📈 Session Info</h3>")
                        
                        session_info = gr.JSON(
                            label="Current Session",
                            value=self.session_data
                        )
            
            # Event handlers
            def start_voice_listening():
                if not self.is_listening:
                    # Start listening in background thread
                    threading.Thread(target=self.start_voice_listening, daemon=True).start()
                    return "<div class='voice-container'>🎙️ Voice listening active - Say 'hey browser' to activate</div>"
                else:
                    return "<div class='voice-container'>🎙️ Voice listening already active</div>"
            
            def stop_voice_listening():
                self.stop_voice_listening()
                return "<div class='voice-container'>🔇 Voice listening stopped</div>"
            
            def execute_text_command(command):
                if command.strip():
                    try:
                        # Run async command
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.execute_browser_command(command))
                        loop.close()
                        return f"✅ Command executed: {command}"
                    except Exception as e:
                        return f"❌ Error: {str(e)}"
                else:
                    return "❌ Please enter a command"
            
            # Wire up events
            start_voice_btn.click(
                fn=start_voice_listening,
                outputs=voice_status
            )
            
            stop_voice_btn.click(
                fn=stop_voice_listening,
                outputs=voice_status
            )
            
            execute_text_btn.click(
                fn=execute_text_command,
                inputs=text_command,
                outputs=result_display
            )
        
        return interface

def main():
    """Main function"""
    print("🚀 Starting Voice-Enhanced Browser-Use AI...")
    print("🎙️ Using high-quality open-source voice libraries:")
    print("   • Whisper for Speech-to-Text")
    print("   • MeloTTS for Text-to-Speech") 
    print("   • Silero VAD for Voice Activity Detection")
    print("   • Anthropic Claude for AI reasoning")
    print()
    
    try:
        # Create voice-enhanced browser use instance
        voice_browser = VoiceEnhancedBrowserUse()
        
        # Create and launch interface
        interface = voice_browser.create_gradio_interface()
        
        print("🌐 Starting voice-enhanced web interface...")
        print("📍 Optimized for Turing.com workflows with voice commands")
        print("🎯 Features: Voice commands, high-quality TTS, advanced VAD")
        print()
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7789,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()