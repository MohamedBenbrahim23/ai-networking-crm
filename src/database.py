import sqlite3
from pathlib import Path

DB_PATH = Path("data/networking_crm.db")


def get_connection():
    """Create and return a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the contacts table if it does not already exist."""
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

    conn.commit()
    conn.close()


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
        SELECT id, name, company, role, linkedin_url, source_event, notes, status, created_at
        FROM contacts
        ORDER BY created_at DESC
        """
    )

    contacts = cursor.fetchall()
    conn.close()

    return contacts