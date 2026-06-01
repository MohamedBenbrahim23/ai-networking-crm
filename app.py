import pandas as pd
import streamlit as st
from datetime import date

from src.database import (
    add_contact,
    get_all_contacts,
    get_all_messages,
    get_contacts_needing_followup,
    get_messages_for_contact,
    initialize_database,
    save_message,
    update_contact_followup,
)
from src.openai_utils import generate_outreach_message, score_outreach_message


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
    "Last Contacted",
    "Follow-up Date",
    "Follow-up Notes",
]

MESSAGE_COLUMNS = [
    "ID",
    "Contact ID",
    "Message Type",
    "Tone",
    "Goal",
    "Message Text",
    "Quality Score",
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
            last_contacted_date,
            follow_up_date,
            follow_up_notes,
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
            "last_contacted_date": last_contacted_date,
            "follow_up_date": follow_up_date,
            "follow_up_notes": follow_up_notes,
        }

    return contact_options


def messages_to_dataframe(messages):
    """Convert saved message rows into a readable DataFrame."""
    return pd.DataFrame(messages, columns=MESSAGE_COLUMNS)


def parse_date_value(value):
    """Convert a stored ISO date string into a date object for Streamlit inputs."""
    if not value:
        return None

    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def format_date_for_database(value):
    """Convert a date input value into an ISO string for SQLite."""
    if not value:
        return ""
    return value.isoformat()


def get_status_count(df, status):
    """Return how many contacts have a specific status."""
    if df.empty:
        return 0
    return int((df["Status"] == status).sum())


def apply_custom_styles():
    """Add lightweight visual polish while keeping the app Streamlit-native."""
    st.markdown(
        """
        <style>
            :root {
                --crm-navy: #0f172a;
                --crm-blue: #2563eb;
                --crm-blue-soft: #eff6ff;
                --crm-text: #1f2937;
                --crm-muted: #64748b;
                --crm-border: #dbe4f0;
                --crm-panel: #ffffff;
                --crm-page: #f5f7fb;
            }

            html, body, [class*="css"] {
                font-family: Inter, "Segoe UI", Arial, sans-serif;
                color: var(--crm-text);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 30rem),
                    linear-gradient(180deg, #f8fbff 0%, var(--crm-page) 45%, #f8fafc 100%);
            }

            .main .block-container {
                max-width: 1180px;
                padding-top: 2rem;
                padding-bottom: 4rem;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f172a 0%, #15223a 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #e5edf8;
            }

            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                box-shadow: none;
            }

            .crm-hero {
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 64, 175, 0.92)),
                    linear-gradient(45deg, #0f172a, #1d4ed8);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 18px;
                padding: 2.2rem 2.4rem;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
                margin-bottom: 1.8rem;
            }

            .crm-kicker {
                color: #bfdbfe;
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                margin-bottom: 0.65rem;
                text-transform: uppercase;
            }

            .crm-hero h1 {
                color: #ffffff;
                font-size: clamp(2.2rem, 5vw, 4.2rem);
                line-height: 1.03;
                margin: 0 0 0.75rem 0;
                letter-spacing: 0;
            }

            .crm-hero h2 {
                color: #dbeafe;
                font-size: 1.25rem;
                line-height: 1.45;
                font-weight: 650;
                margin: 0 0 0.9rem 0;
            }

            .crm-hero p {
                color: #e2e8f0;
                font-size: 1rem;
                line-height: 1.65;
                max-width: 760px;
                margin: 0;
            }

            h2, h3 {
                color: var(--crm-navy);
                letter-spacing: 0;
            }

            div[data-testid="stMetric"] {
                background: var(--crm-panel);
                border: 1px solid var(--crm-border);
                border-radius: 14px;
                padding: 1rem 1.1rem;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
            }

            div[data-testid="stMetric"] label {
                color: var(--crm-muted);
                font-size: 0.86rem;
                font-weight: 650;
            }

            div[data-testid="stMetricValue"] {
                color: var(--crm-navy);
                font-weight: 750;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid var(--crm-border);
                border-radius: 16px;
                box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
            }

            .stButton > button,
            .stFormSubmitButton > button {
                background: linear-gradient(135deg, #1d4ed8, #2563eb);
                border: 1px solid #1d4ed8;
                border-radius: 10px;
                color: #ffffff;
                font-weight: 700;
                min-height: 2.75rem;
                box-shadow: 0 10px 18px rgba(37, 99, 235, 0.20);
                transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
            }

            .stButton > button:hover,
            .stFormSubmitButton > button:hover {
                border-color: #1e40af;
                box-shadow: 0 14px 24px rgba(37, 99, 235, 0.28);
                color: #ffffff;
                transform: translateY(-1px);
            }

            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] {
                border-radius: 10px;
            }

            .stTextArea textarea {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                line-height: 1.55;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid var(--crm-border);
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
            }

            [data-testid="stAlert"] {
                border-radius: 12px;
                border: 1px solid rgba(37, 99, 235, 0.16);
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
            }

            [data-testid="stExpander"] {
                background: rgba(255, 255, 255, 0.75);
                border-radius: 12px;
                border: 1px solid var(--crm-border);
            }

            hr {
                border-color: #dbe4f0;
                margin: 2rem 0 1.4rem 0;
            }

            @media (max-width: 768px) {
                .crm-hero {
                    padding: 1.6rem;
                    border-radius: 14px;
                }

                .main .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="AI Networking CRM", layout="wide")
apply_custom_styles()

initialize_database()
contacts = get_all_contacts()
contacts_df = contacts_to_dataframe(contacts) if contacts else pd.DataFrame(columns=CONTACT_COLUMNS)
saved_messages = get_all_messages()
saved_messages_df = messages_to_dataframe(saved_messages) if saved_messages else pd.DataFrame(columns=MESSAGE_COLUMNS)
followup_contacts = get_contacts_needing_followup()
followup_contacts_df = (
    contacts_to_dataframe(followup_contacts) if followup_contacts else pd.DataFrame(columns=CONTACT_COLUMNS)
)

with st.sidebar:
    st.title("AI Networking CRM")
    st.caption("Portfolio-ready networking workflow")

    st.divider()
    st.markdown("**Workflow**")
    st.markdown("1. Add contacts from events or LinkedIn.")
    st.markdown("2. Track relationship status.")
    st.markdown("3. Generate a personalized outreach draft.")
    st.markdown("4. Score and improve the message.")
    st.markdown("5. Save messages and follow-ups.")

    st.divider()
    st.markdown("**Current database**")
    st.metric("Saved contacts", len(contacts))
    st.metric("Saved messages", len(saved_messages))
    st.caption("Follow-up dates are stored locally in SQLite.")

st.markdown(
    """
    <section class="crm-hero">
        <div class="crm-kicker">AI workflow dashboard</div>
        <h1>AI Networking CRM</h1>
        <h2>Manage networking relationships and draft personalized outreach with AI.</h2>
        <p>
            A focused CRM for organizing contacts, tracking follow-up status, and turning saved
            relationship context into practical LinkedIn or email outreach drafts.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
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

tracking_columns = st.columns(4)
tracking_columns[0].metric("Saved messages", len(saved_messages))
tracking_columns[1].metric("Due follow-ups", len(followup_contacts))
tracking_columns[2].metric("Meetings scheduled", get_status_count(contacts_df, "Meeting scheduled"))
tracking_columns[3].metric("Contacts replied", get_status_count(contacts_df, "Replied"))

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
        "Follow-up Date",
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
                            st.session_state["generated_message_metadata"] = {
                                "contact_id": selected_contact["id"],
                                "message_type": message_type,
                                "tone": tone,
                                "goal": goal,
                            }
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

st.divider()

st.header("Message Quality Scorer")
st.caption(
    "Paste a draft, optionally add contact context, and get practical feedback before sending."
)

if "generated_outreach_message" in st.session_state and "message_to_score" not in st.session_state:
    st.session_state["message_to_score"] = st.session_state["generated_outreach_message"]

scorer_left, scorer_right = st.columns([1, 1.15])

with scorer_left:
    with st.container(border=True):
        st.subheader("Message to review")

        message_to_score = st.text_area(
            "Paste or edit your outreach message",
            key="message_to_score",
            height=230,
            placeholder="Paste a LinkedIn or email outreach draft here.",
        )

        if "generated_outreach_message" in st.session_state:
            st.caption("The latest generated message is loaded here automatically.")

        scoring_contact = None

        if contacts_df.empty:
            st.info("Optional contact context will appear here after you add contacts.")
        else:
            scoring_contact_options = build_contact_options(contacts)
            scoring_contact_label = st.selectbox(
                "Optional contact context",
                ["No contact context"] + list(scoring_contact_options.keys()),
            )

            if scoring_contact_label != "No contact context":
                scoring_contact = scoring_contact_options[scoring_contact_label]

        score_clicked = st.button("Score Message", use_container_width=True)

with scorer_right:
    with st.container(border=True):
        st.subheader("Quality report")

        if score_clicked:
            try:
                with st.spinner("Scoring message quality..."):
                    score_result = score_outreach_message(message_to_score, scoring_contact)
                    st.session_state["message_score_result"] = score_result
                st.success("Message scored. Use the feedback to tighten your draft.")
            except ValueError as error:
                if "Paste or write" in str(error):
                    st.warning(str(error))
                else:
                    st.error(str(error))
            except RuntimeError as error:
                st.error(str(error))

        if "message_score_result" in st.session_state:
            score_result = st.session_state["message_score_result"]
            overall_score = score_result["overall_score"]

            st.metric("Overall score", f"{overall_score}/10")
            st.progress(max(0, min(overall_score, 10)) / 10)

            st.write("**Category scores**")
            score_columns = st.columns(5)

            for index, (category, score) in enumerate(score_result["category_scores"].items()):
                score_columns[index].metric(category, f"{score}/10")

            st.write("**Explanation**")
            st.write(score_result["explanation"])

            st.write("**Improvement suggestions**")
            for suggestion in score_result["improvement_suggestions"]:
                st.markdown(f"- {suggestion}")
        else:
            st.info("Your score report will appear here after you review a message.")

st.divider()

st.header("Saved Messages & Follow-Up Tracking")
st.caption(
    "Store useful outreach drafts and keep lightweight follow-up notes for each contact."
)

if contacts_df.empty:
    st.info("Add a contact first before saving messages or tracking follow-ups.")
else:
    tracking_contact_options = build_contact_options(contacts)
    tracking_contact_label = st.selectbox(
        "Select a contact to manage",
        list(tracking_contact_options.keys()),
        key="tracking_contact_selector",
    )
    tracking_contact = tracking_contact_options[tracking_contact_label]
    tracking_contact_id = tracking_contact["id"]
    contact_messages = get_messages_for_contact(tracking_contact_id)

    messages_panel, followup_panel = st.columns([1.15, 1])

    with messages_panel:
        with st.container(border=True):
            st.subheader("Saved messages")

            if contact_messages:
                contact_messages_df = messages_to_dataframe(contact_messages)
                st.dataframe(
                    contact_messages_df[
                        [
                            "Message Type",
                            "Tone",
                            "Goal",
                            "Quality Score",
                            "Created At",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

                with st.expander("Read saved message text"):
                    for message in contact_messages:
                        (
                            message_id,
                            contact_id,
                            saved_message_type,
                            saved_tone,
                            saved_goal,
                            saved_message_text,
                            saved_quality_score,
                            saved_created_at,
                        ) = message
                        st.write(f"**Message {message_id} - {saved_message_type or 'Outreach'}**")
                        st.caption(f"Saved {saved_created_at}")
                        st.text_area(
                            "Saved message text",
                            value=saved_message_text,
                            height=140,
                            key=f"saved_message_text_{message_id}",
                            disabled=True,
                        )
            else:
                st.info("No messages saved for this contact yet.")

            latest_score = None
            if "message_score_result" in st.session_state:
                latest_score = st.session_state["message_score_result"].get("overall_score")

            if "generated_outreach_message" in st.session_state:
                generated_metadata = st.session_state.get("generated_message_metadata", {})
                generated_message_type = generated_metadata.get("message_type", "AI generated")
                generated_tone = generated_metadata.get("tone", "")
                generated_goal = generated_metadata.get("goal", "")

                if st.button("Save Current Generated Message", use_container_width=True):
                    save_message(
                        tracking_contact_id,
                        generated_message_type,
                        generated_tone,
                        generated_goal,
                        st.session_state["generated_outreach_message"],
                        latest_score,
                    )
                    st.success("Generated message saved for this contact.")
                    st.rerun()
            else:
                st.info("Generate a message first, or paste one manually below.")

            with st.expander("Paste and save a message manually", expanded=False):
                with st.form("manual_message_save_form"):
                    manual_message_type = st.selectbox(
                        "Message type",
                        MESSAGE_TYPE_OPTIONS,
                        key="manual_message_type",
                    )
                    manual_tone = st.selectbox("Tone", TONE_OPTIONS, key="manual_tone")
                    manual_goal = st.selectbox("Goal", GOAL_OPTIONS, key="manual_goal")
                    manual_message_text = st.text_area(
                        "Message text",
                        height=180,
                        placeholder="Paste a LinkedIn or email draft here.",
                    )
                    st.caption(
                        "If a message has been scored in this session, its overall score will be saved too."
                    )

                    manual_save_clicked = st.form_submit_button("Save Manual Message")

                    if manual_save_clicked:
                        if not manual_message_text.strip():
                            st.warning("Paste a message before saving.")
                        else:
                            save_message(
                                tracking_contact_id,
                                manual_message_type,
                                manual_tone,
                                manual_goal,
                                manual_message_text,
                                latest_score,
                            )
                            st.success("Manual message saved.")
                            st.rerun()

    with followup_panel:
        with st.container(border=True):
            st.subheader("Follow-up details")

            with st.form("followup_update_form"):
                last_contacted_date = st.date_input(
                    "Last contacted date",
                    value=parse_date_value(tracking_contact.get("last_contacted_date")),
                )
                follow_up_date = st.date_input(
                    "Follow-up date",
                    value=parse_date_value(tracking_contact.get("follow_up_date")),
                )
                current_status = tracking_contact.get("status") or "Not contacted"
                status_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0
                followup_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=status_index,
                )
                follow_up_notes = st.text_area(
                    "Follow-up notes",
                    value=tracking_contact.get("follow_up_notes") or "",
                    height=150,
                    placeholder="Example: Follow up next week with a short thank-you note.",
                )

                followup_save_clicked = st.form_submit_button("Update Follow-Up")

                if followup_save_clicked:
                    update_contact_followup(
                        tracking_contact_id,
                        format_date_for_database(last_contacted_date),
                        format_date_for_database(follow_up_date),
                        follow_up_notes,
                        followup_status,
                    )
                    st.success("Follow-up information updated.")
                    st.rerun()

    st.subheader("Contacts needing follow-up")

    if followup_contacts_df.empty:
        st.info("No contacts are currently marked as needing follow-up.")
    else:
        st.dataframe(
            followup_contacts_df[
                [
                    "Name",
                    "Company",
                    "Role",
                    "Status",
                    "Last Contacted",
                    "Follow-up Date",
                    "Follow-up Notes",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
