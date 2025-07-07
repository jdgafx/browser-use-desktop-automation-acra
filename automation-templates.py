#!/usr/bin/env python3
"""
Automation Templates for Common Tasks
Pre-built workflows for browser automation without AI
"""

import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import Page

class AutomationTemplates:
    """Pre-built automation templates for common tasks"""

    def __init__(self, detector=None):
        self.detector = detector
        self.templates = {
            'login': self.login_template,
            'job_application': self.job_application_template,
            'form_filling': self.form_filling_template,
            'file_upload': self.file_upload_template,
            'search': self.search_template,
            'social_media_post': self.social_media_template,
            'contact_form': self.contact_form_template,
            'newsletter_signup': self.newsletter_signup_template
        }
    
    async def execute_template(self, template_name: str, page: Page, 
                             data: Dict, interactive_callback=None) -> Dict:
        """Execute a specific automation template"""
        if template_name not in self.templates:
            return {'success': False, 'error': f'Template {template_name} not found'}
        
        try:
            return await self.templates[template_name](page, data, interactive_callback)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def login_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Login automation template with comprehensive login handling"""
        result = {'success': False, 'steps': []}

        # First, try to find and click a "Sign In" or "Login" link if we're not on a login page
        current_url = page.url.lower()
        if 'login' not in current_url and 'signin' not in current_url and 'auth' not in current_url:
            # Look for login/signin links first
            login_link_selectors = [
                'a:has-text("Sign in")', 'a:has-text("Login")', 'a:has-text("Log in")',
                'a:has-text("Sign In")', 'a:has-text("Log In")',
                'button:has-text("Sign in")', 'button:has-text("Login")', 'button:has-text("Log in")',
                'a[href*="login"]', 'a[href*="signin"]', 'a[href*="auth"]'
            ]

            for selector in login_link_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000, state='visible')
                    if element:
                        await element.click()
                        await page.wait_for_timeout(2000)  # Wait for navigation
                        result['steps'].append(f'Clicked login link: {selector}')
                        break
                except:
                    continue

        # Find login elements
        elements = await self.detector.find_login_elements(page)

        if not elements['username'] or not elements['password']:
            if callback:
                response = await callback("Login form not found automatically. Please provide CSS selectors:")
                # Handle manual selector input
                if response and 'username_selector' in response:
                    elements['username'] = page.locator(response['username_selector'])
                    elements['password'] = page.locator(response['password_selector'])

        # Fill username/email
        if elements['username'] and 'username' in data:
            await elements['username'].fill(data['username'])
            result['steps'].append('Username/email filled')

            # Some sites require clicking "Next" after username
            next_buttons = await self.detector.find_buttons_by_text(page, 'submit')
            next_button = None
            for btn in next_buttons:
                btn_text = await btn.text_content() or ""
                if 'next' in btn_text.lower():
                    next_button = btn
                    break

            if next_button:
                await next_button.click()
                await page.wait_for_timeout(2000)  # Wait for password field to appear
                result['steps'].append('Clicked Next after username')

                # Re-find password field after navigation
                elements['password'] = await self.detector._find_element_by_patterns(
                    page, self.detector.login_patterns['password']
                )

        # Fill password
        if elements['password'] and 'password' in data:
            await elements['password'].fill(data['password'])
            result['steps'].append('Password filled')

        # Handle 2FA if needed
        if callback and data.get('requires_2fa'):
            code = await callback("Please enter 2FA code:")
            if code and 'code' in code:
                # Try to find 2FA input
                tfa_input = await self.detector._find_element_by_patterns(page, [
                    'input[name*="code"]', 'input[id*="code"]', 'input[placeholder*="code" i]',
                    'input[name*="otp"]', 'input[id*="otp"]', 'input[name*="token"]'
                ])
                if tfa_input:
                    await tfa_input.fill(code['code'])
                    result['steps'].append('2FA code entered')

        # Submit form
        if elements['submit']:
            await elements['submit'].click()
            result['steps'].append('Login submitted')
        elif elements['password']:
            # Try pressing Enter on password field
            await elements['password'].press('Enter')
            result['steps'].append('Login submitted via Enter key')

        # Wait for navigation or error
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)

            # Check if login was successful by looking for common indicators
            current_url = page.url
            page_content = await page.content()

            # Common success indicators
            success_indicators = [
                'dashboard', 'profile', 'account', 'welcome', 'logout'
            ]

            # Common failure indicators
            failure_indicators = [
                'invalid', 'incorrect', 'error', 'failed', 'try again'
            ]

            if any(indicator in current_url.lower() or indicator in page_content.lower()
                   for indicator in success_indicators):
                result['success'] = True
                result['steps'].append('Login appears successful')
            elif any(indicator in page_content.lower() for indicator in failure_indicators):
                result['success'] = False
                result['steps'].append('Login appears to have failed')
            else:
                result['success'] = True  # Assume success if no clear indicators
                result['steps'].append('Login completed (status unclear)')

        except Exception as e:
            result['steps'].append(f'Login timeout or error: {str(e)}')

        return result
    
    async def job_application_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Job application automation template"""
        result = {'success': False, 'steps': []}
        
        # Find form elements
        elements = await self.detector.find_form_elements(page)
        
        # Fill personal information
        personal_fields = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'name': data.get('full_name'),
            'phone': data.get('phone'),
            'address': data.get('address'),
            'city': data.get('city'),
            'state': data.get('state'),
            'zip': data.get('zip_code')
        }
        
        for field, value in personal_fields.items():
            if elements.get(field) and value:
                await elements[field].fill(str(value))
                result['steps'].append(f'Filled {field}')
        
        # Handle file uploads (resume, cover letter)
        file_uploads = await self.detector.find_file_upload_elements(page)
        if file_uploads and data.get('resume_path'):
            # Try to identify which upload is for resume
            for upload in file_uploads:
                try:
                    # Check if this looks like a resume upload
                    upload_text = await upload.get_attribute('name') or ''
                    upload_text += await upload.get_attribute('id') or ''
                    
                    if any(word in upload_text.lower() for word in ['resume', 'cv']):
                        await upload.set_input_files(data['resume_path'])
                        result['steps'].append('Resume uploaded')
                        break
                except:
                    continue
        
        # Interactive prompts for complex fields
        if callback:
            # Ask about additional fields
            suggestions = await self.detector.suggest_automation_actions(page)
            if suggestions:
                response = await callback(f"Found additional fields: {[s['description'] for s in suggestions]}. Continue?")
                if response and response.get('continue'):
                    result['steps'].append('User chose to continue with additional fields')
        
        result['success'] = True
        return result
    
    async def form_filling_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Generic form filling template"""
        result = {'success': False, 'steps': []}
        
        # Get all form elements
        elements = await self.detector.find_form_elements(page)
        
        # Fill all matching fields
        for field_type, element in elements.items():
            if element and field_type in data:
                try:
                    value = data[field_type]
                    if isinstance(value, str):
                        await element.fill(value)
                        result['steps'].append(f'Filled {field_type}')
                    elif isinstance(value, list):  # For select options
                        await element.select_option(value[0])
                        result['steps'].append(f'Selected {field_type}')
                except Exception as e:
                    result['steps'].append(f'Failed to fill {field_type}: {str(e)}')
        
        result['success'] = True
        return result
    
    async def file_upload_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """File upload automation template"""
        result = {'success': False, 'steps': []}
        
        file_uploads = await self.detector.find_file_upload_elements(page)
        
        if not file_uploads:
            result['error'] = 'No file upload elements found'
            return result
        
        files_to_upload = data.get('files', [])
        if isinstance(files_to_upload, str):
            files_to_upload = [files_to_upload]
        
        for i, upload_element in enumerate(file_uploads):
            if i < len(files_to_upload):
                try:
                    await upload_element.set_input_files(files_to_upload[i])
                    result['steps'].append(f'Uploaded file: {files_to_upload[i]}')
                except Exception as e:
                    result['steps'].append(f'Failed to upload file: {str(e)}')
        
        result['success'] = True
        return result
    
    async def search_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Search automation template"""
        result = {'success': False, 'steps': []}
        
        search_query = data.get('query', '')
        if not search_query:
            result['error'] = 'No search query provided'
            return result
        
        # Find search input
        search_patterns = [
            'input[name*="search"]', 'input[id*="search"]',
            'input[placeholder*="search" i]', 'input[type="search"]',
            'input[name="q"]', 'input[id="q"]'
        ]
        
        search_input = await self.detector._find_element_by_patterns(page, search_patterns)
        
        if search_input:
            await search_input.fill(search_query)
            result['steps'].append(f'Entered search query: {search_query}')
            
            # Try to submit
            await search_input.press('Enter')
            result['steps'].append('Search submitted')
            
            # Wait for results
            await page.wait_for_load_state('networkidle', timeout=10000)
            result['success'] = True
        else:
            result['error'] = 'Search input not found'
        
        return result
    
    async def social_media_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Social media posting template"""
        result = {'success': False, 'steps': []}
        
        post_content = data.get('content', '')
        if not post_content:
            result['error'] = 'No post content provided'
            return result
        
        # Find post input (common patterns for social media)
        post_patterns = [
            'textarea[placeholder*="What\'s on your mind" i]',
            'textarea[placeholder*="What\'s happening" i]',
            'div[contenteditable="true"]',
            'textarea[name*="post"]',
            'textarea[id*="post"]'
        ]
        
        post_input = await self.detector._find_element_by_patterns(page, post_patterns)
        
        if post_input:
            await post_input.fill(post_content)
            result['steps'].append('Post content entered')
            
            # Find and click post button
            post_buttons = await self.detector.find_buttons_by_text(page, 'submit')
            if post_buttons:
                await post_buttons[0].click()
                result['steps'].append('Post submitted')
                result['success'] = True
        else:
            result['error'] = 'Post input not found'
        
        return result
    
    async def contact_form_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Contact form automation template"""
        result = {'success': False, 'steps': []}
        
        # Standard contact form fields
        contact_fields = {
            'name': data.get('name'),
            'email': data.get('email'),
            'subject': data.get('subject'),
            'message': data.get('message')
        }
        
        # Find and fill contact form fields
        for field, value in contact_fields.items():
            if value:
                patterns = [
                    f'input[name*="{field}"]',
                    f'input[id*="{field}"]',
                    f'textarea[name*="{field}"]',
                    f'textarea[id*="{field}"]'
                ]
                
                element = await self.detector._find_element_by_patterns(page, patterns)
                if element:
                    await element.fill(str(value))
                    result['steps'].append(f'Filled {field}')
        
        result['success'] = True
        return result
    
    async def newsletter_signup_template(self, page: Page, data: Dict, callback=None) -> Dict:
        """Newsletter signup automation template"""
        result = {'success': False, 'steps': []}
        
        email = data.get('email', '')
        if not email:
            result['error'] = 'No email provided'
            return result
        
        # Find email input for newsletter
        email_patterns = [
            'input[type="email"]',
            'input[name*="email"]',
            'input[placeholder*="email" i]',
            'input[id*="email"]'
        ]
        
        email_input = await self.detector._find_element_by_patterns(page, email_patterns)
        
        if email_input:
            await email_input.fill(email)
            result['steps'].append('Email entered')
            
            # Find subscribe button
            subscribe_buttons = await self.detector.find_buttons_by_text(page, 'submit')
            if subscribe_buttons:
                await subscribe_buttons[0].click()
                result['steps'].append('Newsletter signup submitted')
                result['success'] = True
        else:
            result['error'] = 'Email input not found'
        
        return result
    
    def get_available_templates(self) -> List[Dict]:
        """Get list of available automation templates"""
        return [
            {'name': 'login', 'description': 'Login to websites', 'fields': ['username', 'password']},
            {'name': 'job_application', 'description': 'Fill job application forms', 'fields': ['personal_info', 'resume_path']},
            {'name': 'form_filling', 'description': 'Fill generic forms', 'fields': ['form_data']},
            {'name': 'file_upload', 'description': 'Upload files', 'fields': ['files']},
            {'name': 'search', 'description': 'Perform searches', 'fields': ['query']},
            {'name': 'social_media_post', 'description': 'Post to social media', 'fields': ['content']},
            {'name': 'contact_form', 'description': 'Fill contact forms', 'fields': ['name', 'email', 'message']},
            {'name': 'newsletter_signup', 'description': 'Sign up for newsletters', 'fields': ['email']}
        ]
