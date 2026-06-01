import pandas as pd
import streamlit as st

from src.database import add_contact, get_all_contacts, initialize_database
from src.openai_utils import generate_outreach_message


STATUS_OPTIONS = [
    "Not contacted",
    "Message drafted",
    "Contacted",
    "Replied",
    "Meeting scheduled",
    "Follow-up needed",
]

MESSAGE_TYPE_OPTIONS = [
    "LinkedIn connection request",
    "LinkedIn follow-up",
    "Email outreach",
    "Conference follow-up",
    "Recruiter message",
]

TONE_OPTIONS = ["Professional", "Warm", "Concise"]

GOAL_OPTIONS = [
    "Connect",
    "Ask for advice",
    "Request informational interview",
    "Follow up after event",
]

CONTACT_COLUMNS = [
    "ID",
    "Name",
    "Company",
    "Role",
    "LinkedIn URL",
    "Source/Event",
    "Notes",
    "Status",
    "Created At",
]


def contacts_to_dataframe(contacts):
    """Convert database rows into a readable contacts DataFrame."""
    return pd.DataFrame(contacts, columns=CONTACT_COLUMNS)


def build_contact_options(contacts):
    """Create selectbox labels mapped to contact dictionaries."""
    contact_options = {}

    for contact in contacts:
        (
            contact_id,
            name,
            company,
            role,
            linkedin_url,
            source_event,
            notes,
            status,
            created_at,
        ) = contact

        label_parts = [name]

        if company:
            label_parts.append(company)
        elif role:
            label_parts.append(role)

        contact_label = f"{' - '.join(label_parts)} (ID {contact_id})"
        contact_options[contact_label] = {
            "id": contact_id,
            "name": name,
            "company": company,
            "role": role,
            "linkedin_url": linkedin_url,
            "source_event": source_event,
            "notes": notes,
            "status": status,
            "created_at": created_at,
        }

    return contact_options


def get_status_count(df, status):
    """Return how many contacts have a specific status."""
    if df.empty:
        return 0
    return int((df["Status"] == status).sum())


st.set_page_config(page_title="AI Networking CRM", layout="wide")

initialize_database()
contacts = get_all_contacts()
contacts_df = contacts_to_dataframe(contacts) if contacts else pd.DataFrame(columns=CONTACT_COLUMNS)

with st.sidebar:
    st.title("AI Networking CRM")
    st.caption("Portfolio-ready networking workflow")

    st.divider()
    st.markdown("**Workflow**")
    st.markdown("1. Add contacts from events or LinkedIn.")
    st.markdown("2. Track relationship status.")
    st.markdown("3. Generate a personalized outreach draft.")

    st.divider()
    st.markdown("**Current database**")
    st.metric("Saved contacts", len(contacts))
    st.caption("Generated messages are not saved yet.")

st.title("AI Networking CRM")
st.subheader("Manage networking relationships and draft personalized outreach with AI.")
st.write(
    "This tool helps job seekers, founders, and professionals organize contacts, "
    "track follow-up status, and generate short outreach messages from saved context."
)

st.divider()

st.header("Dashboard")
st.caption("A quick snapshot of your networking pipeline.")

metric_columns = st.columns(6)
metric_columns[0].metric("Total contacts", len(contacts))
metric_columns[1].metric("Not contacted", get_status_count(contacts_df, "Not contacted"))
metric_columns[2].metric("Contacted", get_status_count(contacts_df, "Contacted"))
metric_columns[3].metric("Replied", get_status_count(contacts_df, "Replied"))
metric_columns[4].metric("Meetings scheduled", get_status_count(contacts_df, "Meeting scheduled"))
metric_columns[5].metric("Follow-up needed", get_status_count(contacts_df, "Follow-up needed"))

if contacts_df.empty:
    st.info(
        "No contacts yet. Add your first contact below, then use the AI generator to draft outreach."
    )

st.divider()

st.header("Add Contact")
st.caption("Capture only the details that make a future message more personal.")

with st.container(border=True):
    with st.form("add_contact_form", clear_on_submit=True):
        first_row = st.columns(3)
        name = first_row[0].text_input("Name *")
        company = first_row[1].text_input("Company")
        role = first_row[2].text_input("Role / Title")

        second_row = st.columns(2)
        linkedin_url = second_row[0].text_input("LinkedIn URL")
        source_event = second_row[1].text_input("Source / Event")

        notes = st.text_area(
            "Notes",
            placeholder="Example: Met at AI meetup. Interested in healthcare startups.",
            height=110,
        )
        status = st.selectbox("Status", STATUS_OPTIONS)

        submitted = st.form_submit_button("Save Contact", use_container_width=True)

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
                st.rerun()

st.divider()

st.header("Contact List")
st.caption("Review your saved contacts and focus on the fields that matter during outreach.")

if contacts_df.empty:
    st.info("Your contact list is empty. Add a contact above to start building your pipeline.")
else:
    overview_columns = [
        "Name",
        "Company",
        "Role",
        "Status",
        "Source/Event",
        "Created At",
    ]
    st.dataframe(
        contacts_df[overview_columns],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Show full contact details"):
        st.dataframe(contacts_df, use_container_width=True, hide_index=True)

st.divider()

st.header("AI Message Generator")
st.caption(
    "Choose a saved contact and generate a short draft that can be copied into LinkedIn or email."
)

if contacts_df.empty:
    st.info("Add a contact first, then come back here to generate a personalized message.")
else:
    contact_options = build_contact_options(contacts)
    generator_left, generator_right = st.columns([1, 1.2])

    with generator_left:
        with st.container(border=True):
            st.subheader("Message setup")
            selected_contact_label = st.selectbox(
                "Select a saved contact",
                list(contact_options.keys()),
                index=None,
                placeholder="Choose a contact",
            )

            message_type = st.selectbox("Message type", MESSAGE_TYPE_OPTIONS)
            tone = st.selectbox("Tone", TONE_OPTIONS)
            goal = st.selectbox("Goal", GOAL_OPTIONS)

            generate_clicked = st.button("Generate Message", use_container_width=True)

            if selected_contact_label:
                selected_contact = contact_options[selected_contact_label]
                with st.expander("Selected contact context", expanded=False):
                    st.write(f"**Name:** {selected_contact['name']}")
                    st.write(f"**Company:** {selected_contact['company'] or 'Not provided'}")
                    st.write(f"**Role:** {selected_contact['role'] or 'Not provided'}")
                    st.write(f"**Source/Event:** {selected_contact['source_event'] or 'Not provided'}")
                    st.write(f"**Status:** {selected_contact['status'] or 'Not provided'}")
                    st.write(f"**Notes:** {selected_contact['notes'] or 'Not provided'}")
            else:
                selected_contact = None
                st.info("Select a contact to give the AI useful context.")

    with generator_right:
        with st.container(border=True):
            st.subheader("Generated draft")

            if generate_clicked:
                if selected_contact is None:
                    st.error("Please select a saved contact before generating a message.")
                else:
                    with st.spinner("Generating a personalized outreach draft..."):
                        try:
                            generated_message = generate_outreach_message(
                                selected_contact,
                                message_type,
                                tone,
                                goal,
                            )
                            st.session_state["generated_outreach_message"] = generated_message
                            st.success("Message generated. Review and copy it when ready.")
                        except ValueError as error:
                            st.error(str(error))
                        except RuntimeError as error:
                            st.error(str(error))

            if "generated_outreach_message" in st.session_state:
                st.text_area(
                    "Copy-ready message",
                    value=st.session_state["generated_outreach_message"],
                    height=220,
                )
                st.caption("Generated messages are drafts. Review before sending.")
            else:
                st.info("Your generated message will appear here.")
