import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def _clean_contact_value(value):
    """Return a readable value for the prompt, even when a field is empty."""
    if value is None or str(value).strip() == "":
        return "Not provided"
    return str(value).strip()


def _get_openai_client():
    """Create an OpenAI client or raise a helpful error if the key is missing."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your local .env file before using AI features."
        )

    return OpenAI(api_key=api_key)


def _build_contact_context(contact):
    """Return formatted contact context for prompts."""
    if not contact:
        return "No contact context provided."

    contact_details = {
        "name": _clean_contact_value(contact.get("name")),
        "company": _clean_contact_value(contact.get("company")),
        "role": _clean_contact_value(contact.get("role")),
        "linkedin_url": _clean_contact_value(contact.get("linkedin_url")),
        "source_event": _clean_contact_value(contact.get("source_event")),
        "notes": _clean_contact_value(contact.get("notes")),
        "status": _clean_contact_value(contact.get("status")),
    }

    return f"""
- Name: {contact_details["name"]}
- Company: {contact_details["company"]}
- Role: {contact_details["role"]}
- LinkedIn URL: {contact_details["linkedin_url"]}
- Source/Event: {contact_details["source_event"]}
- Notes: {contact_details["notes"]}
- Status: {contact_details["status"]}
"""


def _safe_score(value):
    """Convert a score to an integer between 1 and 10."""
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 1

    return max(1, min(score, 10))


def generate_outreach_message(contact, message_type, tone, goal):
    """Generate a short personalized outreach message for one saved contact."""
    client = _get_openai_client()

    prompt = f"""
Write one practical, personalized networking outreach message.

Contact details:
{_build_contact_context(contact)}

Message type: {message_type}
Tone: {tone}
Goal: {goal}

Guidelines:
- Keep it short enough for real networking.
- Be specific when useful details are available.
- Do not invent facts that are not in the contact details.
- Do not mention that you are an AI.
- Return only the finished message.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "You write concise, useful networking outreach messages.",
                },
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=220,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

    message = response.output_text.strip()

    if not message:
        raise RuntimeError("OpenAI returned an empty message. Please try again.")

    return message


def score_outreach_message(message, contact=None):
    """Score an outreach message and return structured feedback for the app."""
    if not message or not message.strip():
        raise ValueError("Paste or write a message before scoring.")

    client = _get_openai_client()

    prompt = f"""
Evaluate this networking outreach message.

Message:
{message.strip()}

Contact context:
{_build_contact_context(contact)}

Return only valid JSON using this exact structure:
{{
  "category_scores": {{
    "Personalization": 1,
    "Clarity": 1,
    "Professionalism": 1,
    "Length": 1,
    "Strength of the ask": 1
  }},
  "overall_score": 1,
  "explanation": "Short explanation of the score.",
  "improvement_suggestions": [
    "Specific suggestion 1",
    "Specific suggestion 2",
    "Specific suggestion 3"
  ]
}}

Scoring rules:
- Use whole numbers from 1 to 10.
- Score personalization based on how well the message uses the contact context.
- Score length based on whether it is short enough for practical networking.
- Give exactly 3 specific improvement suggestions.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "You are a concise outreach coach. Return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=500,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

    raw_feedback = response.output_text.strip()

    if raw_feedback.startswith("```"):
        lines = raw_feedback.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_feedback = "\n".join(lines).strip()

    try:
        feedback = json.loads(raw_feedback)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI returned feedback in an unexpected format. Please try again.") from exc

    required_categories = [
        "Personalization",
        "Clarity",
        "Professionalism",
        "Length",
        "Strength of the ask",
    ]

    raw_category_scores = feedback.get("category_scores", {})
    category_scores = {}
    for category in required_categories:
        category_scores[category] = _safe_score(raw_category_scores.get(category, 1))

    suggestions = feedback.get("improvement_suggestions", [])

    return {
        "category_scores": category_scores,
        "overall_score": _safe_score(feedback.get("overall_score", 1)),
        "explanation": str(feedback.get("explanation", "")).strip(),
        "improvement_suggestions": [str(suggestion).strip() for suggestion in suggestions[:3]],
    }
