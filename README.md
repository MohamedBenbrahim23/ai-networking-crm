# AI Networking CRM

AI Networking CRM is a lightweight Streamlit app that helps students and early-career professionals manage networking contacts, generate personalized outreach messages, evaluate message quality, and track follow-ups.

I built this project because networking can get messy quickly. When attending conferences, reaching out on LinkedIn, talking to recruiters, or following up with alumni, it is easy to lose track of who you contacted, what you said, and when you should follow up. This app brings those steps into one simple workflow.

## What the app does

The app allows users to:

* Add and manage networking contacts
* Store details such as name, company, role, LinkedIn URL, event/source, notes, and status
* Generate personalized outreach messages using the OpenAI API
* Score message quality across categories such as personalization, clarity, professionalism, length, and strength of the ask
* Save generated or manually written messages
* Track follow-up dates, notes, and contact status
* View simple dashboard metrics for networking progress

## Why I built it

This project was designed around a real problem: managing professional networking as a student.

Instead of building a general chatbot, I wanted to create a small AI workflow tool that supports an actual recruiting process. The goal was to make something practical enough to use for LinkedIn outreach, conferences, recruiter conversations, alumni networking, and informational interviews.

The project also gave me a chance to practice combining:

* A simple database-backed application
* AI-assisted text generation
* Prompt design
* User workflow design
* Streamlit UI development
* Local environment and API key management

## Tech stack

* Python
* Streamlit
* SQLite
* Pandas
* OpenAI API
* python-dotenv

## Main features

### Contact management

Users can add contacts with details such as company, role, LinkedIn profile, notes, and source/event. Contacts are stored in a local SQLite database.

### AI outreach generator

The app can generate personalized networking messages based on the selected contact. Users can choose the message type, tone, and goal.

Example message types include:

* LinkedIn connection request
* LinkedIn follow-up
* Email outreach
* Conference follow-up
* Recruiter message

### Message quality scoring

The app evaluates outreach messages across several dimensions:

* Personalization
* Clarity
* Professionalism
* Length
* Strength of the ask

The scorer helps users improve their messages instead of just accepting the first AI-generated draft.

### Saved messages

Generated or manually written messages can be saved and linked to a specific contact. This makes it easier to remember what was sent or prepared for each person.

### Follow-up tracking

Users can update follow-up dates, notes, and contact statuses so they know who needs attention next.

### Dashboard

The dashboard gives a quick overview of networking activity, including contacts, replies, meetings, saved messages, and follow-ups.

## Project structure

```text
ai-networking-crm/
├── app.py
├── src/
│   ├── database.py
│   └── openai_utils.py
├── data/
│   └── networking_crm.db
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## File overview

### `app.py`

Main Streamlit application. It controls the user interface, page layout, dashboard, contact forms, AI message generation, scoring, saved messages, and follow-up tracking.

### `src/database.py`

Handles all SQLite database operations, including contact storage, saved messages, follow-up tracking, and safe database initialization.

### `src/openai_utils.py`

Contains the OpenAI API functions used for outreach message generation and message quality scoring.

### `data/`

Stores the local SQLite database. The database file is ignored by Git so personal contact/message data is not pushed to GitHub.

### `.env.example`

Shows the environment variable needed to run the AI features locally.

## Setup instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ai-networking-crm.git
cd ai-networking-crm
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\activate
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up the API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not commit this file to GitHub.

### 6. Run the app

```bash
streamlit run app.py
```

If you want to force Streamlit to use the project virtual environment on Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Streamlit Cloud deployment notes

For Streamlit Cloud, add the API key through the app settings/secrets instead of uploading a `.env` file.

Example secret:

```toml
OPENAI_API_KEY = "your_api_key_here"
```

The app is designed to run with local SQLite storage for Version 1. For a larger production version, the database could be moved to PostgreSQL or another hosted database.

## What I learned

Building this project helped me practice more than just calling an AI API. The main challenge was designing a workflow that feels useful from start to finish:

1. Add a contact
2. Generate a message
3. Evaluate the message
4. Save the message
5. Track the follow-up

That workflow made the project feel more like a real tool instead of a one-screen AI demo.

I also learned how to structure a small Python app, handle environment variables, manage local data with SQLite, and think about how AI can support a business or recruiting process.

## Future improvements

Some features I would consider adding later:

* Export contacts and messages to CSV
* Filter contacts by company, status, or event
* Calendar reminders for follow-ups
* Better analytics on outreach activity
* More advanced prompt customization
* User authentication
* Hosted database support
* Deployment-ready multi-user version

## Important note

This app does not scrape LinkedIn or automate platform activity. It is designed for organizing contacts, drafting messages, and tracking follow-ups manually and ethically.

## Project status

Version 1 is complete as a working MVP. The app is focused on being simple, practical, and explainable.
