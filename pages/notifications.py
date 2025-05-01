import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
from notification_service import (
    send_case_update, 
    send_rights_reminder, 
    send_hearing_reminder,
    check_twilio_credentials
)

st.set_page_config(
    page_title="Notifications - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Legal Notifications")
st.markdown("### Set up SMS alerts for your legal matters")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

if st.sidebar.button("Defendant Rights"):
    st.switch_page("pages/defendant_rights.py")

if st.sidebar.button("Rights Predictor"):
    st.switch_page("pages/rights_predictor.py")

# Check if Twilio credentials are configured
has_twilio_credentials = check_twilio_credentials()

if not has_twilio_credentials:
    st.warning("""
    **Twilio credentials are not configured.**
    
    To enable SMS notifications, please configure your Twilio credentials:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_PHONE_NUMBER
    
    Contact the system administrator to set up these credentials.
    """)
    
    if st.button("Twilio SMS Setup & Testing"):
        st.switch_page("pages/twilio_test.py")

# Create tabs for different notification types
tab1, tab2, tab3, tab4 = st.tabs(["Case Updates", "Rights Reminders", "Hearing Reminders", "Notification History"])

with tab1:
    st.markdown("## Case Update Notifications")
    st.markdown("""
    Receive SMS notifications when there are updates to your legal cases. 
    Stay informed about status changes, new filings, or decisions.
    """)
    
    # Form for case update notifications
    with st.form("case_update_form"):
        phone_number = st.text_input(
            "Phone Number", 
            placeholder="Enter your phone number (e.g., +91 98765 43210)",
        )
        
        case_ref = st.text_input(
            "Case Reference", 
            placeholder="Enter case number or reference ID"
        )
        
        update_type = st.selectbox(
            "Update Type",
            options=[
                "Case Status Change", 
                "New Document Filed", 
                "Court Order Issued", 
                "Hearing Scheduled", 
                "Case Transferred",
                "Custom Update"
            ]
        )
        
        if update_type == "Custom Update":
            update_message = st.text_area(
                "Custom Message", 
                placeholder="Enter custom update message"
            )
        else:
            update_message = f"{update_type} for case {case_ref}"
        
        submit_button = st.form_submit_button("Send Notification", use_container_width=True)
    
    if submit_button:
        if not phone_number or not case_ref:
            st.error("Please enter both phone number and case reference.")
        elif not has_twilio_credentials:
            st.error("Cannot send SMS. Twilio credentials not configured.")
        else:
            with st.spinner("Sending notification..."):
                result = send_case_update(phone_number, case_ref, update_message)
                
                if result["status"] == "success":
                    st.success(result["message"])
                    # Store notification in session state for history
                    if "notification_history" not in st.session_state:
                        st.session_state.notification_history = []
                    
                    st.session_state.notification_history.append({
                        "type": "Case Update",
                        "recipient": phone_number,
                        "content": update_message,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Sent",
                        "message_id": result.get("message_sid", "N/A")
                    })
                else:
                    st.error(result["message"])

with tab2:
    st.markdown("## Rights Reminder Notifications")
    st.markdown("""
    Receive SMS reminders about your key legal rights. These reminders can be crucial 
    during important stages of your legal proceedings.
    """)
    
    # Form for rights reminder notifications
    with st.form("rights_reminder_form"):
        phone_number = st.text_input(
            "Phone Number", 
            placeholder="Enter your phone number (e.g., +91 98765 43210)",
            key="rights_phone"
        )
        
        # Select rights to include in the reminder
        st.markdown("**Select Rights to Include in the Reminder:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            right1 = st.checkbox("Right to legal representation", value=True)
            right2 = st.checkbox("Right to remain silent", value=True)
            right3 = st.checkbox("Right to bail application", value=True)
            right4 = st.checkbox("Right to a fair trial", value=False)
            right5 = st.checkbox("Right to speedy trial", value=False)
        
        with col2:
            right6 = st.checkbox("Right to be informed of charges", value=False)
            right7 = st.checkbox("Right to cross-examine witnesses", value=False)
            right8 = st.checkbox("Right to present evidence", value=False)
            right9 = st.checkbox("Right to appeal", value=False)
            right10 = st.checkbox("Right to interpretation services", value=False)
        
        # Custom right
        custom_right = st.text_input(
            "Add Custom Right (Optional)",
            placeholder="Enter a custom right to include in the reminder"
        )
        
        # Compile selected rights
        selected_rights = []
        if right1: selected_rights.append("Right to legal representation")
        if right2: selected_rights.append("Right to remain silent")
        if right3: selected_rights.append("Right to bail application")
        if right4: selected_rights.append("Right to a fair trial")
        if right5: selected_rights.append("Right to speedy trial")
        if right6: selected_rights.append("Right to be informed of charges")
        if right7: selected_rights.append("Right to cross-examine witnesses")
        if right8: selected_rights.append("Right to present evidence")
        if right9: selected_rights.append("Right to appeal")
        if right10: selected_rights.append("Right to interpretation services")
        if custom_right: selected_rights.append(custom_right)
        
        rights_submit = st.form_submit_button("Send Rights Reminder", use_container_width=True)
    
    if rights_submit:
        if not phone_number:
            st.error("Please enter a phone number.")
        elif not selected_rights:
            st.error("Please select at least one right to include in the reminder.")
        elif not has_twilio_credentials:
            st.error("Cannot send SMS. Twilio credentials not configured.")
        else:
            with st.spinner("Sending rights reminder..."):
                result = send_rights_reminder(phone_number, selected_rights)
                
                if result["status"] == "success":
                    st.success(result["message"])
                    # Store notification in session state for history
                    if "notification_history" not in st.session_state:
                        st.session_state.notification_history = []
                    
                    st.session_state.notification_history.append({
                        "type": "Rights Reminder",
                        "recipient": phone_number,
                        "content": ", ".join(selected_rights[:3]) + ("..." if len(selected_rights) > 3 else ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Sent",
                        "message_id": result.get("message_sid", "N/A")
                    })
                else:
                    st.error(result["message"])

with tab3:
    st.markdown("## Hearing Reminder Notifications")
    st.markdown("""
    Set up SMS reminders for upcoming court hearings. Never miss an important court date 
    with timely notifications.
    """)
    
    # Form for hearing reminder notifications
    with st.form("hearing_reminder_form"):
        phone_number = st.text_input(
            "Phone Number", 
            placeholder="Enter your phone number (e.g., +91 98765 43210)",
            key="hearing_phone"
        )
        
        case_ref = st.text_input(
            "Case Reference", 
            placeholder="Enter case number or reference ID",
            key="hearing_case"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            hearing_date = st.date_input(
                "Hearing Date",
                value=datetime.now().date() + timedelta(days=1)
            )
        
        with col2:
            hearing_time = st.time_input(
                "Hearing Time",
                value=datetime.strptime("10:30", "%H:%M").time()
            )
        
        court_location = st.text_input(
            "Court Location",
            placeholder="Enter court name and location"
        )
        
        additional_notes = st.text_area(
            "Additional Notes (Optional)",
            placeholder="Enter any additional information or instructions",
            height=100
        )
        
        # Schedule options
        st.markdown("**When to send the reminder:**")
        reminder_option = st.selectbox(
            "Send Reminder",
            options=[
                "Send immediately", 
                "1 day before hearing", 
                "2 days before hearing",
                "1 week before hearing"
            ]
        )
        
        hearing_submit = st.form_submit_button("Schedule Hearing Reminder", use_container_width=True)
    
    if hearing_submit:
        if not phone_number or not case_ref or not court_location:
            st.error("Please fill in all required fields.")
        elif not has_twilio_credentials:
            st.error("Cannot send SMS. Twilio credentials not configured.")
        else:
            with st.spinner("Scheduling hearing reminder..."):
                # Format date and time
                formatted_date = hearing_date.strftime("%d %b, %Y")
                formatted_time = hearing_time.strftime("%I:%M %p")
                
                if reminder_option == "Send immediately":
                    # Send the reminder immediately
                    hearing_details = {
                        'case_ref': case_ref,
                        'date': formatted_date,
                        'time': formatted_time,
                        'court': court_location,
                        'notes': additional_notes
                    }
                    result = send_hearing_reminder(
                        phone_number,
                        hearing_details['case_ref'],
                        hearing_details['date'],
                        hearing_details['time'],
                        hearing_details['court'],
                        hearing_details['notes']
                    )
                    
                    if result["status"] == "success":
                        st.success("Hearing reminder sent successfully.")
                        # Store notification in session state for history
                        if "notification_history" not in st.session_state:
                            st.session_state.notification_history = []
                        
                        st.session_state.notification_history.append({
                            "type": "Hearing Reminder",
                            "recipient": phone_number,
                            "content": f"Case {case_ref} on {formatted_date} at {formatted_time}",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "Sent",
                            "message_id": result.get("message_sid", "N/A")
                        })
                    else:
                        st.error(result["message"])
                else:
                    # In a real system, this would schedule the reminder for later delivery
                    # For demonstration, we'll just show a success message
                    st.success(f"Hearing reminder scheduled to be sent {reminder_option}.")
                    # Store notification in session state for history
                    if "notification_history" not in st.session_state:
                        st.session_state.notification_history = []
                    
                    st.session_state.notification_history.append({
                        "type": "Hearing Reminder (Scheduled)",
                        "recipient": phone_number,
                        "content": f"Case {case_ref} on {formatted_date} at {formatted_time}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Scheduled",
                        "message_id": "Pending"
                    })
                    
                    st.info("Note: In this demo, scheduled reminders are simulated and not actually sent at the scheduled time.")

with tab4:
    st.markdown("## Notification History")
    st.markdown("View a history of your sent and scheduled notifications.")
    
    if "notification_history" not in st.session_state or not st.session_state.notification_history:
        st.info("No notifications have been sent yet.")
    else:
        # Convert notification history to DataFrame for display
        history_df = pd.DataFrame(st.session_state.notification_history)
        
        # Add filter for notification type
        if not history_df.empty:
            notification_types = ["All"] + list(history_df["type"].unique())
            selected_type = st.selectbox("Filter by Notification Type", options=notification_types)
            
            if selected_type != "All":
                filtered_df = history_df[history_df["type"] == selected_type]
            else:
                filtered_df = history_df
            
            st.dataframe(
                filtered_df[["timestamp", "type", "recipient", "content", "status", "message_id"]],
                use_container_width=True
            )
            
            if st.button("Clear History", use_container_width=True):
                st.session_state.notification_history = []
                st.success("Notification history cleared.")
                st.rerun()

# Bottom section with instructions and disclaimer
st.markdown("---")
st.markdown("## SMS Notification Guidelines")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Best Practices
    - **Consent:** Ensure you have the recipient's consent before sending SMS notifications
    - **Frequency:** Avoid sending too many notifications to prevent notification fatigue
    - **Content:** Keep messages concise and relevant to legal matters
    - **Security:** Don't include sensitive legal details in SMS messages
    """)

with col2:
    st.markdown("""
    ### Benefits of SMS Notifications
    - **Timely Reminders:** Never miss important court dates or deadlines
    - **Stay Informed:** Receive instant updates about your case
    - **Rights Awareness:** Regular reminders about your legal rights
    - **Offline Access:** Access critical information without internet
    """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: SMS notifications are provided as a courtesy service and should not be relied upon as the sole reminder for legal proceedings. 
Standard SMS rates may apply based on your carrier. Always consult with a qualified legal professional for advice specific to your situation.
""")