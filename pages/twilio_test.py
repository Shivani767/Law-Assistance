import streamlit as st
import os
from twilio.rest import Client

st.set_page_config(
    page_title="Twilio SMS Test - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Twilio SMS Setup Test")
st.markdown("### Diagnose issues with SMS notifications")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

if st.sidebar.button("Notifications"):
    st.switch_page("pages/notifications.py")

def test_twilio_setup():
    """
    Test Twilio setup to identify issues with sending SMS.
    Returns a detailed status report.
    """
    report = {
        "credentials_found": False,
        "client_created": False,
        "account_info": None,
        "error": None,
        "phone_number_valid": False,
        "overall_status": "Failed"
    }
    
    try:
        # 1. Check if credentials are present
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        if not account_sid or not auth_token or not from_number:
            missing = []
            if not account_sid: missing.append("TWILIO_ACCOUNT_SID")
            if not auth_token: missing.append("TWILIO_AUTH_TOKEN")
            if not from_number: missing.append("TWILIO_PHONE_NUMBER")
            
            report["error"] = f"Missing credentials: {', '.join(missing)}"
            return report
        
        # Credentials found
        report["credentials_found"] = True
        
        # 2. Try to create a client
        try:
            client = Client(account_sid, auth_token)
            report["client_created"] = True
        except Exception as e:
            report["error"] = f"Failed to create Twilio client: {str(e)}"
            return report
        
        # 3. Try to get account info to verify credentials
        try:
            account = client.api.accounts(account_sid).fetch()
            report["account_info"] = {
                "friendly_name": account.friendly_name,
                "status": account.status
            }
        except Exception as e:
            report["error"] = f"Failed to verify account: {str(e)}"
            return report
        
        # 4. Check if provided phone number is valid for sending
        try:
            # Format the phone number for consistency
            if not from_number.startswith('+'):
                from_number = '+' + from_number
                
            numbers = client.incoming_phone_numbers.list(phone_number=from_number)
            if not numbers:
                report["error"] = f"The phone number {from_number} is not found in your Twilio account"
            else:
                report["phone_number_valid"] = True
        except Exception as e:
            report["error"] = f"Failed to verify phone number: {str(e)}"
            return report
        
        # Everything looks good
        if report["credentials_found"] and report["client_created"] and report["phone_number_valid"]:
            report["overall_status"] = "Success"
        else:
            if not report["error"]:
                report["error"] = "Some verifications failed. Check the report details."
            
    except Exception as e:
        report["error"] = f"Unexpected error: {str(e)}"
    
    return report

# Create a Streamlit interface to display test results
st.markdown("""
This page tests your Twilio setup to diagnose SMS sending issues.
It will check your credentials, verify account status, and test phone number configuration.
""")

test_button = st.button("Run Twilio Diagnostics", use_container_width=True)

if test_button:
    with st.spinner("Testing Twilio setup..."):
        results = test_twilio_setup()
        
        st.markdown("## Test Results")
        
        # Status indicator
        if results["overall_status"] == "Success":
            st.success("✅ Twilio setup verified successfully!")
        else:
            st.error(f"❌ Twilio setup test failed: {results.get('error', 'Unknown error')}")
        
        # Display details
        st.markdown("### Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Credentials Check**")
            if results["credentials_found"]:
                st.success("✅ Twilio credentials found")
            else:
                st.error("❌ Twilio credentials missing")
            
            st.markdown("**Client Creation**")
            if results["client_created"]:
                st.success("✅ Twilio client created successfully")
            else:
                st.error("❌ Twilio client creation failed")
        
        with col2:
            st.markdown("**Account Verification**")
            if results["account_info"]:
                st.success(f"✅ Account verified: {results['account_info'].get('friendly_name', 'Unknown')}")
                st.info(f"Account status: {results['account_info'].get('status', 'Unknown')}")
            else:
                st.error("❌ Failed to verify Twilio account")
            
            st.markdown("**Phone Number Verification**")
            if results["phone_number_valid"]:
                st.success("✅ Phone number verified and available for sending")
            else:
                st.error("❌ Phone number verification failed")
        
        # Recommendations
        st.markdown("### Recommendations")
        
        if results["overall_status"] != "Success":
            if not results["credentials_found"]:
                st.markdown("""
                - Make sure all three environment variables are set: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`
                - Verify that there are no typos in the variable names
                """)
            elif not results["client_created"]:
                st.markdown("""
                - Check that your Account SID and Auth Token are correct
                - Ensure your Twilio account is active and not suspended
                """)
            elif not results["account_info"]:
                st.markdown("""
                - Your Twilio credentials may be invalid or expired
                - Verify your account status in the Twilio console
                """)
            elif not results["phone_number_valid"]:
                st.markdown("""
                - The phone number you provided is not found in your Twilio account
                - Verify that the phone number is in the correct format (e.g., +1XXXXXXXXXX)
                - Check that the phone number is enabled for SMS in your Twilio console
                - If using a trial account, make sure the recipient number is verified
                """)
        else:
            st.markdown("""
            - Your Twilio setup appears to be working correctly
            - If you're still having issues sending SMS, check the following:
              - Recipient phone numbers are formatted correctly
              - Your Twilio account has sufficient credits or is set up for billing
              - If using a trial account, recipient numbers must be verified in Twilio
              - The message content doesn't violate Twilio's policies
            """)

# Try to send a test message
st.markdown("---")
st.markdown("## Send Test SMS")

with st.form("test_sms_form"):
    phone_number = st.text_input(
        "Recipient Phone Number", 
        placeholder="Enter recipient phone number (e.g., +91 98765 43210)"
    )
    
    message = st.text_input(
        "Message", 
        value="This is a test message from the Indian Legal Assistant system."
    )
    
    test_sms_button = st.form_submit_button("Send Test SMS", use_container_width=True)

if test_sms_button:
    if not phone_number:
        st.error("Please enter a recipient phone number.")
    else:
        with st.spinner("Sending test SMS..."):
            try:
                # Format the phone number
                formatted_number = phone_number.strip()
                if not formatted_number.startswith('+'):
                    # Add India country code if not present
                    if formatted_number.startswith('0'):
                        formatted_number = '+91' + formatted_number[1:]
                    elif len(formatted_number) == 10:
                        formatted_number = '+91' + formatted_number
                    else:
                        formatted_number = '+' + formatted_number
                
                # Get Twilio credentials
                account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
                from_number = os.environ.get("TWILIO_PHONE_NUMBER")
                
                if not all([account_sid, auth_token, from_number]):
                    st.error("Missing Twilio credentials. Please check setup.")
                else:
                    # Create client
                    client = Client(account_sid, auth_token)
                    
                    # Additional information for debugging
                    st.info(f"Attempting to send from {from_number} to {formatted_number}")
                    
                    # Send message with detailed error handling
                    try:
                        sms_message = client.messages.create(
                            body=message,
                            from_=from_number,
                            to=formatted_number
                        )
                        
                        st.success(f"Test message sent successfully! SID: {sms_message.sid}")
                        st.markdown(f"""
                        **Message details:**
                        - Status: {sms_message.status}
                        - From: {sms_message.from_}
                        - To: {sms_message.to}
                        - Date Sent: {sms_message.date_sent}
                        """)
                    except Exception as e:
                        st.error(f"Error sending SMS: {str(e)}")
                        
                        # Special handling for trial account limitations
                        if "trial account" in str(e).lower():
                            st.warning("""
                            **Trial Account Limitation:**
                            Twilio trial accounts can only send messages to verified phone numbers.
                            Please verify the recipient number in your Twilio console or upgrade your account.
                            """)
            
            except Exception as e:
                st.error(f"Failed to send test SMS: {str(e)}")

# Instructions for configuring Twilio
with st.expander("How to Configure Twilio", expanded=False):
    st.markdown("""
    ### Setting Up Twilio for SMS Notifications
    
    1. **Create a Twilio Account**:
       - Go to [Twilio's website](https://www.twilio.com/) and sign up for an account
       - Verify your email and phone number
    
    2. **Get Your Credentials**:
       - Once logged in, navigate to the Dashboard
       - Find your Account SID and Auth Token
       - These will be used for the `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` environment variables
    
    3. **Get a Twilio Phone Number**:
       - In the Twilio Console, go to "Phone Numbers" > "Active Numbers"
       - Purchase a new number or use the trial number
       - This number will be used for the `TWILIO_PHONE_NUMBER` environment variable
    
    4. **Set Environment Variables**:
       - Set the following environment variables:
         - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
         - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
         - `TWILIO_PHONE_NUMBER`: Your Twilio phone number (in E.164 format, e.g., +1XXXXXXXXXX)
    
    5. **Trial Account Limitations**:
       - With a trial account, you can only send SMS to verified phone numbers
       - Verify recipient numbers in your Twilio console
       - For production use, upgrade your Twilio account
    """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This diagnostic tool is provided for troubleshooting purposes only.
Standard SMS rates may apply when sending test messages. Always follow Twilio's acceptable use policies.
""")