import sqlite3
from datetime import date
from pathlib import Path


DB_PATH = Path("data/networking_crm.db")


def get_connection():
    """Create and return a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create required tables and safely add new columns when needed."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            role TEXT,
            linkedin_url TEXT,
            source_event TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Not contacted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    _add_column_if_missing(cursor, "contacts", "last_contacted_date", "TEXT")
    _add_column_if_missing(cursor, "contacts", "follow_up_date", "TEXT")
    _add_column_if_missing(cursor, "contacts", "follow_up_notes", "TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            message_type TEXT,
            tone TEXT,
            goal TEXT,
            message_text TEXT NOT NULL,
            quality_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
        """
    )

    conn.commit()
    conn.close()


def _add_column_if_missing(cursor, table_name, column_name, column_type):
    """Add a column only when it does not already exist."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [column[1] for column in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def add_contact(name, company, role, linkedin_url, source_event, notes, status):
    """Add a new contact to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO contacts
        (name, company, role, linkedin_url, source_event, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, company, role, linkedin_url, source_event, notes, status),
    )

    conn.commit()
    conn.close()


def get_all_contacts():
    """Return all contacts from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, company, role, linkedin_url, source_event, notes, status,
               created_at, last_contacted_date, follow_up_date, follow_up_notes
        FROM contacts
        ORDER BY created_at DESC
        """
    )

    contacts = cursor.fetchall()
    conn.close()

    return contacts


def save_message(contact_id, message_type, tone, goal, message_text, quality_score=None):
    """Save an outreach message for a contact."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (contact_id, message_type, tone, goal, message_text, quality_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (contact_id, message_type, tone, goal, message_text, quality_score),
    )

    conn.commit()
    conn.close()


def get_messages_for_contact(contact_id):
    """Return saved messages for one contact."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, contact_id, message_type, tone, goal, message_text, quality_score, created_at
        FROM messages
        WHERE contact_id = ?
        ORDER BY created_at DESC
        """,
        (contact_id,),
    )

    messages = cursor.fetchall()
    conn.close()

    return messages


def get_all_messages():
    """Return all saved messages."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, contact_id, message_type, tone, goal, message_text, quality_score, created_at
        FROM messages
        ORDER BY created_at DESC
        """
    )

    messages = cursor.fetchall()
    conn.close()

    return messages


def update_contact_followup(contact_id, last_contacted_date, follow_up_date, follow_up_notes, status):
    """Update follow-up fields and status for one contact."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE contacts
        SET last_contacted_date = ?,
            follow_up_date = ?,
            follow_up_notes = ?,
            status = ?
        WHERE id = ?
        """,
        (last_contacted_date, follow_up_date, follow_up_notes, status, contact_id),
    )

    conn.commit()
    conn.close()


def get_contacts_needing_followup():
    """Return contacts marked for follow-up or due by date."""
    today = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, company, role, linkedin_url, source_event, notes, status,
               created_at, last_contacted_date, follow_up_date, follow_up_notes
        FROM contacts
        WHERE status = 'Follow-up needed'
           OR (
                follow_up_date IS NOT NULL
                AND follow_up_date != ''
                AND date(follow_up_date) <= date(?)
           )
        ORDER BY follow_up_date ASC
        """,
        (today,),
    )

    contacts = cursor.fetchall()
    conn.close()

    return contacts
