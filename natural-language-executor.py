#!/usr/bin/env python3
"""
Natural Language Executor for Playwright Automation
Executes automation actions derived from natural language commands
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any
from playwright.async_api import Page, Browser, BrowserContext
from pathlib import Path

# Import our modules using dynamic loading
import importlib.util

def load_nlp_module():
    """Load the natural language processor module"""
    spec = importlib.util.spec_from_file_location("natural_language_processor", "natural-language-processor.py")
    nlp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nlp_module)
    return nlp_module.NaturalLanguageProcessor, nlp_module.AutomationAction, nlp_module.ActionType

NaturalLanguageProcessor, AutomationAction, ActionType = load_nlp_module()

class NaturalLanguageExecutor:
    """Executes automation actions from natural language processing"""
    
    def __init__(self, page: Page, smart_detector=None, templates=None):
        self.page = page
        self.smart_detector = smart_detector
        self.templates = templates
        self.nlp = NaturalLanguageProcessor()
        self.execution_log = []
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a natural language command"""
        try:
            # Process the command into actions
            actions = self.nlp.process_command(command)
            
            if not actions:
                return {
                    "success": False,
                    "message": "Could not understand the command. Please try rephrasing.",
                    "suggestions": self.nlp.get_action_suggestions(command)
                }
            
            results = []
            for action in actions:
                result = await self._execute_action(action)
                results.append(result)
                
                # Log the action
                self.execution_log.append({
                    "command": command,
                    "action": action,
                    "result": result,
                    "timestamp": time.time()
                })
                
                # If action failed, stop execution
                if not result.get("success", False):
                    break
            
            # Combine results
            success = all(r.get("success", False) for r in results)
            messages = [r.get("message", "") for r in results if r.get("message")]
            
            return {
                "success": success,
                "message": " | ".join(messages) if messages else "Command executed successfully",
                "actions_executed": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing command: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute a single automation action"""
        try:
            if action.action_type == ActionType.NAVIGATE:
                return await self._execute_navigate(action)
            elif action.action_type == ActionType.CLICK:
                return await self._execute_click(action)
            elif action.action_type == ActionType.TYPE:
                return await self._execute_type(action)
            elif action.action_type == ActionType.SCROLL:
                return await self._execute_scroll(action)
            elif action.action_type == ActionType.WAIT:
                return await self._execute_wait(action)
            elif action.action_type == ActionType.SCREENSHOT:
                return await self._execute_screenshot(action)
            elif action.action_type == ActionType.EXTRACT:
                return await self._execute_extract(action)
            elif action.action_type == ActionType.SEARCH:
                return await self._execute_search(action)
            elif action.action_type == ActionType.LOGIN:
                return await self._execute_login(action)
            elif action.action_type == ActionType.FILL_FORM:
                return await self._execute_fill_form(action)
            elif action.action_type == ActionType.CUSTOM:
                return await self._execute_custom(action)
            else:
                return {
                    "success": False,
                    "message": f"Action type {action.action_type} not implemented yet"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing {action.action_type}: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_navigate(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute navigation action"""
        url = action.target

        try:
            # Navigate with longer timeout
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for network to be idle with longer timeout
            try:
                await self.page.wait_for_load_state("networkidle", timeout=20000)
            except:
                # If networkidle times out, just wait for load state
                await self.page.wait_for_load_state("load", timeout=10000)

            return {
                "success": True,
                "message": f"Navigated to {url}",
                "url": self.page.url
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Navigation failed: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_click(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute click action"""
        target = action.target
        
        # Try to find the element using smart detection
        element = await self._find_element(target)
        
        if element:
            await element.click()
            return {
                "success": True,
                "message": f"Clicked on {target}"
            }
        else:
            return {
                "success": False,
                "message": f"Could not find element: {target}"
            }
    
    async def _execute_type(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute typing action"""
        target = action.target
        value = action.value
        
        # Find the input element
        element = await self._find_input_element(target)
        
        if element:
            await element.clear()
            await element.type(value)
            return {
                "success": True,
                "message": f"Typed '{value}' in {target}"
            }
        else:
            return {
                "success": False,
                "message": f"Could not find input field: {target}"
            }
    
    async def _execute_scroll(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute scroll action"""
        target = action.target or "down"
        
        if "down" in target.lower():
            await self.page.keyboard.press("PageDown")
        elif "up" in target.lower():
            await self.page.keyboard.press("PageUp")
        elif "top" in target.lower():
            await self.page.keyboard.press("Home")
        elif "bottom" in target.lower():
            await self.page.keyboard.press("End")
        else:
            # Scroll to specific element
            element = await self._find_element(target)
            if element:
                await element.scroll_into_view_if_needed()
        
        return {
            "success": True,
            "message": f"Scrolled {target}"
        }
    
    async def _execute_wait(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute wait action"""
        if action.value and action.value.isdigit():
            seconds = int(action.value)
            await asyncio.sleep(seconds)
            return {
                "success": True,
                "message": f"Waited for {seconds} seconds"
            }
        elif action.target:
            # Wait for element or condition
            try:
                await self.page.wait_for_selector(action.target, timeout=10000)
                return {
                    "success": True,
                    "message": f"Waited for {action.target}"
                }
            except:
                return {
                    "success": False,
                    "message": f"Timeout waiting for {action.target}"
                }
        else:
            await asyncio.sleep(2)  # Default wait
            return {
                "success": True,
                "message": "Waited for 2 seconds"
            }
    
    async def _execute_screenshot(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute screenshot action"""
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        
        await self.page.screenshot(path=filename, full_page=True)
        
        return {
            "success": True,
            "message": f"Screenshot saved as {filename}",
            "filename": filename
        }
    
    async def _execute_extract(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute extraction action"""
        target = action.target
        
        # Try to extract text from the specified element or page
        if "title" in target.lower():
            title = await self.page.title()
            return {
                "success": True,
                "message": f"Page title: {title}",
                "data": title
            }
        elif "url" in target.lower():
            url = self.page.url
            return {
                "success": True,
                "message": f"Current URL: {url}",
                "data": url
            }
        else:
            # Try to find and extract text from element
            element = await self._find_element(target)
            if element:
                text = await element.text_content()
                return {
                    "success": True,
                    "message": f"Extracted text from {target}: {text[:100]}...",
                    "data": text
                }
            else:
                return {
                    "success": False,
                    "message": f"Could not find element to extract: {target}"
                }
    
    async def _execute_search(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute search action"""
        query = action.value
        
        # Look for search input field
        search_selectors = [
            'input[type="search"]',
            'input[name*="search"]',
            'input[placeholder*="search"]',
            'input[id*="search"]',
            '.search input',
            '#search input'
        ]
        
        for selector in search_selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=2000)
                if element:
                    await element.clear()
                    await element.type(query)
                    await element.press("Enter")
                    return {
                        "success": True,
                        "message": f"Searched for '{query}'"
                    }
            except:
                continue
        
        return {
            "success": False,
            "message": "Could not find search field"
        }
    
    async def _execute_login(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute login action"""
        # Use templates if available
        if self.templates:
            try:
                # Prepare login data from action
                login_data = {
                    'site': action.target or 'current site',
                    'method': action.value or 'standard'
                }

                result = await self.templates.execute_template('login', self.page, login_data)

                if result.get('success'):
                    return {
                        "success": True,
                        "message": f"Login successful to {login_data['site']}",
                        "details": result.get('steps', [])
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Login failed: {result.get('error', 'Unknown error')}",
                        "details": result.get('steps', [])
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Login failed: {str(e)}"
                }
        else:
            # Fallback login without templates
            try:
                # Look for common login elements - try visible elements first
                login_selectors = [
                    'a:has-text("Sign in")', 'a:has-text("Login")', 'a:has-text("Log in")',
                    'button:has-text("Sign in")', 'button:has-text("Login")', 'button:has-text("Log in")',
                    'a:has-text("Sign In")', 'a:has-text("Log In")',
                    '[data-testid*="login"]', '[data-testid*="signin"]',
                    '.login-button', '.signin-button', '#login', '#signin',
                    'a[href*="login"]', 'a[href*="signin"]', 'a[href*="auth"]'
                ]

                for selector in login_selectors:
                    try:
                        # Wait for element and check if it's visible
                        element = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                        if element:
                            await element.click()
                            # Wait a bit for login form to appear
                            await self.page.wait_for_timeout(2000)
                            return {
                                "success": True,
                                "message": f"Clicked login element: {selector}"
                            }
                    except:
                        continue

                # If no visible login elements found, try to find any login-related text
                try:
                    # Look for text-based login links
                    login_text_elements = await self.page.query_selector_all('a, button')
                    for element in login_text_elements:
                        text = await element.text_content()
                        if text and any(word in text.lower() for word in ['sign in', 'login', 'log in', 'sign up']):
                            try:
                                await element.click()
                                await self.page.wait_for_timeout(2000)
                                return {
                                    "success": True,
                                    "message": f"Clicked login text: {text}"
                                }
                            except:
                                continue
                except:
                    pass

                return {
                    "success": False,
                    "message": "Could not find visible login elements"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Login failed: {str(e)}"
                }
    
    async def _execute_fill_form(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute form filling action"""
        # Use templates if available
        if self.templates:
            try:
                # Prepare form data from action
                form_data = {
                    'target': action.target or 'form',
                    'data': action.value or {}
                }

                result = await self.templates.execute_template('form_filling', self.page, form_data)

                if result.get('success'):
                    return {
                        "success": True,
                        "message": "Form filled successfully",
                        "details": result.get('steps', [])
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Form filling failed: {result.get('error', 'Unknown error')}",
                        "details": result.get('steps', [])
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Form filling failed: {str(e)}"
                }
        else:
            return {
                "success": False,
                "message": "Form templates not available"
            }
    
    async def _find_element(self, description: str):
        """Find an element based on description"""
        # Use smart detector if available
        if self.smart_detector:
            try:
                elements = await self.smart_detector.find_elements_by_description(self.page, description)
                return elements[0] if elements else None
            except:
                pass
        
        # Fallback to simple text matching
        try:
            # Try exact text match
            element = await self.page.get_by_text(description).first
            if await element.count() > 0:
                return element
        except:
            pass
        
        # Try partial text match
        try:
            element = await self.page.get_by_text(description, exact=False).first
            if await element.count() > 0:
                return element
        except:
            pass
        
        return None
    
    async def _find_input_element(self, description: str):
        """Find an input element based on description"""
        # Common input selectors
        selectors = [
            f'input[placeholder*="{description}"]',
            f'input[name*="{description}"]',
            f'input[id*="{description}"]',
            f'textarea[placeholder*="{description}"]',
            f'[aria-label*="{description}"]'
        ]
        
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=2000)
                if element:
                    return element
            except:
                continue
        
        # Fallback to generic input
        try:
            return await self.page.wait_for_selector('input', timeout=2000)
        except:
            return None

    async def _execute_custom(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute custom complex actions like completing tasks with specific scores"""
        try:
            target = action.target or "task"
            score = action.value or "100%"

            # For complex tasks, break them down into simpler actions
            if "quiz" in target.lower() or "test" in target.lower() or "assessment" in target.lower():
                # Look for quiz/test elements
                quiz_selectors = [
                    'a[href*="quiz"]', 'a[href*="test"]', 'a[href*="assessment"]',
                    'button:has-text("Start")', 'button:has-text("Begin")', 'button:has-text("Take")',
                    '.quiz-item', '.test-item', '.assessment-item',
                    '[data-testid*="quiz"]', '[data-testid*="test"]'
                ]

                for selector in quiz_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        if elements:
                            # Click on available quizzes/tests
                            for element in elements[:3]:  # Limit to first 3
                                await element.click()
                                await self.page.wait_for_timeout(1000)

                            return {
                                "success": True,
                                "message": f"Started {len(elements)} {target} items",
                                "details": f"Attempting to complete with {score} score"
                            }
                    except:
                        continue

            # Generic custom action - try to find and interact with relevant elements
            keywords = target.lower().split()
            for keyword in keywords:
                try:
                    # Look for elements containing the keyword
                    element = await self.page.query_selector(f'text="{keyword}"')
                    if not element:
                        element = await self.page.query_selector(f'[aria-label*="{keyword}"]')
                    if not element:
                        element = await self.page.query_selector(f'[title*="{keyword}"]')

                    if element:
                        await element.click()
                        return {
                            "success": True,
                            "message": f"Clicked on {keyword} element",
                            "details": f"Working towards {target} with {score} target"
                        }
                except:
                    continue

            return {
                "success": False,
                "message": f"Could not find elements for custom task: {target}",
                "details": f"Target score: {score}"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing custom action: {str(e)}",
                "error": str(e)
            }
