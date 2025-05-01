import os
from twilio.rest import Client
import streamlit as st

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

# Create a Streamlit page to display test results
def show_test_page():
    st.title("Twilio SMS Setup Test")
    
    st.markdown("""
    This page tests your Twilio setup to diagnose SMS sending issues.
    """)
    
    if st.button("Run Twilio Diagnostics", use_container_width=True):
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
                    """)
            else:
                st.markdown("""
                - Your Twilio setup appears to be working correctly
                - If you're still having issues sending SMS, check the following:
                  - Recipient phone numbers are formatted correctly
                  - Your Twilio account has sufficient credits or is set up for billing
                  - The message content doesn't violate Twilio's policies
                """)
    
    st.markdown("---")
    
    # Navigation button to go back
    if st.button("Back to Notifications", use_container_width=True):
        st.switch_page("pages/notifications.py")

if __name__ == "__main__":
    show_test_page()