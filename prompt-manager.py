#!/usr/bin/env python3
"""
Prompt Manager for Enhanced Playwright Automation
Handles interactive prompting during automation execution
"""

import asyncio
import queue
import threading
import time
from typing import Dict, List, Optional, Any, Callable

class PromptManager:
    """Manages interactive prompts during automation execution"""
    
    def __init__(self):
        self.prompt_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.pending_prompts: Dict[str, Dict[str, Any]] = {}
        self.prompt_counter = 0
    
    async def prompt_user(self, message: str, options: Optional[List[str]] = None, timeout: int = 30) -> str:
        """
        Prompt user for input during automation
        
        Args:
            message: The prompt message
            options: Optional list of valid responses
            timeout: Timeout in seconds
            
        Returns:
            User's response or timeout message
        """
        prompt_id = f"prompt_{self.prompt_counter}_{int(time.time())}"
        self.prompt_counter += 1
        
        prompt_data = {
            'id': prompt_id,
            'message': message,
            'options': options or [],
            'timestamp': time.time(),
            'timeout': timeout,
            'status': 'pending'
        }
        
        # Store prompt
        self.pending_prompts[prompt_id] = prompt_data
        
        # Add to queue for UI
        self.prompt_queue.put(prompt_data)
        
        # Wait for response with timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for response
                if not self.response_queue.empty():
                    response_data = self.response_queue.get_nowait()
                    if response_data.get('prompt_id') == prompt_id:
                        self.pending_prompts[prompt_id]['status'] = 'answered'
                        self.pending_prompts[prompt_id]['response'] = response_data.get('response', '')
                        return response_data.get('response', '')
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except queue.Empty:
                continue
        
        # Timeout
        self.pending_prompts[prompt_id]['status'] = 'timeout'
        return f"⏰ Timeout after {timeout} seconds"
    
    def submit_response(self, prompt_id: str, response: str) -> bool:
        """
        Submit a response to a pending prompt
        
        Args:
            prompt_id: ID of the prompt to respond to
            response: User's response
            
        Returns:
            True if response was submitted successfully
        """
        if prompt_id in self.pending_prompts:
            response_data = {
                'prompt_id': prompt_id,
                'response': response,
                'timestamp': time.time()
            }
            self.response_queue.put(response_data)
            return True
        return False
    
    def get_pending_prompts(self) -> List[Dict[str, Any]]:
        """Get all pending prompts"""
        return [
            prompt for prompt in self.pending_prompts.values()
            if prompt['status'] == 'pending'
        ]
    
    def get_latest_prompt(self) -> Optional[Dict[str, Any]]:
        """Get the most recent pending prompt"""
        pending = self.get_pending_prompts()
        if pending:
            return max(pending, key=lambda p: p['timestamp'])
        return None
    
    def clear_old_prompts(self, max_age_seconds: int = 300):
        """Clear prompts older than max_age_seconds"""
        current_time = time.time()
        to_remove = []
        
        for prompt_id, prompt_data in self.pending_prompts.items():
            if current_time - prompt_data['timestamp'] > max_age_seconds:
                to_remove.append(prompt_id)
        
        for prompt_id in to_remove:
            del self.pending_prompts[prompt_id]
    
    def format_prompt_for_ui(self, prompt_data: Dict[str, Any]) -> str:
        """Format prompt data for UI display"""
        message = prompt_data['message']
        options = prompt_data.get('options', [])
        
        formatted = f"🤖 {message}\n"
        if options:
            formatted += f"Options: {', '.join(options)}\n"
        
        formatted += f"ID: {prompt_data['id']}"
        return formatted
    
    def get_prompt_history(self) -> List[Dict[str, Any]]:
        """Get history of all prompts (answered and pending)"""
        return list(self.pending_prompts.values())
    
    def clear_all_prompts(self):
        """Clear all prompts and queues"""
        self.pending_prompts.clear()
        
        # Clear queues
        while not self.prompt_queue.empty():
            try:
                self.prompt_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break
    
    def has_pending_prompts(self) -> bool:
        """Check if there are any pending prompts"""
        return len(self.get_pending_prompts()) > 0
    
    def get_prompt_stats(self) -> Dict[str, int]:
        """Get statistics about prompts"""
        total = len(self.pending_prompts)
        pending = len(self.get_pending_prompts())
        answered = len([p for p in self.pending_prompts.values() if p['status'] == 'answered'])
        timeout = len([p for p in self.pending_prompts.values() if p['status'] == 'timeout'])
        
        return {
            'total': total,
            'pending': pending,
            'answered': answered,
            'timeout': timeout
        }
