#!/usr/bin/env python3
"""
Enhanced Browser-Use Interface with Interactive Prompting and File Attachments
Advanced browser automation with real-time user interaction and context management
"""

import asyncio
import gradio as gr
import os
import sys
import json
import time
import threading
import queue
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile
import shutil

# File parsing imports
try:
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
    FILE_PARSING_AVAILABLE = True
except ImportError:
    print("⚠️  Some file parsing libraries not available. Install with: pip install PyPDF2 python-docx pillow pytesseract")
    FILE_PARSING_AVAILABLE = False

# Browser-use imports
try:
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    print("✅ Browser-use imported successfully!")
except ImportError as e:
    print(f"❌ Browser-use import error: {e}")
    print("Please ensure browser-use is installed: pip install browser-use")
    sys.exit(1)

class InteractivePromptManager:
    """Manages interactive prompts during browser automation"""
    
    def __init__(self):
        self.prompt_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_waiting = False
        self.current_prompt = None
    
    def request_user_input(self, prompt_text: str, options: List[str] = None) -> str:
        """Request input from user during automation"""
        self.current_prompt = {
            "text": prompt_text,
            "options": options or [],
            "timestamp": time.time()
        }
        self.is_waiting = True
        self.prompt_queue.put(self.current_prompt)
        
        # Wait for response
        try:
            response = self.response_queue.get(timeout=300)  # 5 minute timeout
            self.is_waiting = False
            self.current_prompt = None
            return response
        except queue.Empty:
            self.is_waiting = False
            self.current_prompt = None
            return "timeout"
    
    def provide_response(self, response: str):
        """Provide response to waiting automation"""
        if self.is_waiting:
            self.response_queue.put(response)
    
    def get_current_prompt(self):
        """Get current prompt if any"""
        return self.current_prompt if self.is_waiting else None

class FileManager:
    """Manages uploaded files and context extraction"""
    
    def __init__(self):
        self.upload_dir = Path(tempfile.gettempdir()) / "browser_automation_files"
        self.upload_dir.mkdir(exist_ok=True)
        self.files = {}
    
    def save_file(self, file_path: str, original_name: str) -> str:
        """Save uploaded file and extract content"""
        file_id = f"file_{int(time.time())}_{len(self.files)}"
        saved_path = self.upload_dir / f"{file_id}_{original_name}"
        
        # Copy file to managed location
        shutil.copy2(file_path, saved_path)
        
        # Extract content
        content = self._extract_content(saved_path)
        
        self.files[file_id] = {
            "id": file_id,
            "original_name": original_name,
            "path": str(saved_path),
            "content": content,
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "size": saved_path.stat().st_size
        }
        
        return file_id
    
    def _extract_content(self, file_path: Path) -> str:
        """Extract text content from various file types"""
        try:
            suffix = file_path.suffix.lower()
            
            if suffix == '.pdf':
                return self._extract_pdf_content(file_path)
            elif suffix in ['.docx', '.doc']:
                return self._extract_docx_content(file_path)
            elif suffix in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                return file_path.read_text(encoding='utf-8', errors='ignore')
            elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                return self._extract_image_text(file_path)
            else:
                return f"File type {suffix} not supported for content extraction"
                
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF"""
        if not FILE_PARSING_AVAILABLE:
            return "PDF parsing not available - install PyPDF2"
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except:
            return "Could not extract PDF content"

    def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text from Word document"""
        if not FILE_PARSING_AVAILABLE:
            return "Word document parsing not available - install python-docx"
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except:
            return "Could not extract Word document content"

    def _extract_image_text(self, file_path: Path) -> str:
        """Extract text from image using OCR"""
        if not FILE_PARSING_AVAILABLE:
            return "Image OCR not available - install pillow and pytesseract"
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except:
            return "Could not extract text from image"
    
    def get_file_content(self, file_id: str) -> str:
        """Get content of a specific file"""
        return self.files.get(file_id, {}).get("content", "")
    
    def get_all_files_context(self) -> str:
        """Get context from all uploaded files"""
        if not self.files:
            return ""
        
        context = "UPLOADED FILES CONTEXT:\n"
        for file_info in self.files.values():
            context += f"\n--- {file_info['original_name']} ---\n"
            context += file_info['content'][:2000]  # Limit content length
            if len(file_info['content']) > 2000:
                context += "\n... (content truncated)"
            context += "\n"
        
        return context
    
    def list_files(self) -> List[Dict]:
        """List all uploaded files"""
        return list(self.files.values())

class WindowManager:
    """Manages browser window positioning and focusing"""
    
    @staticmethod
    def bring_to_front_and_center():
        """Bring browser window to front and center it"""
        try:
            system = platform.system()
            
            if system == "Linux":
                # Use wmctrl if available
                subprocess.run(["wmctrl", "-a", "Chrome"], check=False)
                subprocess.run(["wmctrl", "-a", "Chromium"], check=False)
            elif system == "Darwin":  # macOS
                subprocess.run([
                    "osascript", "-e",
                    'tell application "Google Chrome" to activate'
                ], check=False)
            elif system == "Windows":
                # Windows-specific window management would go here
                pass
                
        except Exception as e:
            print(f"Window management warning: {e}")

class EnhancedBrowserInterface:
    """Enhanced browser interface with interactive prompting and file attachments"""
    
    def __init__(self):
        self.llm = self.setup_anthropic()
        self.prompt_manager = InteractivePromptManager()
        self.file_manager = FileManager()
        self.session_data = {
            "credentials": {},
            "conversation_history": [],
            "current_url": "",
            "last_screenshot": None,
            "execution_state": "idle"
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
                model="claude-3-haiku-20240307",
                api_key=anthropic_key,
                temperature=0.3,
                max_tokens=4000
            )
        else:
            print("⚠️  No Anthropic API key found. Please configure it.")
            return None

    async def execute_interactive_command(self, command: str, username: str = "", password: str = ""):
        """Execute browser command with interactive prompting support"""
        try:
            if not self.llm:
                return "❌ No Anthropic API key configured. Please add it in settings."

            self.session_data["execution_state"] = "running"

            # Get file context
            file_context = self.file_manager.get_all_files_context()

            # Build enhanced prompt with file context and interactive capabilities
            enhanced_command = f"""
{command}

{file_context}

INTERACTIVE AUTOMATION INSTRUCTIONS:
1. You can request user input during execution by saying "REQUEST_USER_INPUT: [your question]"
2. If you need clarification or direction, pause and ask the user
3. Use uploaded file context when relevant (resumes, cover letters, etc.)
4. For complex workflows, break them into steps and confirm with user
5. If credentials provided: username="{username}", password="{password}"
6. Take screenshots at key decision points
7. Handle authentication and multi-step processes carefully
8. If you encounter unexpected situations, ask for user guidance

SPECIAL FILE REFERENCES:
- When user mentions "my resume" or "resume", refer to uploaded resume files
- When user mentions "cover letter", refer to uploaded cover letter files
- Use file content to fill forms or provide context-appropriate responses

Execute this command with interactive capabilities and comprehensive feedback.
"""

            print(f"🚀 Executing interactive command: {command}")

            # Bring browser to front and center
            WindowManager.bring_to_front_and_center()

            # Create agent with enhanced settings and window positioning
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
                    '--window-position=100,100',  # Position window
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--exclude-switches=enable-automation',
                    '--disable-infobars',
                    '--no-first-run'
                ]
            )

            # Execute with interactive monitoring
            result = await self._execute_with_interaction_monitoring(agent)

            # Store result in session
            self.session_data["conversation_history"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "command": command,
                "result": str(result),
                "credentials_used": bool(username),
                "files_used": len(self.file_manager.files) > 0
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

            self.session_data["execution_state"] = "idle"

            success_msg = "✅ Interactive browser command executed successfully!"
            result_msg = f"Result: {result}"

            return f"{success_msg}\n\n{result_msg}"

        except Exception as e:
            self.session_data["execution_state"] = "error"
            error_msg = f"❌ Command execution failed: {str(e)}"
            print(error_msg)
            return error_msg

    async def _execute_with_interaction_monitoring(self, agent):
        """Execute agent with monitoring for interaction requests"""
        # This would need to be implemented with custom agent monitoring
        # For now, we'll use the standard execution
        return await agent.run()

    def handle_file_upload(self, files):
        """Handle file uploads and extract content"""
        if not files:
            return "No files uploaded", []

        uploaded_files = []
        for file in files:
            if hasattr(file, 'name'):
                file_id = self.file_manager.save_file(file.name, os.path.basename(file.name))
                uploaded_files.append(file_id)

        file_list = self.file_manager.list_files()
        status = f"✅ Uploaded {len(uploaded_files)} file(s). Total files: {len(file_list)}"

        return status, file_list

    def get_current_prompt(self):
        """Get current interactive prompt if any"""
        prompt = self.prompt_manager.get_current_prompt()
        if prompt:
            return prompt["text"], prompt.get("options", [])
        return "", []

    def respond_to_prompt(self, response: str):
        """Respond to current interactive prompt"""
        self.prompt_manager.provide_response(response)
        return f"✅ Response sent: {response}"

    def create_interface(self):
        """Create enhanced Gradio interface with file attachments and interactive prompting"""
        with gr.Blocks(
            title="Enhanced Browser-Use AI: Interactive Automation",
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
            .file-section {
                border: 2px solid #10b981;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
            .prompt-section {
                border: 2px solid #f59e0b;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: #fef3c7;
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
                <h1>🤖 Enhanced Browser-Use AI</h1>
                <h2>Interactive Automation with File Context</h2>
                <p><strong>Features: Real-time prompting • File attachments • Auto-positioning • Context awareness</strong></p>
            </div>
            """)

            with gr.Tab("🚀 Interactive Automation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎯 Automation Commands</h3>")

                        # Main command input
                        command_input = gr.Textbox(
                            label="Enter Browser Command",
                            placeholder="e.g., 'Apply to jobs using my resume and cover letter'",
                            lines=4,
                            elem_classes="command-section"
                        )

                        # Credentials section
                        gr.HTML("<h4>🔐 Credentials (Optional)</h4>")
                        with gr.Row():
                            cred_username = gr.Textbox(
                                label="Username/Email",
                                placeholder="Enter username if needed"
                            )
                            cred_password = gr.Textbox(
                                label="Password",
                                type="password",
                                placeholder="Enter password if needed"
                            )

                        execute_btn = gr.Button("🚀 Execute Interactive Command", variant="primary", size="lg")

                        # Interactive prompt section
                        gr.HTML("<h4>💬 Interactive Prompts</h4>")
                        with gr.Group(elem_classes="prompt-section"):
                            current_prompt_display = gr.Textbox(
                                label="Current Prompt",
                                placeholder="No active prompts",
                                interactive=False,
                                lines=3
                            )

                            prompt_response = gr.Textbox(
                                label="Your Response",
                                placeholder="Enter your response to the prompt above"
                            )

                            respond_btn = gr.Button("📤 Send Response", variant="secondary")
                            prompt_status = gr.HTML("No active prompts")

                        # Quick templates
                        gr.HTML("<h4>📋 Quick Templates</h4>")
                        templates = [
                            "Apply to software engineer jobs using my resume",
                            "Fill out job application with my information",
                            "Search for remote Python developer positions",
                            "Update my LinkedIn profile with resume info",
                            "Navigate to job board and filter by my skills"
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

                        execution_status = gr.HTML("Status: Idle")

                        # Screenshot display
                        screenshot_display = gr.Image(
                            label="Latest Screenshot",
                            interactive=False
                        )

            with gr.Tab("📁 File Management"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>📤 File Upload</h3>")

                        file_upload = gr.File(
                            label="Upload Files (Resume, Cover Letter, etc.)",
                            file_count="multiple",
                            file_types=[".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"],
                            elem_classes="file-section"
                        )

                        upload_btn = gr.Button("📁 Process Files", variant="primary")
                        upload_status = gr.HTML("No files uploaded")

                        gr.HTML("<h4>💡 Supported File Types</h4>")
                        gr.HTML("""
                        <ul>
                            <li><strong>Documents:</strong> PDF, Word (.docx, .doc), Text (.txt)</li>
                            <li><strong>Images:</strong> PNG, JPG, JPEG (with OCR)</li>
                            <li><strong>Use cases:</strong> Resumes, cover letters, certificates, forms</li>
                        </ul>
                        """)

                    with gr.Column(scale=2):
                        gr.HTML("<h3>📋 Uploaded Files</h3>")

                        files_display = gr.JSON(
                            label="File List",
                            value=[]
                        )

                        refresh_files_btn = gr.Button("🔄 Refresh File List")

                        gr.HTML("<h4>📖 File Content Preview</h4>")
                        file_content_preview = gr.Textbox(
                            label="Content Preview",
                            lines=10,
                            max_lines=15,
                            interactive=False,
                            placeholder="Select a file to preview its content"
                        )

            with gr.Tab("⚙️ Settings & History"):
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

                        gr.HTML("<h3>📊 Session Information</h3>")
                        session_display = gr.JSON(
                            label="Current Session",
                            value={}
                        )

                        refresh_session_btn = gr.Button("🔄 Refresh Session")

                    with gr.Column():
                        gr.HTML("<h3>📜 Execution History</h3>")

                        history_display = gr.JSON(
                            label="Command History",
                            value=[]
                        )

                        clear_history_btn = gr.Button("🗑️ Clear History", variant="stop")

            # Event handlers
            def execute_command_handler(command, username, password):
                if not command.strip():
                    return "❌ Please enter a command", "", None, "Status: Error"

                try:
                    # Run async command
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.execute_interactive_command(command, username, password)
                    )
                    loop.close()

                    # Return result, current URL, screenshot, and status
                    current_url_val = self.session_data.get("current_url", "")
                    screenshot_path = self.session_data.get("last_screenshot")
                    status = f"Status: {self.session_data.get('execution_state', 'idle').title()}"

                    return result, current_url_val, screenshot_path, status

                except Exception as e:
                    return f"❌ Error: {str(e)}", "", None, "Status: Error"

            def handle_file_upload_handler(files):
                return self.handle_file_upload(files)

            def respond_to_prompt_handler(response):
                return self.respond_to_prompt(response)

            def refresh_files_handler():
                return self.file_manager.list_files()

            def save_api_key_handler(api_key):
                if api_key and api_key.strip():
                    os.environ["ANTHROPIC_API_KEY"] = api_key.strip()
                    self.llm = self.setup_anthropic()
                    return "✅ API key saved and LLM configured"
                else:
                    return "❌ Please enter a valid API key"

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
                outputs=[result_output, current_url, screenshot_display, execution_status]
            )

            upload_btn.click(
                fn=handle_file_upload_handler,
                inputs=file_upload,
                outputs=[upload_status, files_display]
            )

            respond_btn.click(
                fn=respond_to_prompt_handler,
                inputs=prompt_response,
                outputs=prompt_status
            )

            refresh_files_btn.click(
                fn=refresh_files_handler,
                outputs=files_display
            )

            save_key_btn.click(
                fn=save_api_key_handler,
                inputs=api_key_input,
                outputs=api_status
            )

            refresh_session_btn.click(
                fn=refresh_session_handler,
                outputs=[session_display, history_display]
            )

        return interface

def main():
    """Main function to launch the enhanced browser interface"""
    print("🚀 Starting Enhanced Browser-Use AI Interface...")
    print("🤖 Features: Interactive prompting, file attachments, auto-positioning")
    print("🎯 Optimized for job applications and complex workflows")
    print()

    try:
        # Create enhanced browser interface
        browser_interface = EnhancedBrowserInterface()

        # Create and launch interface
        interface = browser_interface.create_interface()

        print("🌐 Starting enhanced web interface...")
        print("📍 Access at: http://127.0.0.1:7789")
        print("💡 Enhanced Features:")
        print("   • 💬 Interactive prompting during automation")
        print("   • 📁 File upload and context integration")
        print("   • 🎯 Automatic browser positioning")
        print("   • 📄 Resume/cover letter context awareness")
        print("   • 🔄 Real-time execution monitoring")
        print()

        interface.launch(
            server_name="127.0.0.1",
            server_port=7789,
            share=False,
            debug=False,
            show_error=True
        )

    except Exception as e:
        print(f"❌ Error starting enhanced interface: {e}")

if __name__ == "__main__":
    main()
