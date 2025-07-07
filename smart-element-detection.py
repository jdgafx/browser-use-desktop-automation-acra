#!/usr/bin/env python3
"""
Smart Element Detection for Playwright Automation
Provides intelligent element finding without AI
"""

import re
from typing import List, Dict, Optional, Tuple
from playwright.async_api import Page, Locator

class SmartElementDetector:
    """Intelligent element detection using heuristics and patterns"""
    
    def __init__(self):
        # Common patterns for different element types
        self.login_patterns = {
            'username': [
                'input[name*="user"]', 'input[name*="email"]', 'input[name*="login"]',
                'input[id*="user"]', 'input[id*="email"]', 'input[id*="login"]',
                'input[placeholder*="username" i]', 'input[placeholder*="email" i]',
                'input[type="email"]', 'input[autocomplete="username"]'
            ],
            'password': [
                'input[type="password"]', 'input[name*="pass"]', 'input[id*="pass"]',
                'input[placeholder*="password" i]', 'input[autocomplete="current-password"]'
            ],
            'submit': [
                'button[type="submit"]', 'input[type="submit"]',
                'button:has-text("login" i)', 'button:has-text("sign in" i)',
                'button:has-text("log in" i)', 'a:has-text("login" i)'
            ]
        }
        
        self.form_patterns = {
            'name': [
                'input[name*="name"]', 'input[id*="name"]',
                'input[placeholder*="name" i]', 'input[autocomplete="name"]'
            ],
            'first_name': [
                'input[name*="first"]', 'input[id*="first"]',
                'input[placeholder*="first" i]', 'input[autocomplete="given-name"]'
            ],
            'last_name': [
                'input[name*="last"]', 'input[id*="last"]',
                'input[placeholder*="last" i]', 'input[autocomplete="family-name"]'
            ],
            'phone': [
                'input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]',
                'input[placeholder*="phone" i]', 'input[autocomplete="tel"]'
            ],
            'address': [
                'input[name*="address"]', 'input[id*="address"]',
                'textarea[name*="address"]', 'input[autocomplete="street-address"]'
            ],
            'city': [
                'input[name*="city"]', 'input[id*="city"]',
                'input[autocomplete="address-level2"]'
            ],
            'state': [
                'select[name*="state"]', 'input[name*="state"]',
                'select[id*="state"]', 'input[autocomplete="address-level1"]'
            ],
            'zip': [
                'input[name*="zip"]', 'input[name*="postal"]',
                'input[id*="zip"]', 'input[autocomplete="postal-code"]'
            ],
            'file_upload': [
                'input[type="file"]', 'input[accept*="pdf"]',
                'input[accept*="doc"]', 'input[name*="resume"]',
                'input[name*="cv"]', 'input[id*="upload"]'
            ]
        }
        
        self.button_patterns = {
            'submit': ['submit', 'send', 'apply', 'continue', 'next', 'save'],
            'cancel': ['cancel', 'back', 'previous', 'close'],
            'upload': ['upload', 'attach', 'browse', 'choose file'],
            'search': ['search', 'find', 'go', 'lookup']
        }
    
    async def find_login_elements(self, page: Page) -> Dict[str, Optional[Locator]]:
        """Find login form elements"""
        elements = {}
        
        # Find username/email field
        elements['username'] = await self._find_element_by_patterns(
            page, self.login_patterns['username']
        )
        
        # Find password field
        elements['password'] = await self._find_element_by_patterns(
            page, self.login_patterns['password']
        )
        
        # Find submit button
        elements['submit'] = await self._find_element_by_patterns(
            page, self.login_patterns['submit']
        )
        
        return elements
    
    async def find_form_elements(self, page: Page) -> Dict[str, Optional[Locator]]:
        """Find common form elements"""
        elements = {}
        
        for field_type, patterns in self.form_patterns.items():
            elements[field_type] = await self._find_element_by_patterns(page, patterns)
        
        return elements
    
    async def find_buttons_by_text(self, page: Page, button_type: str) -> List[Locator]:
        """Find buttons by text content"""
        if button_type not in self.button_patterns:
            return []
        
        buttons = []
        text_patterns = self.button_patterns[button_type]
        
        for pattern in text_patterns:
            # Try different button selectors with text matching
            selectors = [
                f'button:has-text("{pattern}" i)',
                f'input[value*="{pattern}" i]',
                f'a:has-text("{pattern}" i)',
                f'[role="button"]:has-text("{pattern}" i)'
            ]
            
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    buttons.extend(elements)
                except:
                    continue
        
        return buttons
    
    async def find_file_upload_elements(self, page: Page) -> List[Locator]:
        """Find file upload elements"""
        return await self._find_elements_by_patterns(
            page, self.form_patterns['file_upload']
        )
    
    async def analyze_page_structure(self, page: Page) -> Dict:
        """Analyze page structure and identify key elements"""
        analysis = {
            'title': await page.title(),
            'url': page.url,
            'forms': [],
            'buttons': [],
            'inputs': [],
            'links': [],
            'has_login_form': False,
            'has_file_upload': False
        }
        
        # Count different element types
        analysis['forms'] = await page.locator('form').count()
        analysis['buttons'] = await page.locator('button').count()
        analysis['inputs'] = await page.locator('input').count()
        analysis['links'] = await page.locator('a').count()
        
        # Check for login form
        login_elements = await self.find_login_elements(page)
        analysis['has_login_form'] = bool(
            login_elements['username'] and login_elements['password']
        )
        
        # Check for file upload
        file_uploads = await self.find_file_upload_elements(page)
        analysis['has_file_upload'] = len(file_uploads) > 0
        
        # Get visible text content (first 500 chars)
        try:
            text_content = await page.locator('body').text_content()
            analysis['text_preview'] = text_content[:500] if text_content else ""
        except:
            analysis['text_preview'] = ""
        
        return analysis
    
    async def suggest_automation_actions(self, page: Page) -> List[Dict]:
        """Suggest possible automation actions based on page content"""
        suggestions = []
        
        # Check for login form
        login_elements = await self.find_login_elements(page)
        if login_elements['username'] and login_elements['password']:
            suggestions.append({
                'action': 'login',
                'description': 'Login form detected',
                'elements': login_elements,
                'confidence': 0.9
            })
        
        # Check for file upload
        file_uploads = await self.find_file_upload_elements(page)
        if file_uploads:
            suggestions.append({
                'action': 'file_upload',
                'description': f'File upload field(s) detected ({len(file_uploads)})',
                'elements': file_uploads,
                'confidence': 0.8
            })
        
        # Check for forms
        form_elements = await self.find_form_elements(page)
        filled_fields = {k: v for k, v in form_elements.items() if v}
        if filled_fields:
            suggestions.append({
                'action': 'fill_form',
                'description': f'Form fields detected: {", ".join(filled_fields.keys())}',
                'elements': filled_fields,
                'confidence': 0.7
            })
        
        # Check for common buttons
        for button_type in self.button_patterns:
            buttons = await self.find_buttons_by_text(page, button_type)
            if buttons:
                suggestions.append({
                    'action': f'click_{button_type}',
                    'description': f'{button_type.title()} button(s) detected ({len(buttons)})',
                    'elements': buttons,
                    'confidence': 0.6
                })
        
        return suggestions
    
    async def _find_element_by_patterns(self, page: Page, patterns: List[str]) -> Optional[Locator]:
        """Find first matching element from a list of patterns"""
        for pattern in patterns:
            try:
                element = page.locator(pattern).first
                if await element.count() > 0:
                    return element
            except:
                continue
        return None
    
    async def _find_elements_by_patterns(self, page: Page, patterns: List[str]) -> List[Locator]:
        """Find all matching elements from a list of patterns"""
        elements = []
        for pattern in patterns:
            try:
                found = await page.locator(pattern).all()
                elements.extend(found)
            except:
                continue
        return elements
