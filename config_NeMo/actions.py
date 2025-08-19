"""
Custom actions for NeMo Guardrails
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def init(app):
    """Initialize the actions."""
    app.register_action("check_jailbreak_patterns", check_jailbreak_patterns)
    app.register_action("check_sensitive_output", check_sensitive_output)
    app.register_action("log_blocked_attempt", log_blocked_attempt)


async def check_jailbreak_patterns(context: dict) -> str:
    """
    Check if the user input contains jailbreak patterns.
    Returns 'Yes' if jailbreak detected, 'No' otherwise.
    """
    user_input = context.get("user_input", "").lower()

    jailbreak_patterns = [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?",
        r"disregard\s+(?:all\s+)?(?:previous\s+)?instructions?",
        r"forget\s+(?:your\s+)?instructions?",
        r"you\s+are\s+now\s+(?:a|an)?\s*\w+",
        r"act\s+as\s+(?:a|an)?\s*\w+",
        r"pretend\s+(?:to\s+be|you\s+are)",
        r"dan\s+mode",
        r"developer\s+mode",
        r"show\s+(?:me\s+)?(?:your\s+)?(?:system\s+)?prompt",
        r"what\s+(?:is|are)\s+(?:your\s+)?instructions",
        r"reveal\s+(?:your\s+)?(?:secrets?|prompt)",
    ]

    for pattern in jailbreak_patterns:
        if re.search(pattern, user_input):
            logger.warning(f"Jailbreak pattern detected: {pattern}")
            return "Yes"

    return "No"


async def check_sensitive_output(context: dict) -> str:
    """
    Check if the bot output contains sensitive information.
    Returns 'Yes' if sensitive data detected, 'No' otherwise.
    """
    bot_response = context.get("bot_response", "")

    sensitive_patterns = [
        r"admin123!",
        r"sk-[a-zA-Z0-9-]+",
        r"\d{3}-\d{2}-\d{4}",  # SSN pattern
        r"mysql://[^@\s]+@[^\/\s]+",
        r"RED-ALERT-\d+",
        r"dbpass2024",
        r"int-svc-[a-zA-Z0-9-]+",
        r"ssh-rsa\s+[A-Za-z0-9+\/=]+",
        r"CUST-\d{6}",
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, bot_response, re.IGNORECASE):
            logger.warning(f"Sensitive data detected in output: {pattern}")
            return "Yes"

    return "No"


async def log_blocked_attempt(context: dict) -> str:
    """
    Log when an attempt is blocked by guardrails.
    """
    user_input = context.get("user_input", "")
    reason = context.get("reason", "policy_violation")

    logger.info(f"Blocked attempt - Reason: {reason}, Input: {user_input[:100]}...")

    return "logged"