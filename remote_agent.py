#!/usr/bin/env python3
"""
Simple Universal Web Automation Remote Agent
AI that can complete any task on any website

Based on the Simple Universal Web Automation PRD
Primary Example: "Log into turing.com with Google, find quizzes, complete all remaining ones"
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Browser automation
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

# AI/LLM integration
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("Installing required AI packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain-anthropic", "langchain-openai", "langchain-google-genai"])
    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI

# Computer vision for element detection
try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    print("Installing computer vision packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "pillow", "numpy"])
    import cv2
    import numpy as np
    from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETAKE_AVAILABLE = "retake_available"

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CODING = "coding"
    ESSAY = "essay"
    MATH = "math"
    FORM_FILL = "form_fill"
    GENERAL = "general"

@dataclass
class QuizItem:
    title: str
    url: str
    status: TaskStatus
    start_button_selector: Optional[str] = None
    completion_indicator: Optional[str] = None

@dataclass
class Question:
    text: str
    question_type: QuestionType
    options: List[str] = None
    context: str = ""
    element_selector: str = ""

class SmartBrowserEngine:
    """Smart browser engine that understands web pages and handles authentication"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url = ""
        
    async def start_browser(self, headless: bool = False) -> bool:
        """Start browser with stealth settings"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with anti-detection settings
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                    '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            logger.info("✅ Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False
    
    async def stop_browser(self):
        """Stop browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("✅ Browser stopped successfully")
        except Exception as e:
            logger.error(f"❌ Error stopping browser: {e}")
    
    async def navigate_to(self, url: str) -> bool:
        """Navigate to URL with error handling"""
        try:
            if not self.page:
                logger.error("Browser not started")
                return False
                
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            self.current_url = self.page.url
            logger.info(f"✅ Navigated to: {self.current_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False
    
    async def take_screenshot(self, path: str = None) -> str:
        """Take screenshot for analysis"""
        try:
            if not self.page:
                return None
                
            if not path:
                path = f"screenshot_{int(time.time())}.png"
                
            await self.page.screenshot(path=path, full_page=True)
            logger.info(f"📸 Screenshot saved: {path}")
            return path
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    async def find_element_by_text(self, text: str, element_type: str = "*") -> Optional[str]:
        """Find element by text content"""
        try:
            # Try different text matching strategies
            selectors = [
                f"{element_type}:has-text('{text}')",
                f"{element_type}[text*='{text}']",
                f"{element_type}:contains('{text}')",
                f"//{element_type}[contains(text(), '{text}')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        element = await self.page.wait_for_selector(f"xpath={selector}", timeout=5000)
                    else:
                        # CSS selector
                        element = await self.page.wait_for_selector(selector, timeout=5000)
                    
                    if element:
                        return selector
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"❌ Element search failed: {e}")
            return None

class QuestionAnsweringAI:
    """AI system that can answer any type of question"""
    
    def __init__(self, api_key: str, provider: str = "anthropic"):
        self.api_key = api_key
        self.provider = provider
        self.llm = self._setup_llm()
    
    def _setup_llm(self):
        """Setup LLM based on provider"""
        try:
            if self.provider == "anthropic":
                return ChatAnthropic(
                    model="claude-3-haiku-20240307",
                    api_key=self.api_key,
                    temperature=0.1,
                    max_tokens=4000
                )
            elif self.provider == "openai":
                return ChatOpenAI(
                    model="gpt-4",
                    api_key=self.api_key,
                    temperature=0.1,
                    max_tokens=4000
                )
            elif self.provider == "google":
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.api_key,
                    temperature=0.1,
                    max_output_tokens=4000
                )
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to setup LLM: {e}")
            return None
    
    def classify_question(self, question_text: str) -> QuestionType:
        """Classify the type of question"""
        question_lower = question_text.lower()
        
        # Check for multiple choice indicators
        if any(indicator in question_lower for indicator in ['a)', 'b)', 'c)', 'd)', 'select', 'choose']):
            return QuestionType.MULTIPLE_CHOICE
        
        # Check for coding indicators
        if any(indicator in question_lower for indicator in ['code', 'function', 'algorithm', 'programming', 'python', 'javascript']):
            return QuestionType.CODING
        
        # Check for math indicators
        if any(indicator in question_lower for indicator in ['calculate', 'solve', 'equation', 'formula', 'math']):
            return QuestionType.MATH
        
        # Check for essay indicators
        if any(indicator in question_lower for indicator in ['explain', 'describe', 'discuss', 'essay', 'paragraph']):
            return QuestionType.ESSAY
        
        return QuestionType.GENERAL
    
    async def solve_question(self, question: Question) -> str:
        """Solve any type of question using AI"""
        try:
            if not self.llm:
                return "AI not available"
            
            # Create specialized prompt based on question type
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                return await self._solve_multiple_choice(question)
            elif question.question_type == QuestionType.CODING:
                return await self._solve_coding_challenge(question)
            elif question.question_type == QuestionType.ESSAY:
                return await self._generate_essay_response(question)
            elif question.question_type == QuestionType.MATH:
                return await self._solve_math_problem(question)
            else:
                return await self._generate_general_response(question)
                
        except Exception as e:
            logger.error(f"❌ Question solving failed: {e}")
            return "Unable to solve question"
    
    async def _solve_multiple_choice(self, question: Question) -> str:
        """Solve multiple choice questions"""
        prompt = f"""
        You are an expert at answering multiple choice questions. 
        
        Question: {question.text}
        
        Options: {question.options if question.options else 'Options will be provided in the interface'}
        
        Context: {question.context}
        
        Provide the best answer. If options are A, B, C, D format, respond with just the letter.
        If options are numbered, respond with just the number.
        Be concise and accurate.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def _solve_coding_challenge(self, question: Question) -> str:
        """Solve coding challenges"""
        prompt = f"""
        You are an expert programmer. Solve this coding challenge:

        Question: {question.text}
        Context: {question.context}

        Provide clean, working code. Include comments if helpful.
        Focus on correctness and efficiency.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def _generate_essay_response(self, question: Question) -> str:
        """Generate essay responses"""
        prompt = f"""
        You are an expert writer. Provide a well-structured response to this question:

        Question: {question.text}
        Context: {question.context}

        Write a clear, comprehensive response that directly addresses the question.
        Use proper structure with introduction, main points, and conclusion if appropriate.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def _solve_math_problem(self, question: Question) -> str:
        """Solve math problems"""
        prompt = f"""
        You are a mathematics expert. Solve this problem step by step:

        Problem: {question.text}
        Context: {question.context}

        Show your work clearly and provide the final answer.
        Be precise with calculations.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def _generate_general_response(self, question: Question) -> str:
        """Generate general responses"""
        prompt = f"""
        Provide a helpful and accurate response to this question:

        Question: {question.text}
        Context: {question.context}

        Be clear, concise, and directly address what is being asked.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

class TaskExecutionEngine:
    """Plans and executes complex multi-step workflows"""

    def __init__(self, browser_engine: SmartBrowserEngine, ai_solver: QuestionAnsweringAI):
        self.browser = browser_engine
        self.ai_solver = ai_solver
        self.execution_log = []

    def log(self, message: str):
        """Log execution steps"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        logger.info(log_entry)

    async def handle_google_oauth(self) -> bool:
        """Handle Google OAuth flow"""
        try:
            self.log("🔐 Handling Google OAuth...")

            # Wait for Google login page
            await self.browser.page.wait_for_url("**/accounts.google.com/**", timeout=10000)

            # This would typically require user interaction or stored credentials
            # For demo purposes, we'll wait for manual completion
            self.log("⏳ Waiting for manual Google authentication...")

            # Wait for redirect back to original site (timeout after 60 seconds)
            try:
                await self.browser.page.wait_for_url("**turing.com**", timeout=60000)
                self.log("✅ Google OAuth completed successfully")
                return True
            except:
                self.log("⚠️ OAuth timeout - may need manual intervention")
                return False

        except Exception as e:
            self.log(f"❌ OAuth failed: {e}")
            return False

    async def find_navigation_item(self, possible_names: List[str]) -> Optional[str]:
        """Find navigation item by possible names"""
        try:
            for name in possible_names:
                # Try different element types and selectors
                selectors = [
                    f"a:has-text('{name}')",
                    f"button:has-text('{name}')",
                    f"[role='menuitem']:has-text('{name}')",
                    f"nav a:has-text('{name}')",
                    f".nav-item:has-text('{name}')",
                    f".menu-item:has-text('{name}')"
                ]

                for selector in selectors:
                    try:
                        element = await self.browser.page.wait_for_selector(selector, timeout=2000)
                        if element:
                            self.log(f"✅ Found navigation item: {name}")
                            return selector
                    except:
                        continue

            self.log("❌ No navigation items found")
            return None

        except Exception as e:
            self.log(f"❌ Navigation search failed: {e}")
            return None

    async def get_all_quiz_items(self) -> List[QuizItem]:
        """Scan and identify all quiz items on the page"""
        try:
            self.log("🔍 Scanning for quiz items...")

            # Common selectors for quiz/assessment items
            quiz_selectors = [
                ".quiz-item", ".assessment-item", ".test-item",
                ".skill-test", ".challenge-item", "[data-testid*='quiz']",
                ".card", ".list-item", ".assessment-card"
            ]

            quizzes = []

            for selector in quiz_selectors:
                try:
                    elements = await self.browser.page.query_selector_all(selector)

                    for element in elements:
                        # Extract quiz information
                        title_element = await element.query_selector("h1, h2, h3, h4, .title, .name")
                        title = await title_element.text_content() if title_element else "Unknown Quiz"

                        # Try to find start button or link
                        start_button = await element.query_selector("button, a, .start-btn, .take-test")
                        start_selector = None
                        if start_button:
                            start_selector = f"{selector} button, {selector} a"

                        # Detect completion status
                        status = await self._detect_completion_status(element)

                        # Get URL if it's a link
                        url = await start_button.get_attribute("href") if start_button else self.browser.current_url

                        quiz = QuizItem(
                            title=title.strip(),
                            url=url or self.browser.current_url,
                            status=status,
                            start_button_selector=start_selector
                        )

                        quizzes.append(quiz)

                except Exception as e:
                    continue

            self.log(f"✅ Found {len(quizzes)} quiz items")
            return quizzes

        except Exception as e:
            self.log(f"❌ Quiz scanning failed: {e}")
            return []

    async def _detect_completion_status(self, quiz_element) -> TaskStatus:
        """Detect if quiz is completed, in progress, or not started"""
        try:
            # Get element text content
            text_content = await quiz_element.text_content()
            text_lower = text_content.lower() if text_content else ""

            # Check for completion indicators
            if any(indicator in text_lower for indicator in ["✓", "completed", "100%", "passed", "done"]):
                return TaskStatus.COMPLETED

            # Check for in-progress indicators
            if any(indicator in text_lower for indicator in ["in progress", "started", "continue"]):
                return TaskStatus.IN_PROGRESS

            # Check for failed/retake indicators
            if any(indicator in text_lower for indicator in ["failed", "retake", "try again"]):
                return TaskStatus.RETAKE_AVAILABLE

            # Check for visual indicators (classes, attributes)
            class_list = await quiz_element.get_attribute("class") or ""
            if any(cls in class_list for cls in ["completed", "done", "passed"]):
                return TaskStatus.COMPLETED

            if any(cls in class_list for cls in ["in-progress", "started"]):
                return TaskStatus.IN_PROGRESS

            # Default to not started if no clear indicators
            return TaskStatus.NOT_STARTED

        except Exception as e:
            self.log(f"⚠️ Status detection failed: {e}")
            return TaskStatus.NOT_STARTED

    async def complete_quiz(self, quiz: QuizItem) -> bool:
        """Complete a single quiz"""
        try:
            self.log(f"🎯 Starting quiz: {quiz.title}")

            # Navigate to quiz if needed
            if quiz.url != self.browser.current_url:
                await self.browser.navigate_to(quiz.url)

            # Click start button if available
            if quiz.start_button_selector:
                try:
                    await self.browser.page.click(quiz.start_button_selector)
                    await self.browser.page.wait_for_load_state('networkidle')
                except Exception as e:
                    self.log(f"⚠️ Could not click start button: {e}")

            # Process questions in a loop
            question_count = 0
            max_questions = 50  # Safety limit

            while question_count < max_questions:
                # Check if quiz is finished
                if await self._is_quiz_finished():
                    self.log(f"✅ Quiz completed: {quiz.title}")
                    return True

                # Get current question
                question = await self._get_current_question()
                if not question:
                    self.log("⚠️ No question found, quiz may be complete")
                    break

                self.log(f"❓ Processing question {question_count + 1}: {question.text[:50]}...")

                # Solve the question
                answer = await self.ai_solver.solve_question(question)

                # Submit the answer
                success = await self._submit_answer(answer, question)
                if not success:
                    self.log(f"❌ Failed to submit answer for question {question_count + 1}")
                    return False

                question_count += 1

                # Small delay between questions
                await asyncio.sleep(1)

            self.log(f"✅ Completed quiz: {quiz.title} ({question_count} questions)")
            return True

        except Exception as e:
            self.log(f"❌ Quiz completion failed: {e}")
            return False

    async def _is_quiz_finished(self) -> bool:
        """Check if quiz is finished"""
        try:
            # Look for completion indicators
            completion_selectors = [
                ".quiz-complete", ".assessment-complete", ".finished",
                "[data-testid*='complete']", ".success-message",
                "text='Quiz Complete'", "text='Assessment Complete'"
            ]

            for selector in completion_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(selector, timeout=1000)
                    if element:
                        return True
                except:
                    continue

            # Check URL for completion indicators
            current_url = self.browser.page.url
            if any(indicator in current_url for indicator in ["complete", "finished", "results"]):
                return True

            return False

        except Exception as e:
            return False

    async def _get_current_question(self) -> Optional[Question]:
        """Extract current question from the page"""
        try:
            # Common question selectors
            question_selectors = [
                ".question", ".quiz-question", ".assessment-question",
                "[data-testid*='question']", ".question-text", "h1, h2, h3"
            ]

            question_text = ""
            question_element = None

            for selector in question_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(selector, timeout=2000)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 10:  # Reasonable question length
                            question_text = text.strip()
                            question_element = element
                            break
                except:
                    continue

            if not question_text:
                return None

            # Classify question type
            question_type = self.ai_solver.classify_question(question_text)

            # Extract options for multiple choice
            options = []
            if question_type == QuestionType.MULTIPLE_CHOICE:
                options = await self._extract_multiple_choice_options()

            # Get page context
            page_title = await self.browser.page.title()

            return Question(
                text=question_text,
                question_type=question_type,
                options=options,
                context=f"Page: {page_title}",
                element_selector=question_selectors[0] if question_element else ""
            )

        except Exception as e:
            self.log(f"❌ Question extraction failed: {e}")
            return None

    async def _extract_multiple_choice_options(self) -> List[str]:
        """Extract multiple choice options from the page"""
        try:
            options = []

            # Common option selectors
            option_selectors = [
                ".option", ".choice", ".answer-option",
                "[data-testid*='option']", "input[type='radio'] + label",
                ".multiple-choice-option"
            ]

            for selector in option_selectors:
                try:
                    elements = await self.browser.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and text.strip():
                            options.append(text.strip())

                    if options:  # If we found options, use them
                        break
                except:
                    continue

            return options

        except Exception as e:
            self.log(f"❌ Option extraction failed: {e}")
            return []

    async def _submit_answer(self, answer: str, question: Question) -> bool:
        """Submit answer to current question"""
        try:
            # For multiple choice, try to click the matching option
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                return await self._submit_multiple_choice_answer(answer)

            # For text-based answers, find input field and type
            else:
                return await self._submit_text_answer(answer)

        except Exception as e:
            self.log(f"❌ Answer submission failed: {e}")
            return False

    async def _submit_multiple_choice_answer(self, answer: str) -> bool:
        """Submit multiple choice answer"""
        try:
            # Try to find and click the matching option
            option_selectors = [
                f"text='{answer}'",
                f"label:has-text('{answer}')",
                f"input[value='{answer}'] + label",
                f".option:has-text('{answer}')"
            ]

            for selector in option_selectors:
                try:
                    await self.browser.page.click(selector)
                    self.log(f"✅ Selected option: {answer}")

                    # Try to find and click submit/next button
                    await self._click_submit_button()
                    return True
                except:
                    continue

            self.log(f"❌ Could not find option: {answer}")
            return False

        except Exception as e:
            self.log(f"❌ Multiple choice submission failed: {e}")
            return False

    async def _submit_text_answer(self, answer: str) -> bool:
        """Submit text-based answer"""
        try:
            # Find text input or textarea
            input_selectors = [
                "textarea", "input[type='text']", ".answer-input",
                "[data-testid*='answer']", ".text-input"
            ]

            for selector in input_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(selector, timeout=2000)
                    if element:
                        await element.fill(answer)
                        self.log(f"✅ Entered answer: {answer[:50]}...")

                        # Try to submit
                        await self._click_submit_button()
                        return True
                except:
                    continue

            self.log("❌ Could not find answer input field")
            return False

        except Exception as e:
            self.log(f"❌ Text answer submission failed: {e}")
            return False

    async def _click_submit_button(self) -> bool:
        """Find and click submit/next button"""
        try:
            submit_selectors = [
                "button:has-text('Submit')", "button:has-text('Next')",
                "button:has-text('Continue')", ".submit-btn", ".next-btn",
                "[data-testid*='submit']", "[data-testid*='next']"
            ]

            for selector in submit_selectors:
                try:
                    await self.browser.page.click(selector)
                    await self.browser.page.wait_for_load_state('networkidle')
                    self.log("✅ Clicked submit button")
                    return True
                except:
                    continue

            # Try pressing Enter as fallback
            await self.browser.page.keyboard.press('Enter')
            self.log("✅ Pressed Enter to submit")
            return True

        except Exception as e:
            self.log(f"❌ Submit button click failed: {e}")
            return False

class UniversalWebAutomationAgent:
    """Main agent that orchestrates all components"""

    def __init__(self, api_key: str, provider: str = "anthropic"):
        self.browser_engine = SmartBrowserEngine()
        self.ai_solver = QuestionAnsweringAI(api_key, provider)
        self.task_executor = TaskExecutionEngine(self.browser_engine, self.ai_solver)
        self.execution_log = []

    def log(self, message: str):
        """Log agent activities"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        logger.info(log_entry)
        print(log_entry)  # Also print to console

    async def complete_turing_quizzes(self) -> str:
        """
        Main function: Log into turing.com with Google, find all quizzes,
        see which ones are done, complete all the rest
        """
        try:
            self.log("🚀 Starting Turing.com quiz automation...")

            # Step 1: Start browser
            if not await self.browser_engine.start_browser(headless=False):
                return "❌ Failed to start browser"

            # Step 2: Navigate to Turing.com
            self.log("🌐 Navigating to turing.com...")
            if not await self.browser_engine.navigate_to("https://turing.com"):
                return "❌ Failed to navigate to turing.com"

            # Step 3: Find and click Google sign-in
            self.log("🔐 Looking for Google sign-in...")
            google_login_selectors = [
                "button:has-text('Sign in with Google')",
                "button:has-text('Continue with Google')",
                "a:has-text('Google Login')",
                "[data-testid*='google']",
                ".google-signin-btn"
            ]

            google_clicked = False
            for selector in google_login_selectors:
                try:
                    await self.browser_engine.page.click(selector)
                    google_clicked = True
                    self.log("✅ Clicked Google sign-in button")
                    break
                except:
                    continue

            if not google_clicked:
                self.log("⚠️ Could not find Google sign-in button - may need manual login")
            else:
                # Handle Google OAuth
                if not await self.task_executor.handle_google_oauth():
                    self.log("⚠️ OAuth may need manual completion")

            # Step 4: Find quizzes section
            self.log("🔍 Looking for quizzes section...")
            quiz_nav_names = [
                "Skills", "Assessments", "Tests", "Quizzes",
                "Skill Tests", "Technical Assessment", "Challenges"
            ]

            quiz_section = await self.task_executor.find_navigation_item(quiz_nav_names)
            if quiz_section:
                await self.browser_engine.page.click(quiz_section)
                await self.browser_engine.page.wait_for_load_state('networkidle')
                self.log("✅ Navigated to quizzes section")
            else:
                self.log("⚠️ Could not find quizzes section - continuing with current page")

            # Step 5: Scan all available quizzes
            all_quizzes = await self.task_executor.get_all_quiz_items()
            self.log(f"📊 Found {len(all_quizzes)} total quizzes")

            # Step 6: Filter incomplete quizzes
            incomplete_quizzes = [
                quiz for quiz in all_quizzes
                if quiz.status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS, TaskStatus.RETAKE_AVAILABLE]
            ]

            self.log(f"🎯 Found {len(incomplete_quizzes)} incomplete quizzes to complete")

            if not incomplete_quizzes:
                return "✅ All quizzes are already completed!"

            # Step 7: Complete each incomplete quiz
            completed_count = 0
            for quiz in incomplete_quizzes:
                if await self.task_executor.complete_quiz(quiz):
                    completed_count += 1
                else:
                    self.log(f"❌ Failed to complete: {quiz.title}")

                # Small delay between quizzes
                await asyncio.sleep(2)

            # Final result
            result = f"✅ Successfully completed {completed_count} out of {len(incomplete_quizzes)} quizzes"
            self.log(result)
            return result

        except Exception as e:
            error_msg = f"❌ Automation failed: {e}"
            self.log(error_msg)
            return error_msg

        finally:
            # Cleanup
            await self.browser_engine.stop_browser()

    async def complete_tasks_on_any_site(self, site_url: str, task_description: str) -> str:
        """
        Universal website automation - works on ANY website with the same pattern
        """
        try:
            self.log(f"🚀 Starting universal automation on {site_url}")
            self.log(f"📋 Task: {task_description}")

            # Step 1: Start browser
            if not await self.browser_engine.start_browser(headless=False):
                return "❌ Failed to start browser"

            # Step 2: Navigate to site
            if not await self.browser_engine.navigate_to(site_url):
                return f"❌ Failed to navigate to {site_url}"

            # Step 3: Detect authentication method and login
            auth_method = await self._detect_authentication_method()
            if auth_method:
                self.log(f"🔐 Detected authentication: {auth_method}")
                await self._perform_login(auth_method)

            # Step 4: Find relevant content area based on task description
            content_area = await self._find_relevant_section(task_description)
            if content_area:
                await self.browser_engine.page.click(content_area)
                await self.browser_engine.page.wait_for_load_state('networkidle')

            # Step 5: Analyze available tasks
            tasks = await self._analyze_available_tasks(task_description)
            incomplete_tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]

            self.log(f"📊 Found {len(incomplete_tasks)} tasks to complete")

            # Step 6: Complete tasks
            completed_count = 0
            for task in incomplete_tasks:
                if await self.task_executor.complete_quiz(task):  # Reuse quiz completion logic
                    completed_count += 1
                await asyncio.sleep(1)

            result = f"✅ Completed {completed_count} out of {len(incomplete_tasks)} tasks on {site_url}"
            self.log(result)
            return result

        except Exception as e:
            error_msg = f"❌ Universal automation failed: {e}"
            self.log(error_msg)
            return error_msg

        finally:
            await self.browser_engine.stop_browser()

    async def _detect_authentication_method(self) -> Optional[str]:
        """Detect what authentication method the site uses"""
        try:
            # Look for common login indicators
            login_indicators = [
                ("google", ["Sign in with Google", "Google Login", "Continue with Google"]),
                ("facebook", ["Sign in with Facebook", "Facebook Login"]),
                ("github", ["Sign in with GitHub", "GitHub Login"]),
                ("username", ["Username", "Email", "Login", "Sign In"])
            ]

            for method, texts in login_indicators:
                for text in texts:
                    try:
                        element = await self.browser_engine.page.wait_for_selector(f"text='{text}'", timeout=2000)
                        if element:
                            return method
                    except:
                        continue

            return None

        except Exception as e:
            self.log(f"❌ Auth detection failed: {e}")
            return None

    async def _perform_login(self, auth_method: str) -> bool:
        """Perform login based on detected method"""
        try:
            if auth_method == "google":
                # Click Google login and handle OAuth
                google_selectors = [
                    "button:has-text('Sign in with Google')",
                    "a:has-text('Google Login')",
                    "[data-provider='google']"
                ]

                for selector in google_selectors:
                    try:
                        await self.browser_engine.page.click(selector)
                        return await self.task_executor.handle_google_oauth()
                    except:
                        continue

            # Add other auth methods as needed
            self.log(f"⚠️ Authentication method {auth_method} not fully implemented")
            return False

        except Exception as e:
            self.log(f"❌ Login failed: {e}")
            return False

    async def _find_relevant_section(self, task_description: str) -> Optional[str]:
        """Find relevant content section based on task description"""
        try:
            # Extract keywords from task description
            keywords = task_description.lower().split()

            # Common section mappings
            section_mappings = {
                "quiz": ["Skills", "Assessments", "Tests", "Quizzes"],
                "test": ["Skills", "Assessments", "Tests", "Quizzes"],
                "course": ["Courses", "Learning", "Training"],
                "job": ["Jobs", "Opportunities", "Positions"],
                "profile": ["Profile", "Account", "Settings"]
            }

            # Find matching sections
            for keyword in keywords:
                if keyword in section_mappings:
                    section_names = section_mappings[keyword]
                    section = await self.task_executor.find_navigation_item(section_names)
                    if section:
                        return section

            return None

        except Exception as e:
            self.log(f"❌ Section finding failed: {e}")
            return None

    async def _analyze_available_tasks(self, task_description: str) -> List[QuizItem]:
        """Analyze and identify available tasks on the page"""
        try:
            # Reuse quiz scanning logic for general tasks
            return await self.task_executor.get_all_quiz_items()

        except Exception as e:
            self.log(f"❌ Task analysis failed: {e}")
            return []

    def get_execution_log(self) -> List[str]:
        """Get execution log for debugging"""
        return self.execution_log.copy()

# CLI Interface and Main Functions
async def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Universal Web Automation Agent")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--api-key", help="API key for AI provider")
    parser.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "google"], help="AI provider")
    parser.add_argument("--site", help="Website URL for universal automation")

    args = parser.parse_args()

    # Get API key from environment if not provided
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ No API key provided. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY environment variable")
        return

    # Create agent
    agent = UniversalWebAutomationAgent(api_key, args.provider)

    try:
        if args.command.lower() == "turing-quizzes":
            # Specific Turing.com automation
            result = await agent.complete_turing_quizzes()
            print(f"\n🎯 Final Result: {result}")

        elif args.site:
            # Universal website automation
            result = await agent.complete_tasks_on_any_site(args.site, args.command)
            print(f"\n🎯 Final Result: {result}")

        else:
            print("❌ Please provide either 'turing-quizzes' command or --site URL with task description")

    except KeyboardInterrupt:
        print("\n⚠️ Automation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    # Print execution log
    print("\n📋 Execution Log:")
    for log_entry in agent.get_execution_log():
        print(log_entry)

if __name__ == "__main__":
    print("🚀 Simple Universal Web Automation Agent")
    print("=" * 50)
    print("Examples:")
    print("  python remote_agent.py turing-quizzes")
    print("  python remote_agent.py 'complete all courses' --site https://coursera.org")
    print("  python remote_agent.py 'apply to jobs' --site https://linkedin.com")
    print("=" * 50)
    print()

    asyncio.run(main())
