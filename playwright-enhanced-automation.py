#!/usr/bin/env python3
"""
Enhanced Browser Automation using Playwright (No API Key Required)
Recreates the enhanced browser interface functionality using templates and smart detection
"""

import asyncio
import os
import platform
import subprocess
import queue
import threading
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

import gradio as gr
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Import our custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import with proper module names using absolute file paths
    import importlib.util
    from pathlib import Path

    current_dir = Path(__file__).parent

    def load_module_from_file(module_name, file_name):
        """Load a module from a file with proper error handling"""
        file_path = current_dir / file_name
        if not file_path.exists():
            raise ImportError(f"File {file_name} not found in {current_dir}")

        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec is None:
            raise ImportError(f"Could not create spec for {file_name}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Load all modules
    smart_module = load_module_from_file("smart_element_detection", "smart-element-detection.py")
    SmartElementDetector = smart_module.SmartElementDetector

    auto_module = load_module_from_file("automation_templates", "automation-templates.py")
    AutomationTemplates = auto_module.AutomationTemplates

    nlp_module = load_module_from_file("natural_language_processor", "natural-language-processor.py")
    NaturalLanguageProcessor = nlp_module.NaturalLanguageProcessor

    exec_module = load_module_from_file("natural_language_executor", "natural-language-executor.py")
    NaturalLanguageExecutor = exec_module.NaturalLanguageExecutor

    file_module = load_module_from_file("file_manager", "file-manager.py")
    FileManager = file_module.FileManager

    prompt_module = load_module_from_file("prompt_manager", "prompt-manager.py")
    PromptManager = prompt_module.PromptManager

    print("✅ Successfully loaded all custom modules including natural language processing")
    MODULES_LOADED = True
except Exception as e:
    print(f"❌ Error loading custom modules: {e}")
    print("Make sure all module files are in the same directory")
    import traceback
    traceback.print_exc()
    SmartElementDetector = None
    AutomationTemplates = None
    NaturalLanguageProcessor = None
    NaturalLanguageExecutor = None
    FileManager = None
    PromptManager = None
    MODULES_LOADED = False

# File processing imports (same as enhanced interface)
try:
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class InteractivePromptManager:
    """Manages interactive prompts during automation execution"""
    
    def __init__(self):
        self.prompt_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.waiting_for_response = False
    
    async def prompt_user(self, message: str, options: List[str] = None) -> Dict:
        """Send a prompt to the user and wait for response"""
        self.waiting_for_response = True
        prompt_data = {
            'message': message,
            'options': options or [],
            'timestamp': time.time()
        }
        self.prompt_queue.put(prompt_data)
        
        # Wait for response (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while self.waiting_for_response and (time.time() - start_time) < timeout:
            try:
                response = self.response_queue.get(timeout=1)
                self.waiting_for_response = False
                return response
            except queue.Empty:
                continue
        
        self.waiting_for_response = False
        return {'response': 'timeout', 'message': 'User response timeout'}
    
    def send_response(self, response: Dict):
        """Send response from user interface"""
        if self.waiting_for_response:
            self.response_queue.put(response)
    
    def get_pending_prompt(self) -> Optional[Dict]:
        """Get pending prompt for UI display"""
        try:
            return self.prompt_queue.get_nowait()
        except queue.Empty:
            return None

class FileManager:
    """Handles file uploads and content extraction (same as enhanced interface)"""
    
    def __init__(self):
        self.upload_dir = Path("/tmp/playwright_automation_files")
        self.upload_dir.mkdir(exist_ok=True)
        self.uploaded_files = {}
    
    def save_uploaded_file(self, file_path: str, content: bytes) -> str:
        """Save uploaded file and return path"""
        filename = Path(file_path).name
        save_path = self.upload_dir / filename
        
        with open(save_path, 'wb') as f:
            f.write(content)
        
        # Extract content
        file_content = self.extract_file_content(str(save_path))
        self.uploaded_files[filename] = {
            'path': str(save_path),
            'content': file_content,
            'type': self.get_file_type(filename)
        }
        
        return str(save_path)
    
    def extract_file_content(self, file_path: str) -> str:
        """Extract text content from various file types"""
        if not PDF_SUPPORT:
            return "File processing libraries not available"
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext in ['.doc', '.docx']:
                return self._extract_docx_content(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._extract_image_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"PDF extraction error: {str(e)}"
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"DOCX extraction error: {str(e)}"
    
    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"OCR extraction error: {str(e)}"
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type"""
        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            return 'resume/document'
        elif ext in ['.doc', '.docx']:
            return 'document'
        elif ext in ['.png', '.jpg', '.jpeg']:
            return 'image'
        else:
            return 'other'
    
    def get_file_context(self) -> str:
        """Get context from all uploaded files"""
        if not self.uploaded_files:
            return "No files uploaded"
        
        context = "Uploaded file context:\n\n"
        for filename, file_info in self.uploaded_files.items():
            context += f"File: {filename} ({file_info['type']})\n"
            context += f"Content preview: {file_info['content'][:500]}...\n\n"
        
        return context

class WindowManager:
    """Manages browser window positioning (same as enhanced interface)"""
    
    def __init__(self):
        self.system = platform.system()
    
    async def position_browser_window(self):
        """Position browser window to front and center"""
        try:
            if self.system == "Linux":
                await self._position_linux()
            elif self.system == "Darwin":  # macOS
                await self._position_macos()
            elif self.system == "Windows":
                await self._position_windows()
        except Exception as e:
            print(f"Window positioning failed: {e}")
    
    async def _position_linux(self):
        """Position window on Linux using wmctrl"""
        try:
            # Find browser window
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            windows = result.stdout.split('\n')
            
            browser_window = None
            for window in windows:
                if any(browser in window.lower() for browser in ['chrome', 'firefox', 'browser']):
                    browser_window = window.split()[0]
                    break
            
            if browser_window:
                # Move to front and center
                subprocess.run(['wmctrl', '-i', '-a', browser_window])
                subprocess.run(['wmctrl', '-i', '-r', browser_window, '-e', '0,100,100,1200,800'])
        except Exception:
            pass
    
    async def _position_macos(self):
        """Position window on macOS using AppleScript"""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            if frontApp contains "Chrome" or frontApp contains "Firefox" or frontApp contains "Safari" then
                tell process frontApp
                    set position of front window to {100, 100}
                    set size of front window to {1200, 800}
                end tell
            end if
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script])
        except Exception:
            pass
    
    async def _position_windows(self):
        """Position window on Windows using Windows API"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if any(browser in window_text.lower() for browser in ['chrome', 'firefox', 'edge']):
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                hwnd = windows[0]
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 100, 100, 1200, 800, 0)
        except ImportError:
            pass

class PlaywrightAutomationEngine:
    """Main automation engine using Playwright with templates"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

        # Initialize components with error handling
        if SmartElementDetector:
            self.detector = SmartElementDetector()
        else:
            self.detector = None

        if AutomationTemplates:
            self.templates = AutomationTemplates(self.detector)
        else:
            self.templates = None

        self.prompt_manager = InteractivePromptManager()
        self.file_manager = FileManager()
        self.window_manager = WindowManager()
        self.nl_executor = None  # Will be initialized when browser starts

        self.execution_log = []
        self.is_running = False
    
    async def start_browser(self, headless: bool = False) -> str:
        """Start browser session"""
        try:
            if self.playwright:
                await self.stop_browser()
            
            self.playwright = await async_playwright().start()

            # Enhanced stealth browser configuration to bypass bot detection
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-plugins-discovery',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-ipc-flooding-protection',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--no-pings',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    '--window-size=1920,1080',
                    '--disable-automation',
                    '--exclude-switches=enable-automation',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-client-side-phishing-detection',
                    '--disable-sync',
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-restore-session-state',
                    '--disable-ipc-flooding-protection',
                    '--no-service-autorun',
                    '--no-experiments',
                    '--no-default-browser-check',
                    '--no-first-run',
                    '--no-pings',
                    '--no-zygote',
                    '--use-fake-ui-for-media-stream',
                    '--use-fake-device-for-media-stream',
                    '--autoplay-policy=user-gesture-required',
                    '--disable-features=ScriptStreaming',
                    '--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer',
                    '--run-all-compositor-stages-before-draw',
                    '--disable-threaded-animation',
                    '--disable-threaded-scrolling',
                    '--disable-checker-imaging',
                    '--disable-new-content-rendering-timeout',
                    '--disable-image-animation-resync',
                    '--disable-partial-raster',
                    '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4'
                ]
            )

            # Create context with stealth settings
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )

            self.page = await self.context.new_page()

            # Add comprehensive stealth JavaScript to hide automation indicators
            await self.page.add_init_script("""
                // Remove webdriver property completely
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });

                // Remove automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

                // Mock realistic navigator properties
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Native Client', filename: 'internal-nacl-plugin'}
                    ],
                });

                // Mock permissions realistically
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Mock chrome runtime
                window.chrome = {
                    runtime: {
                        onConnect: undefined,
                        onMessage: undefined,
                    },
                    app: {
                        isInstalled: false,
                    },
                };

                // Mock realistic screen properties
                Object.defineProperty(screen, 'colorDepth', {
                    get: () => 24,
                });

                Object.defineProperty(screen, 'pixelDepth', {
                    get: () => 24,
                });

                // Mock hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });

                // Mock device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });

                // Mock connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                    }),
                });

                // Override toString methods to hide automation
                window.navigator.webdriver = undefined;

                // Mock realistic timing
                const originalPerformanceNow = performance.now;
                performance.now = function() {
                    return originalPerformanceNow.call(performance) + Math.random() * 0.1;
                };

                // Mock realistic mouse movements
                let mouseX = 0, mouseY = 0;
                document.addEventListener('mousemove', (e) => {
                    mouseX = e.clientX;
                    mouseY = e.clientY;
                });

                // Hide automation in iframe detection
                Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                    get: function() {
                        return window;
                    }
                });
            """)
            
            # Position browser window
            if not headless:
                await self.window_manager.position_browser_window()

            # Initialize natural language executor
            if NaturalLanguageExecutor:
                self.nl_executor = NaturalLanguageExecutor(
                    self.page,
                    self.detector,
                    self.templates
                )

            self.log("Browser started successfully with natural language support")
            return "✅ Browser started successfully with natural language support"
            
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            self.log(error_msg)
            return f"❌ {error_msg}"
    
    async def stop_browser(self) -> str:
        """Stop browser session"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            
            self.log("Browser stopped")
            return "✅ Browser stopped successfully"
            
        except Exception as e:
            error_msg = f"Error stopping browser: {str(e)}"
            self.log(error_msg)
            return f"❌ {error_msg}"
    
    def log(self, message: str):
        """Add message to execution log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        print(log_entry)  # Also print to console

    async def navigate_to_url(self, url: str) -> str:
        """Navigate to a specific URL"""
        if not self.page:
            return "❌ Browser not started. Please start browser first."

        try:
            await self.page.goto(url)
            title = await self.page.title()
            self.log(f"Navigated to: {url}")
            self.log(f"Page title: {title}")
            return f"✅ Navigated to: {url}\nPage title: {title}"
        except Exception as e:
            error_msg = f"Failed to navigate to {url}: {str(e)}"
            self.log(error_msg)
            return f"❌ {error_msg}"

    async def analyze_current_page(self) -> Dict:
        """Analyze current page and suggest automation actions"""
        if not self.page:
            return {'error': 'Browser not started'}

        try:
            # Get page analysis
            analysis = await self.detector.analyze_page_structure(self.page)

            # Get automation suggestions
            suggestions = await self.detector.suggest_automation_actions(self.page)

            analysis['suggestions'] = suggestions
            self.log(f"Page analyzed: {len(suggestions)} automation suggestions found")

            return analysis
        except Exception as e:
            error_msg = f"Page analysis failed: {str(e)}"
            self.log(error_msg)
            return {'error': error_msg}

    async def execute_template(self, template_name: str, data: Dict) -> Dict:
        """Execute an automation template"""
        if not self.page:
            return {'success': False, 'error': 'Browser not started'}

        self.is_running = True
        self.log(f"Starting template execution: {template_name}")

        try:
            # Add file context to data if available
            if self.file_manager.uploaded_files:
                data['file_context'] = self.file_manager.get_file_context()

            # Execute template with interactive callback
            result = await self.templates.execute_template(
                template_name,
                self.page,
                data,
                self.prompt_manager.prompt_user
            )

            self.log(f"Template execution completed: {template_name}")
            for step in result.get('steps', []):
                self.log(f"  - {step}")

            return result

        except Exception as e:
            error_msg = f"Template execution failed: {str(e)}"
            self.log(error_msg)
            return {'success': False, 'error': error_msg}
        finally:
            self.is_running = False

    async def take_screenshot(self) -> str:
        """Take screenshot of current page"""
        if not self.page:
            return "❌ Browser not started"

        try:
            screenshot_path = f"/tmp/playwright_screenshot_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path)
            self.log(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            error_msg = f"Screenshot failed: {str(e)}"
            self.log(error_msg)
            return f"❌ {error_msg}"

    async def execute_natural_language_command(self, command: str) -> str:
        """Execute a natural language command"""
        try:
            if not self.page:
                return "❌ No browser session active. Please start the browser first."

            if not self.nl_executor:
                return "❌ Natural language processing not available"

            self.log(f"Executing command: {command}")
            result = await self.nl_executor.execute_command(command)

            if result.get("success"):
                self.log(f"✅ Command executed: {result.get('message')}")
                return f"✅ {result.get('message')}"
            else:
                self.log(f"❌ Command failed: {result.get('message')}")
                suggestions = result.get('suggestions', [])
                if suggestions:
                    return f"❌ {result.get('message')}\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions[:3])
                else:
                    return f"❌ {result.get('message')}"

        except Exception as e:
            error_msg = f"Failed to execute command: {str(e)}"
            self.log(error_msg)
            return f"❌ {error_msg}"

    def get_execution_log(self) -> str:
        """Get formatted execution log"""
        if not self.execution_log:
            return "No execution log available"

        return "\n".join(self.execution_log[-50:])  # Last 50 entries

# Global automation engine instance
automation_engine = PlaywrightAutomationEngine()

# Gradio Interface Functions
async def start_browser_ui(headless):
    """Start browser from UI"""
    return await automation_engine.start_browser(headless)

async def stop_browser_ui():
    """Stop browser from UI"""
    return await automation_engine.stop_browser()

async def navigate_ui(url):
    """Navigate to URL from UI"""
    return await automation_engine.navigate_to_url(url)

async def analyze_page_ui():
    """Analyze current page from UI"""
    analysis = await automation_engine.analyze_current_page()

    if 'error' in analysis:
        return analysis['error'], ""

    # Format analysis for display
    info = f"""
📊 Page Analysis:
URL: {analysis.get('url', 'Unknown')}
Title: {analysis.get('title', 'Unknown')}
Forms: {analysis.get('forms', 0)}
Buttons: {analysis.get('buttons', 0)}
Inputs: {analysis.get('inputs', 0)}
Links: {analysis.get('links', 0)}

🔍 Detected Features:
- Login Form: {'✅' if analysis.get('has_login_form') else '❌'}
- File Upload: {'✅' if analysis.get('has_file_upload') else '❌'}

🎯 Automation Suggestions:
"""

    suggestions = analysis.get('suggestions', [])
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            info += f"{i}. {suggestion['description']} (confidence: {suggestion['confidence']:.1f})\n"
    else:
        info += "No automation suggestions found"

    return info, analysis.get('text_preview', '')

async def execute_template_ui(template_name, template_data):
    """Execute automation template from UI"""
    if not template_name:
        return "❌ Please select a template"

    try:
        # Parse template data (JSON format expected)
        import json
        data = json.loads(template_data) if template_data.strip() else {}
    except json.JSONDecodeError:
        return "❌ Invalid JSON in template data"

    result = await automation_engine.execute_template(template_name, data)

    if result['success']:
        steps = '\n'.join([f"✅ {step}" for step in result.get('steps', [])])
        return f"✅ Template executed successfully!\n\nSteps completed:\n{steps}"
    else:
        return f"❌ Template execution failed: {result.get('error', 'Unknown error')}"

def upload_file_ui(file):
    """Handle file upload from UI"""
    if not file:
        return "No file uploaded"

    try:
        with open(file.name, 'rb') as f:
            content = f.read()

        saved_path = automation_engine.file_manager.save_uploaded_file(file.name, content)
        file_info = automation_engine.file_manager.uploaded_files[Path(file.name).name]

        return f"✅ File uploaded: {Path(file.name).name}\nType: {file_info['type']}\nContent preview: {file_info['content'][:200]}..."
    except Exception as e:
        return f"❌ File upload failed: {str(e)}"

async def execute_nl_command_ui(command):
    """Execute natural language command from UI"""
    return await automation_engine.execute_natural_language_command(command)

def get_log_ui():
    """Get execution log for UI"""
    return automation_engine.get_execution_log()

async def take_screenshot_ui():
    """Take screenshot from UI"""
    result = await automation_engine.take_screenshot()
    if result.startswith("❌"):
        return result, None
    else:
        return f"✅ Screenshot taken: {result}", result

def handle_prompt_response_ui(response_text):
    """Handle user response to interactive prompt"""
    if automation_engine.prompt_manager.waiting_for_response:
        automation_engine.prompt_manager.send_response({'response': response_text})
        return "✅ Response sent"
    else:
        return "No pending prompt"

def get_pending_prompt_ui():
    """Get pending prompt for UI"""
    prompt = automation_engine.prompt_manager.get_pending_prompt()
    if prompt:
        return f"🤖 {prompt['message']}", True
    else:
        return "", False

# Create Gradio Interface
def create_interface():
    """Create the main Gradio interface"""

    with gr.Blocks(title="Enhanced Playwright Automation", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🎭 Enhanced Playwright Automation")
        gr.Markdown("**Template-based browser automation without API keys**")

        with gr.Tab("🚀 Browser Control"):
            with gr.Row():
                with gr.Column(scale=2):
                    start_btn = gr.Button("Start Browser", variant="primary")
                    stop_btn = gr.Button("Stop Browser", variant="secondary")
                with gr.Column(scale=1):
                    headless_check = gr.Checkbox(label="Headless Mode", value=False)

            browser_status = gr.Textbox(label="Browser Status", lines=3)

            with gr.Row():
                url_input = gr.Textbox(
                    label="Navigate to URL",
                    placeholder="https://example.com",
                    scale=3
                )
                nav_btn = gr.Button("Navigate", scale=1)

            nav_result = gr.Textbox(label="Navigation Result", lines=2)

        with gr.Tab("🗣️ Natural Language Commands"):
            gr.Markdown("### Tell the browser what to do in plain English!")
            gr.Markdown("Examples: *'go to google.com'*, *'click on login button'*, *'search for python tutorials'*, *'take a screenshot'*")

            with gr.Row():
                nl_command_input = gr.Textbox(
                    label="Natural Language Command",
                    placeholder="Type what you want the browser to do...",
                    lines=2,
                    scale=4
                )
                execute_nl_btn = gr.Button("Execute", variant="primary", scale=1)

            nl_result = gr.Textbox(label="Execution Result", lines=5)

            gr.Markdown("### Common Commands:")
            gr.Markdown("""
            - **Navigation**: "go to website.com", "visit google.com"
            - **Clicking**: "click on login button", "press submit"
            - **Typing**: "type 'hello world' in search box", "enter my email"
            - **Screenshots**: "take a screenshot", "capture the page"
            - **Scrolling**: "scroll down", "go to bottom of page"
            - **Waiting**: "wait 5 seconds", "wait for page to load"
            - **Searching**: "search for 'python tutorials'"
            """)

        with gr.Tab("🔍 Page Analysis"):
            analyze_btn = gr.Button("Analyze Current Page", variant="primary")

            with gr.Row():
                with gr.Column():
                    page_info = gr.Textbox(label="Page Information", lines=15)
                with gr.Column():
                    page_content = gr.Textbox(label="Page Content Preview", lines=15)

            screenshot_btn = gr.Button("Take Screenshot")
            screenshot_status = gr.Textbox(label="Screenshot Status")
            screenshot_image = gr.Image(label="Page Screenshot")

        with gr.Tab("🎯 Template Automation"):
            with gr.Row():
                template_dropdown = gr.Dropdown(
                    choices=[
                        "login", "job_application", "form_filling", "file_upload",
                        "search", "social_media_post", "contact_form", "newsletter_signup"
                    ],
                    label="Select Template",
                    value="login"
                )
                execute_btn = gr.Button("Execute Template", variant="primary")

            template_data = gr.Textbox(
                label="Template Data (JSON format)",
                placeholder='{"username": "user@example.com", "password": "password123"}',
                lines=8
            )

            template_result = gr.Textbox(label="Execution Result", lines=10)

            gr.Markdown("### 📋 Template Examples:")
            gr.Markdown("""
            **Login:** `{"username": "user@example.com", "password": "password123"}`

            **Job Application:** `{"first_name": "John", "last_name": "Doe", "phone": "555-1234", "resume_path": "/path/to/resume.pdf"}`

            **Search:** `{"query": "browser automation"}`

            **Contact Form:** `{"name": "John Doe", "email": "john@example.com", "message": "Hello!"}`
            """)

        with gr.Tab("📁 File Management"):
            file_upload = gr.File(
                label="Upload Files (Resume, Cover Letter, etc.)",
                file_types=[".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".txt"]
            )
            upload_result = gr.Textbox(label="Upload Result", lines=5)

            gr.Markdown("### 📄 Supported File Types:")
            gr.Markdown("""
            - **PDF**: Resume, cover letters, documents
            - **Word**: .doc, .docx documents
            - **Images**: .png, .jpg, .jpeg (with OCR text extraction)
            - **Text**: .txt files
            """)

        with gr.Tab("💬 Interactive Prompts"):
            gr.Markdown("### Real-time Interaction During Automation")

            prompt_display = gr.Textbox(label="Current Prompt", lines=3)
            prompt_response = gr.Textbox(label="Your Response", placeholder="Enter your response here...")
            send_response_btn = gr.Button("Send Response", variant="primary")
            response_status = gr.Textbox(label="Response Status")

            # Auto-refresh for pending prompts
            refresh_prompt_btn = gr.Button("Check for Prompts")

        with gr.Tab("📊 Execution Log"):
            log_display = gr.Textbox(label="Execution Log", lines=20)
            refresh_log_btn = gr.Button("Refresh Log")
            clear_log_btn = gr.Button("Clear Log")

        # Event handlers
        start_btn.click(start_browser_ui, inputs=[headless_check], outputs=[browser_status])
        stop_btn.click(stop_browser_ui, outputs=[browser_status])
        nav_btn.click(navigate_ui, inputs=[url_input], outputs=[nav_result])

        execute_nl_btn.click(execute_nl_command_ui, inputs=[nl_command_input], outputs=[nl_result])
        nl_command_input.submit(execute_nl_command_ui, inputs=[nl_command_input], outputs=[nl_result])

        analyze_btn.click(analyze_page_ui, outputs=[page_info, page_content])
        screenshot_btn.click(take_screenshot_ui, outputs=[screenshot_status, screenshot_image])

        execute_btn.click(
            execute_template_ui,
            inputs=[template_dropdown, template_data],
            outputs=[template_result]
        )

        file_upload.upload(upload_file_ui, inputs=[file_upload], outputs=[upload_result])

        send_response_btn.click(
            handle_prompt_response_ui,
            inputs=[prompt_response],
            outputs=[response_status]
        )
        refresh_prompt_btn.click(get_pending_prompt_ui, outputs=[prompt_display])

        refresh_log_btn.click(get_log_ui, outputs=[log_display])
        clear_log_btn.click(lambda: automation_engine.execution_log.clear() or "Log cleared", outputs=[log_display])

    return interface

if __name__ == "__main__":
    print("🎭 Starting Enhanced Playwright Automation Interface...")
    print("🎯 Features: Template-based automation, smart element detection, interactive prompts")
    print("🚫 No API keys required!")

    interface = create_interface()
    interface.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7862,
        show_error=True
    )
