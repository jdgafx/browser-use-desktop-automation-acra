#!/usr/bin/env python3
"""
Natural Language Processor for Playwright Automation
Converts natural language prompts into automation actions
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    FILL_FORM = "fill_form"
    LOGIN = "login"
    SEARCH = "search"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    CUSTOM = "custom"

@dataclass
class AutomationAction:
    action_type: ActionType
    target: Optional[str] = None
    value: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class NaturalLanguageProcessor:
    """Processes natural language commands and converts them to automation actions"""
    
    def __init__(self):
        self.action_patterns = self._initialize_patterns()
        self.context_keywords = self._initialize_context_keywords()
    
    def _initialize_patterns(self) -> Dict[ActionType, List[str]]:
        """Initialize regex patterns for different action types"""
        return {
            ActionType.NAVIGATE: [
                r"(?:go to|navigate to|visit|open)\s+(.+)",
                r"(?:load|browse to)\s+(.+)",
                r"(?:take me to|show me)\s+(.+)"
            ],
            ActionType.CLICK: [
                r"(?:click|press|tap)\s+(?:on\s+)?(.+)",
                r"(?:select|choose)\s+(.+)",
                r"(?:hit|activate)\s+(.+)"
            ],
            ActionType.TYPE: [
                r"(?:type|enter|input)\s+[\"'](.+?)[\"']\s+(?:in|into|on)\s+(.+)",
                r"(?:write|fill)\s+(.+?)\s+(?:in|into)\s+(.+)",
                r"(?:put|insert)\s+[\"'](.+?)[\"']\s+(?:in|into)\s+(.+)"
            ],
            ActionType.SCROLL: [
                r"(?:scroll|move)\s+(down|up|to\s+.+)",
                r"(?:page\s+down|page\s+up)",
                r"(?:go\s+to\s+top|go\s+to\s+bottom)"
            ],
            ActionType.WAIT: [
                r"(?:wait|pause)\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?|s)?",
                r"(?:delay|hold)\s+(\d+)",
                r"(?:wait for|wait until)\s+(.+)"
            ],
            ActionType.SCREENSHOT: [
                r"(?:take|capture|grab)\s+(?:a\s+)?(?:screenshot|picture|image)",
                r"(?:save|export)\s+(?:screenshot|image)",
                r"(?:show me|let me see)\s+(?:the\s+)?(?:page|screen)"
            ],
            ActionType.EXTRACT: [
                r"(?:get|extract|find|grab)\s+(?:the\s+)?(.+)",
                r"(?:copy|save)\s+(?:the\s+)?(.+)",
                r"(?:what is|show me)\s+(?:the\s+)?(.+)"
            ],
            ActionType.FILL_FORM: [
                r"(?:fill|complete)\s+(?:the\s+)?(?:form|fields)",
                r"(?:submit|send)\s+(?:the\s+)?form",
                r"(?:enter|input)\s+(?:my\s+)?(?:details|information)"
            ],
            ActionType.LOGIN: [
                r"(?:log in|login|sign in)(?:\s+to\s+(.+))?",
                r"(?:authenticate|access)\s+(.+)",
                r"(?:enter|use)\s+(?:my\s+)?(?:credentials|login)"
            ],
            ActionType.SEARCH: [
                r"(?:search|look)\s+(?:for\s+)?[\"'](.+?)[\"']",
                r"(?:find|locate)\s+(.+)",
                r"(?:query|lookup)\s+(.+)"
            ],
            ActionType.DOWNLOAD: [
                r"(?:download|save|get)\s+(.+)",
                r"(?:fetch|retrieve)\s+(.+)",
                r"(?:export|backup)\s+(.+)"
            ],
            ActionType.UPLOAD: [
                r"(?:upload|attach|add)\s+(?:file\s+)?(.+)",
                r"(?:select|choose)\s+(?:file\s+)?(.+)\s+(?:to upload|for upload)",
                r"(?:browse|pick)\s+(?:a\s+)?file"
            ],
            ActionType.CUSTOM: [
                r"(?:complete|finish|do)\s+(.+?)\s+(?:with\s+)?(\d+%|\d+\s*percent|100%|all)?",
                r"(?:take|attempt)\s+(.+?)\s+(?:and\s+)?(?:pass|score)\s+(\d+%|\d+\s*percent|100%)",
                r"(?:we\s+need\s+to\s+)?(?:accomplish|achieve)\s+(.+)"
            ]
        }
    
    def _initialize_context_keywords(self) -> Dict[str, List[str]]:
        """Initialize context keywords for better understanding"""
        return {
            'elements': [
                'button', 'link', 'field', 'input', 'textbox', 'dropdown', 'menu',
                'checkbox', 'radio', 'tab', 'header', 'footer', 'sidebar', 'form',
                'table', 'row', 'column', 'cell', 'image', 'video', 'text', 'title'
            ],
            'locations': [
                'top', 'bottom', 'left', 'right', 'center', 'middle', 'corner',
                'header', 'footer', 'sidebar', 'main', 'content', 'navigation'
            ],
            'actions': [
                'submit', 'cancel', 'save', 'delete', 'edit', 'create', 'update',
                'refresh', 'reload', 'back', 'forward', 'home', 'logout', 'settings'
            ],
            'modifiers': [
                'first', 'last', 'next', 'previous', 'all', 'any', 'main', 'primary',
                'secondary', 'visible', 'hidden', 'enabled', 'disabled', 'selected'
            ]
        }
    
    def process_command(self, command: str) -> List[AutomationAction]:
        """
        Enhanced natural language command processing for complex workflows
        Handles sophisticated multi-step automation tasks
        """
        command = command.lower().strip()
        actions = []

        # Enhanced compound command splitting with better context awareness
        sub_commands = self._split_compound_command_enhanced(command)

        # Process each command with context from previous actions
        for i, sub_command in enumerate(sub_commands):
            sub_command = sub_command.strip()
            if not sub_command:
                continue

            # Parse with context awareness
            action = self._parse_single_command_enhanced(sub_command, actions)
            if action:
                actions.append(action)
            else:
                # Try advanced inference for complex phrases
                inferred_action = self._infer_complex_action(sub_command, actions)
                if inferred_action:
                    actions.append(inferred_action)

        return actions
    
    def _split_compound_command_enhanced(self, command: str) -> List[str]:
        """Enhanced compound command splitting with better context awareness"""
        # More sophisticated separators that preserve context
        separators = [
            r'\s+and\s+then\s+',
            r'\s+then\s+',
            r'\s*,\s*then\s+',
            r'\s*,\s*and\s+then\s+',
            r'\s*,\s*and\s+',
            r'\s*;\s*',
            r'\s+after\s+that\s+',
            r'\s+next\s+',
            r'\s+afterwards\s+',
            r'\s*,\s*(?=(?:find|see|take|click|go|navigate|login|search|fill|submit|wait|scroll))',
            r'\s+and\s+(?=(?:find|see|take|click|go|navigate|login|search|fill|submit|wait|scroll))'
        ]

        commands = [command]
        for separator in separators:
            new_commands = []
            for cmd in commands:
                split_parts = re.split(separator, cmd)
                new_commands.extend(split_parts)
            commands = new_commands

        # Clean and filter parts
        cleaned_commands = []
        for cmd in commands:
            cmd = cmd.strip()
            if cmd and len(cmd) > 2:  # Ignore very short fragments
                cleaned_commands.append(cmd)

        return cleaned_commands

    def _split_compound_command(self, command: str) -> List[str]:
        """Legacy method - calls enhanced version"""
        return self._split_compound_command_enhanced(command)
    
    def _parse_single_command_enhanced(self, command: str, previous_actions: List[AutomationAction]) -> Optional[AutomationAction]:
        """Enhanced single command parsing with context awareness"""
        # First try standard parsing
        action = self._parse_single_command(command)
        if action:
            return action

        # Try advanced pattern matching for complex phrases
        return self._parse_complex_phrases(command, previous_actions)

    def _parse_complex_phrases(self, command: str, previous_actions: List[AutomationAction]) -> Optional[AutomationAction]:
        """Parse complex phrases that don't match simple patterns"""

        # Handle authentication/login patterns
        auth_patterns = [
            r"login\s+with\s+(.+?)\s+to\s+(?:the\s+)?(.+)",
            r"sign\s+in\s+(?:with\s+)?(.+?)\s+(?:to\s+)?(?:the\s+)?(.+)",
            r"authenticate\s+(?:with\s+)?(.+?)\s+(?:for\s+)?(.+)"
        ]

        for pattern in auth_patterns:
            match = re.search(pattern, command)
            if match:
                method = match.group(1).strip()
                target = match.group(2).strip() if len(match.groups()) > 1 else ""
                return AutomationAction(
                    ActionType.LOGIN,
                    target=f"{method} login",
                    value=target,
                    description=f"Login with {method} to {target}"
                )

        # Handle finding/searching patterns
        find_patterns = [
            r"find\s+(?:my\s+)?(.+?)(?:\s*,|\s+and|\s*$)",
            r"look\s+for\s+(?:my\s+)?(.+?)(?:\s*,|\s+and|\s*$)",
            r"locate\s+(?:my\s+)?(.+?)(?:\s*,|\s+and|\s*$)",
            r"see\s+(?:what\s+)?(?:i\s+)?(.+?)(?:\s*,|\s+and|\s*$)"
        ]

        for pattern in find_patterns:
            match = re.search(pattern, command)
            if match:
                target = match.group(1).strip()
                return AutomationAction(
                    ActionType.SEARCH,
                    target=target,
                    description=f"Find {target}"
                )

        # Handle completion/achievement patterns
        completion_patterns = [
            r"(?:take|complete|do|finish)\s+(?:the\s+)?(.+?)\s+(?:and\s+)?(?:pass\s+them\s+)?(\d+%|\d+\s*percent|100%|all)?",
            r"(?:pass|complete)\s+(.+?)\s+(?:at\s+)?(\d+%|\d+\s*percent|100%)?",
            r"(?:we\s+need\s+to\s+)?(?:take|do|complete)\s+(.+?)\s+(?:all\s+)?(?:please)?"
        ]

        for pattern in completion_patterns:
            match = re.search(pattern, command)
            if match:
                target = match.group(1).strip()
                score = match.group(2) if len(match.groups()) > 1 and match.group(2) else "100%"
                return AutomationAction(
                    ActionType.CUSTOM,
                    target=target,
                    value=score,
                    description=f"Complete {target} with {score} score"
                )

        return None

    def _infer_complex_action(self, command: str, previous_actions: List[AutomationAction]) -> Optional[AutomationAction]:
        """Infer actions from complex natural language using context"""

        # If previous action was navigation, this might be an interaction
        if previous_actions and previous_actions[-1].action_type == ActionType.NAVIGATE:

            # Look for interaction keywords
            interaction_keywords = [
                "quizzes", "tests", "assessments", "exams", "assignments",
                "account", "profile", "dashboard", "settings",
                "results", "scores", "grades", "progress"
            ]

            for keyword in interaction_keywords:
                if keyword in command:
                    return AutomationAction(
                        ActionType.CLICK,
                        target=keyword,
                        description=f"Click on {keyword}"
                    )

        # Handle implicit actions based on keywords
        if any(word in command for word in ["my", "i", "me"]):
            if any(word in command for word in ["passed", "completed", "finished"]):
                return AutomationAction(
                    ActionType.SEARCH,
                    target="completed items",
                    description="Find completed items"
                )

        # Default to search if we can't determine the action
        if len(command) > 5:  # Avoid very short commands
            return AutomationAction(
                ActionType.SEARCH,
                target=command,
                description=f"Search for: {command}"
            )

        return None

    def _parse_single_command(self, command: str) -> Optional[AutomationAction]:
        """Parse a single command into an automation action"""
        # Try to match against each action type
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    return self._create_action(action_type, match, command)
        
        # If no specific pattern matches, try to infer from keywords
        return self._infer_action_from_keywords(command)
    
    def _create_action(self, action_type: ActionType, match: re.Match, command: str) -> AutomationAction:
        """Create an automation action from a regex match"""
        groups = match.groups()
        
        if action_type == ActionType.NAVIGATE:
            url = groups[0].strip()
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if '.' in url and not url.startswith('www.'):
                    url = 'https://' + url
                elif not url.startswith('www.'):
                    url = 'https://www.' + url
            return AutomationAction(
                action_type=action_type,
                target=url,
                description=f"Navigate to {url}"
            )
        
        elif action_type == ActionType.CLICK:
            target = groups[0].strip()
            return AutomationAction(
                action_type=action_type,
                target=target,
                description=f"Click on {target}"
            )
        
        elif action_type == ActionType.TYPE:
            if len(groups) >= 2:
                value = groups[0].strip()
                target = groups[1].strip()
            else:
                # Handle single group case
                parts = groups[0].split(' in ')
                if len(parts) >= 2:
                    value = parts[0].strip()
                    target = ' '.join(parts[1:]).strip()
                else:
                    value = groups[0].strip()
                    target = "input field"
            
            return AutomationAction(
                action_type=action_type,
                target=target,
                value=value,
                description=f"Type '{value}' in {target}"
            )
        
        elif action_type == ActionType.WAIT:
            if groups[0].isdigit():
                seconds = int(groups[0])
                return AutomationAction(
                    action_type=action_type,
                    value=str(seconds),
                    description=f"Wait for {seconds} seconds"
                )
            else:
                condition = groups[0].strip()
                return AutomationAction(
                    action_type=action_type,
                    target=condition,
                    description=f"Wait for {condition}"
                )
        
        elif action_type == ActionType.SEARCH:
            query = groups[0].strip()
            return AutomationAction(
                action_type=action_type,
                value=query,
                description=f"Search for '{query}'"
            )
        
        elif action_type == ActionType.LOGIN:
            site = "current site"
            if groups and len(groups) > 0 and groups[0]:
                site = groups[0].strip()
            return AutomationAction(
                action_type=action_type,
                target=site,
                description=f"Login to {site}"
            )

        elif action_type == ActionType.CUSTOM:
            task = groups[0].strip() if groups and groups[0] else "task"
            score = groups[1].strip() if groups and len(groups) > 1 and groups[1] else "100%"
            return AutomationAction(
                action_type=action_type,
                target=task,
                value=score,
                description=f"Complete {task} with {score} score"
            )

        else:
            # Generic action
            target = groups[0].strip() if groups and groups[0] else None
            return AutomationAction(
                action_type=action_type,
                target=target,
                description=command
            )
    
    def _infer_action_from_keywords(self, command: str) -> Optional[AutomationAction]:
        """Infer action type from keywords when no pattern matches"""
        words = command.lower().split()
        
        # Check for URL patterns
        if any(word.startswith(('http://', 'https://')) or '.' in word for word in words):
            return AutomationAction(
                action_type=ActionType.NAVIGATE,
                target=command,
                description=f"Navigate to {command}"
            )
        
        # Check for common action keywords
        if any(word in ['click', 'press', 'tap', 'select'] for word in words):
            target = ' '.join(words[1:]) if len(words) > 1 else "element"
            return AutomationAction(
                action_type=ActionType.CLICK,
                target=target,
                description=f"Click on {target}"
            )
        
        # Default to extraction if asking for information
        if any(word in ['what', 'show', 'get', 'find', 'tell'] for word in words):
            return AutomationAction(
                action_type=ActionType.EXTRACT,
                target=command,
                description=f"Extract information: {command}"
            )
        
        return None
    
    def get_action_suggestions(self, partial_command: str) -> List[str]:
        """Get suggestions for completing a partial command"""
        suggestions = []
        partial = partial_command.lower().strip()
        
        # Common command starters
        starters = [
            "go to", "click on", "type", "search for", "login to",
            "take screenshot", "scroll down", "wait for", "fill form",
            "download", "upload file", "extract", "find"
        ]
        
        for starter in starters:
            if starter.startswith(partial) or partial in starter:
                suggestions.append(starter)
        
        return suggestions[:10]  # Limit to 10 suggestions
