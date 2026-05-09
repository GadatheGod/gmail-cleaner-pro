"""
Email Preview Service
---------------------
Fetch and decode email content for preview before deletion.
"""

import base64
import logging
import re
from typing import Optional

from app.core import state
from app.services.auth import get_gmail_service

logger = logging.getLogger(__name__)


def preview_emails_background(sender: str, limit: int = 10):
    """Preview emails from a specific sender."""
    state.preview_status["message"] = f"Fetching emails from {sender}..."
    state.preview_status["loading"] = True

    service, error = get_gmail_service()
    if error:
        state.preview_status["error"] = error
        state.preview_status["loading"] = False
        return

    try:
        query = f"from:{sender}"
        results = service.users().messages().list(
            userId="me", q=query, maxResults=limit
        ).execute()

        messages = results.get("messages", [])
        previews = []

        for msg_data in messages:
            msg = service.users().messages().get(
                userId="me", id=msg_data["id"], format="full"
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])
            subject = ""
            date_str = ""
            from_addr = ""

            for h in headers:
                if h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "Date":
                    date_str = h["value"]
                elif h["name"] == "From":
                    from_addr = h["value"]

            body = _extract_body(msg)

            previews.append({
                "id": msg_data["id"],
                "subject": subject,
                "date": date_str,
                "from": from_addr,
                "body": body[:2000],
            })

            state.preview_status["message"] = f"Loaded {len(previews)}/{limit} emails"

        state.preview_results = previews
        state.preview_status["done"] = True
        state.preview_status["loading"] = False
        state.preview_status["message"] = f"Previewing {len(previews)} emails"

    except Exception as e:
        state.preview_status["error"] = str(e)
        state.preview_status["loading"] = False


def get_preview_status() -> dict:
    """Get preview operation status."""
    return state.preview_status.copy()


def get_preview_results() -> list:
    """Get preview results."""
    return state.preview_results.copy()


def _extract_body(message: dict) -> str:
    """Extract text body from a Gmail message."""
    payload = message.get("payload", {})

    def _decode(data: str) -> str:
        if not data:
            return ""
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""

    def _extract_from_part(part: dict) -> str:
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {})
        data = body_data.get("data", "")

        if mime_type == "text/plain" and data:
            return _decode(data)
        elif mime_type == "text/html" and data:
            text = _decode(data)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        elif mime_type.startswith("multipart"):
            for sub_part in part.get("parts", []):
                result = _extract_from_part(sub_part)
                if result:
                    return result

        return ""

    return _extract_from_part(payload)
