#!/usr/bin/env python3
"""
Simple Universal Web Automation - Web Interface
Provides a Gradio-based web interface for the remote agent
"""

import asyncio
import gradio as gr
import os
import sys
import json
from typing import Dict, List, Optional
import threading
import time

# Import our remote agent
from remote_agent import UniversalWebAutomationAgent

class RemoteAgentWebUI:
    """Web interface for the Universal Web Automation Agent"""
    
    def __init__(self):
        self.agent: Optional[UniversalWebAutomationAgent] = None
        self.current_task = None
        self.execution_thread = None
        self.is_running = False
        
    def setup_agent(self, api_key: str, provider: str = "anthropic") -> str:
        """Setup the automation agent"""
        try:
            if not api_key:
                return "❌ Please provide an API key"
            
            self.agent = UniversalWebAutomationAgent(api_key, provider)
            return f"✅ Agent setup complete with {provider} provider"
            
        except Exception as e:
            return f"❌ Agent setup failed: {e}"
    
    def execute_turing_automation(self, api_key: str, provider: str) -> str:
        """Execute Turing.com quiz automation"""
        try:
            if not api_key:
                return "❌ Please provide an API key"
            
            # Setup agent if needed
            setup_result = self.setup_agent(api_key, provider)
            if "❌" in setup_result:
                return setup_result
            
            self.is_running = True
            
            # Run automation in background thread
            def run_automation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.agent.complete_turing_quizzes())
                    self.current_task = result
                except Exception as e:
                    self.current_task = f"❌ Error: {e}"
                finally:
                    self.is_running = False
                    loop.close()
            
            self.execution_thread = threading.Thread(target=run_automation)
            self.execution_thread.start()
            
            return "🚀 Turing.com automation started! Check status below..."
            
        except Exception as e:
            self.is_running = False
            return f"❌ Failed to start automation: {e}"
    
    def execute_universal_automation(self, api_key: str, provider: str, site_url: str, task_description: str) -> str:
        """Execute universal website automation"""
        try:
            if not api_key:
                return "❌ Please provide an API key"
            
            if not site_url or not task_description:
                return "❌ Please provide both site URL and task description"
            
            # Setup agent if needed
            setup_result = self.setup_agent(api_key, provider)
            if "❌" in setup_result:
                return setup_result
            
            self.is_running = True
            
            # Run automation in background thread
            def run_automation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.agent.complete_tasks_on_any_site(site_url, task_description)
                    )
                    self.current_task = result
                except Exception as e:
                    self.current_task = f"❌ Error: {e}"
                finally:
                    self.is_running = False
                    loop.close()
            
            self.execution_thread = threading.Thread(target=run_automation)
            self.execution_thread.start()
            
            return f"🚀 Universal automation started for {site_url}! Check status below..."
            
        except Exception as e:
            self.is_running = False
            return f"❌ Failed to start automation: {e}"
    
    def get_status(self) -> tuple:
        """Get current automation status"""
        if self.is_running:
            status = "🔄 Automation in progress..."
            result = "Please wait..."
            log = "Automation running..."
        elif self.current_task:
            status = "✅ Automation completed"
            result = self.current_task
            log = "\n".join(self.agent.get_execution_log() if self.agent else ["No log available"])
        else:
            status = "⏳ Ready to start automation"
            result = "No automation executed yet"
            log = "No log available"
        
        return status, result, log
    
    def stop_automation(self) -> str:
        """Stop current automation"""
        try:
            if self.is_running and self.execution_thread:
                # Note: This is a graceful stop indication, actual thread stopping is complex
                self.is_running = False
                return "⚠️ Stop signal sent (automation may take time to stop)"
            else:
                return "ℹ️ No automation currently running"
        except Exception as e:
            return f"❌ Error stopping automation: {e}"
    
    def create_interface(self):
        """Create Gradio interface"""
        
        with gr.Blocks(
            title="Simple Universal Web Automation",
            theme=gr.themes.Soft(),
            css="""
            .main-header {
                text-align: center;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .example-box {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
            <div class="main-header">
                <h1>🤖 Simple Universal Web Automation</h1>
                <p>AI that can complete any task on any website</p>
                <p><strong>Primary Example:</strong> "Log into turing.com with Google, find quizzes, complete all remaining ones"</strong></p>
            </div>
            """)
            
            with gr.Tab("🎯 Turing.com Quiz Automation"):
                gr.HTML("""
                <div class="example-box">
                    <h3>🎯 Turing.com Example</h3>
                    <p><strong>What it does:</strong> Logs into turing.com with Google, finds all quizzes, identifies completed ones, and automatically completes all remaining quizzes.</p>
                    <p><strong>Features:</strong> Handles authentication, detects quiz status, answers multiple choice/coding/essay questions using AI</p>
                </div>
                """)
                
                with gr.Row():
                    with gr.Column():
                        turing_api_key = gr.Textbox(
                            label="🔑 API Key",
                            type="password",
                            placeholder="Enter your Anthropic/OpenAI/Google API key",
                            value=os.getenv("ANTHROPIC_API_KEY", "")
                        )
                        
                        turing_provider = gr.Dropdown(
                            label="🤖 AI Provider",
                            choices=["anthropic", "openai", "google"],
                            value="anthropic"
                        )
                        
                        turing_execute_btn = gr.Button("🚀 Start Turing.com Automation", variant="primary")
                        
                    with gr.Column():
                        turing_status = gr.Textbox(
                            label="📊 Status",
                            value="⏳ Ready to start automation",
                            interactive=False
                        )
                        
                        turing_result = gr.Textbox(
                            label="🎯 Result",
                            value="No automation executed yet",
                            interactive=False,
                            lines=3
                        )
            
            with gr.Tab("🌐 Universal Website Automation"):
                gr.HTML("""
                <div class="example-box">
                    <h3>🌐 Universal Automation Examples</h3>
                    <ul>
                        <li><strong>Coursera:</strong> "Complete all my enrolled courses"</li>
                        <li><strong>LinkedIn:</strong> "Apply to 10 relevant software engineer jobs"</li>
                        <li><strong>Khan Academy:</strong> "Complete all math exercises"</li>
                        <li><strong>Any Website:</strong> "Find and complete available tasks"</li>
                    </ul>
                </div>
                """)
                
                with gr.Row():
                    with gr.Column():
                        universal_api_key = gr.Textbox(
                            label="🔑 API Key",
                            type="password",
                            placeholder="Enter your API key",
                            value=os.getenv("ANTHROPIC_API_KEY", "")
                        )
                        
                        universal_provider = gr.Dropdown(
                            label="🤖 AI Provider",
                            choices=["anthropic", "openai", "google"],
                            value="anthropic"
                        )
                        
                        site_url = gr.Textbox(
                            label="🌐 Website URL",
                            placeholder="https://example.com",
                            value=""
                        )
                        
                        task_description = gr.Textbox(
                            label="📋 Task Description",
                            placeholder="Complete all available courses",
                            lines=2
                        )
                        
                        universal_execute_btn = gr.Button("🚀 Start Universal Automation", variant="primary")
                        
                    with gr.Column():
                        universal_status = gr.Textbox(
                            label="📊 Status",
                            value="⏳ Ready to start automation",
                            interactive=False
                        )
                        
                        universal_result = gr.Textbox(
                            label="🎯 Result",
                            value="No automation executed yet",
                            interactive=False,
                            lines=3
                        )
            
            with gr.Tab("📋 Execution Log & Control"):
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh Status")
                    stop_btn = gr.Button("⛔ Stop Automation", variant="stop")
                
                execution_log = gr.Textbox(
                    label="📋 Execution Log",
                    value="No log available",
                    interactive=False,
                    lines=20,
                    max_lines=50
                )
            
            # Event handlers
            def refresh_status():
                return self.get_status()
            
            turing_execute_btn.click(
                fn=self.execute_turing_automation,
                inputs=[turing_api_key, turing_provider],
                outputs=[turing_status]
            )
            
            universal_execute_btn.click(
                fn=self.execute_universal_automation,
                inputs=[universal_api_key, universal_provider, site_url, task_description],
                outputs=[universal_status]
            )
            
            refresh_btn.click(
                fn=refresh_status,
                outputs=[turing_status, turing_result, execution_log]
            )
            
            stop_btn.click(
                fn=self.stop_automation,
                outputs=[turing_status]
            )
            
            # Auto-refresh every 5 seconds
            interface.load(
                fn=refresh_status,
                outputs=[turing_status, turing_result, execution_log],
                every=5
            )
        
        return interface

def main():
    """Main function to launch the web interface"""
    print("🚀 Starting Simple Universal Web Automation Web Interface...")
    print("🤖 Features: Turing.com automation, Universal website support")
    print("🎯 Primary example: Complete all Turing.com quizzes automatically")
    print()
    
    try:
        # Create web interface
        webui = RemoteAgentWebUI()
        interface = webui.create_interface()
        
        print("🌐 Starting web interface...")
        print("📍 Access at: http://127.0.0.1:7790")
        print("💡 Features:")
        print("   • 🎯 Turing.com quiz automation")
        print("   • 🌐 Universal website task completion")
        print("   • 🤖 Multi-LLM support (Anthropic, OpenAI, Google)")
        print("   • 📋 Real-time execution monitoring")
        print()
        
        interface.launch(
            server_name="127.0.0.1",
            server_port=7790,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

if __name__ == "__main__":
    main()
