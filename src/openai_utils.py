import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def _clean_contact_value(value):
    """Return a readable value for the prompt, even when a field is empty."""
    if value is None or str(value).strip() == "":
        return "Not provided"
    return str(value).strip()


def generate_outreach_message(contact, message_type, tone, goal):
    """Generate a short personalized outreach message for one saved contact."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your local .env file before generating messages."
        )

    client = OpenAI(api_key=api_key)

    contact_details = {
        "name": _clean_contact_value(contact.get("name")),
        "company": _clean_contact_value(contact.get("company")),
        "role": _clean_contact_value(contact.get("role")),
        "linkedin_url": _clean_contact_value(contact.get("linkedin_url")),
        "source_event": _clean_contact_value(contact.get("source_event")),
        "notes": _clean_contact_value(contact.get("notes")),
        "status": _clean_contact_value(contact.get("status")),
    }

    prompt = f"""
Write one practical, personalized networking outreach message.

Contact details:
- Name: {contact_details["name"]}
- Company: {contact_details["company"]}
- Role: {contact_details["role"]}
- LinkedIn URL: {contact_details["linkedin_url"]}
- Source/Event: {contact_details["source_event"]}
- Notes: {contact_details["notes"]}
- Status: {contact_details["status"]}

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
