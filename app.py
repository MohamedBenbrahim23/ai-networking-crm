import streamlit as st
import pandas as pd

from src.database import initialize_database, add_contact, get_all_contacts

st.set_page_config(page_title="AI Networking CRM", layout="wide")

initialize_database()

st.title("AI Networking CRM")
st.write("Manage networking contacts, outreach, and follow-ups in one place.")

st.divider()

st.header("Add a New Contact")

with st.form("add_contact_form"):
    name = st.text_input("Name *")
    company = st.text_input("Company")
    role = st.text_input("Role / Title")
    linkedin_url = st.text_input("LinkedIn URL")
    source_event = st.text_input("Source / Event")
    notes = st.text_area("Notes")
    status = st.selectbox(
        "Status",
        [
            "Not contacted",
            "Message drafted",
            "Contacted",
            "Replied",
            "Meeting scheduled",
            "Follow-up needed",
        ],
    )

    submitted = st.form_submit_button("Save Contact")

    if submitted:
        if not name.strip():
            st.error("Name is required.")
        else:
            add_contact(
                name=name,
                company=company,
                role=role,
                linkedin_url=linkedin_url,
                source_event=source_event,
                notes=notes,
                status=status,
            )
            st.success(f"Saved contact: {name}")

st.divider()

st.header("Saved Contacts")

contacts = get_all_contacts()

if contacts:
    df = pd.DataFrame(
        contacts,
        columns=[
            "ID",
            "Name",
            "Company",
            "Role",
            "LinkedIn URL",
            "Source/Event",
            "Notes",
            "Status",
            "Created At",
        ],
    )

    st.dataframe(df, use_container_width=True)
else:
    st.info("No contacts saved yet. Add your first networking contact above.")