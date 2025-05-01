import os
import datetime  # For datetime operations
import re        # For regular expressions

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def format_phone_number(phone_number):
    """Format the phone number to ensure it has the correct international format."""
    if not phone_number:
        raise ValueError("Phone number cannot be empty")
        
    # Remove any non-digit characters except the plus sign
    digits_only = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # Strip any leading/trailing whitespace
    digits_only = digits_only.strip()
    
    if len(digits_only) < 10:
        raise ValueError("Phone number must be at least 10 digits long")
    
    # If the number already has a plus sign, leave it as is
    if digits_only.startswith("+"):
        return digits_only
        
    # Add India country code (+91) if not present
    if len(digits_only) == 10:  # Standard Indian mobile number
        return f"+91{digits_only}"
    elif digits_only.startswith("91") and len(digits_only) == 12:  # Number with country code but no +
        return f"+{digits_only}"
    elif digits_only.startswith("0"):  # Number with leading 0
        return f"+91{digits_only[1:]}"
    else:  # Any other format
        # Check if it might be an international number without +
        if len(digits_only) > 10:
            return f"+{digits_only}"
        else:
            # Default to adding Indian country code
            return f"+91{digits_only}"

def send_case_update(to_phone_number, case_ref, update_message, notes=None):
    """
    Send an SMS notification about a case update.
    
    Args:
        to_phone_number (str): Recipient's phone number
        case_ref (str): Case reference number or identifier
        update_message (str): Brief update message
        notes (str, optional): Additional notes or scheduling information
    
    Returns:
        dict: Status of the message and message SID if successful
    """
    
    # Message templates for different update types
    templates = {
        "Case Status Change": "🔄 Status Update - {case}: {message}",
        "New Document Filed": "📄 New Filing - {case}: {message}",
        "Court Order Issued": "⚖️ Court Order - {case}: {message}",
        "Hearing Scheduled": "📅 Hearing Alert - {case}: {message}",
        "Case Transferred": "🔁 Transfer Notice - {case}: {message}"
    }
    if not all([to_phone_number, case_ref, date, time, court]):
        return {
            "status": "error",
            "message": "Phone number, case reference, date, time and court location are required"
        }

    try:
        # Format the phone number
        try:
            formatted_number = format_phone_number(to_phone_number)
        except ValueError as ve:
            return {
                "status": "error",
                "message": f"Invalid phone number: {str(ve)}"
            }
        
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if all required credentials are available
        missing_creds = []
        if not account_sid: missing_creds.append("TWILIO_ACCOUNT_SID")
        if not auth_token: missing_creds.append("TWILIO_AUTH_TOKEN")
        if not from_number: missing_creds.append("TWILIO_PHONE_NUMBER")
        
        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing Twilio credentials: {', '.join(missing_creds)}. Please configure these environment variables."
            }
        
        # Create Twilio client
        try:
            client = Client(account_sid, auth_token)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize Twilio client: {str(e)}"
            }
        
        # Validate and parse the message
        if not isinstance(update_message, str):
            return {
                "status": "error",
                "message": "Update message must be a string"
            }
            
        # Parse and format the message
        message_type = None
        message_content = update_message
        
        # Check if message starts with a template type
        for template_type in templates.keys():
            if update_message.startswith(template_type):
                message_type = template_type
                # Extract content after template type, handling both with and without colon
                parts = update_message.split(':', 1)
                if len(parts) > 1:
                    message_content = parts[1].strip()
                break
        
        # Format the message using template if available
        if message_type and message_type in templates:
            message_body = templates[message_type].format(case=case_ref, message=message_content)
        else:
            message_body = f"📢 Case Update - {case_ref}: {message_content}"
        
        # Add message scheduling if specified in notes
        if "SCHEDULE" in str(notes).upper():
            # Extract scheduled time from notes (format: SCHEDULE: YYYY-MM-DD HH:MM)
            try:
                schedule_time = re.search(r'SCHEDULE:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', str(notes))
                if schedule_time:
                    scheduled_time = datetime.strptime(schedule_time.group(1), '%Y-%m-%d %H:%M')
                    message_body += f"\n\nScheduled for: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"
            except Exception as e:
                pass  # Continue without scheduling if format is invalid

        # Validate message length
        if len(message_body) > 1600:  # Twilio's SMS length limit
            return {
                "status": "error",
                "message": "Message is too long. Please shorten the content."
            }

        try:
            # Send the message
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=formatted_number
            )
            
            return {
                "status": "success",
                "message_sid": message.sid,
                "message": f"SMS notification sent successfully to {formatted_number}"
            }
        except TwilioRestException as te:
            error_msg = "Failed to send message: "
            if te.code == 21610:
                error_msg += "Message body is required."
            elif te.code == 21612:
                error_msg += "The 'To' phone number is not a valid mobile number."
            elif te.code == 21408:
                error_msg += "Account doesn't have the permission to send messages to this number."
            else:
                error_msg += str(te)
            return {
                "status": "error",
                "message": error_msg,
                "error_code": te.code
            }
        
    except TwilioRestException as e:
        error_message = "Failed to send SMS notification: "
        if e.code == 20003:
            error_message += "Authentication error. Please check your Twilio credentials."
        elif e.code == 21211:
            error_message += "Invalid phone number format."
        elif e.code == 21608:
            error_message += "Unverified phone number. Please verify the recipient's number in your Twilio console."
        elif e.code == 21614:
            error_message += "Invalid sending phone number. Please check your Twilio phone number configuration."
        else:
            error_message += str(e)
        
        return {
            "status": "error",
            "message": error_message,
            "error_code": e.code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error while sending SMS: {str(e)}"
        }

def send_rights_reminder(to_phone_number, rights_list, notes=None):
    """
    Send an SMS reminder about key legal rights.
    
    Args:
        to_phone_number (str): Recipient's phone number
        rights_list (list): List of key rights to remind about
        notes (str, optional): Additional notes or scheduling information
    
    Returns:
        dict: Status of the message and message SID if successful
    """
    try:
        # Format the phone number
        try:
            formatted_number = format_phone_number(to_phone_number)
        except ValueError as ve:
            return {
                "status": "error",
                "message": f"Invalid phone number: {str(ve)}"
            }

        # Validate required parameters
        if not all([to_phone_number, rights_list]):
            return {
                "status": "error",
                "message": "Phone number and rights list are required"
            }
        
        if not isinstance(rights_list, list) or not rights_list:
            return {
                "status": "error",
                "message": "Rights list must be a non-empty list"
            }

        # Get Twilio credentials
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check for missing credentials
        missing_creds = []
        if not account_sid: missing_creds.append("TWILIO_ACCOUNT_SID")
        if not auth_token: missing_creds.append("TWILIO_AUTH_TOKEN")
        if not from_number: missing_creds.append("TWILIO_PHONE_NUMBER")
        
        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing Twilio credentials: {', '.join(missing_creds)}. Please configure these environment variables."
            }

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Format the message
        message_body = "⚖️ IMPORTANT LEGAL RIGHTS REMINDER ⚖️\n\n"
        for i, right in enumerate(rights_list, 1):
            message_body += f"{i}. {right}\n"

        if notes:
            message_body += f"\nAdditional Notes:\n{notes}"

        # Validate message length
        if len(message_body) > 1600:  # Twilio's SMS length limit
            return {
                "status": "error",
                "message": "Message is too long. Please reduce the number of rights or shorten the notes."
            }

        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_number
        )

        return {
            "status": "success",
            "message_sid": message.sid,
            "message": f"Rights reminder sent successfully to {formatted_number}"
        }

    except TwilioRestException as e:
        error_message = "Failed to send rights reminder: "
        if e.code == 20003:
            error_message += "Authentication error. Please check your Twilio credentials."
        elif e.code == 21211:
            error_message += "Invalid phone number format."
        elif e.code == 21608:
            error_message += "Unverified phone number. Please verify the recipient's number in your Twilio console."
        else:
            error_message += str(e)
        
        return {
            "status": "error",
            "message": error_message,
            "error_code": e.code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error while sending rights reminder: {str(e)}"
        }

    try:
        # Format the phone number
        try:
            formatted_number = format_phone_number(to_phone_number)
        except ValueError as ve:
            return {
                "status": "error",
                "message": f"Invalid phone number: {str(ve)}"
            }
        
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if all required credentials are available
        missing_creds = []
        if not account_sid: missing_creds.append("TWILIO_ACCOUNT_SID")
        if not auth_token: missing_creds.append("TWILIO_AUTH_TOKEN")
        if not from_number: missing_creds.append("TWILIO_PHONE_NUMBER")
        
        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing Twilio credentials: {', '.join(missing_creds)}. Please configure these environment variables."
            }
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Compose the message with key rights
        rights_text = "\n".join([f"• {right}" for right in rights_list[:3]])  # Limit to top 3 for SMS
        message_body = f"Important Legal Rights Reminder:\n{rights_text}"
        
        if len(rights_list) > 3:
            message_body += "\n...and more. Check the app for full details."
        
        # Add message scheduling if specified in notes
        if "SCHEDULE" in str(notes).upper():
            # Extract scheduled time from notes (format: SCHEDULE: YYYY-MM-DD HH:MM)
            try:
                schedule_time = re.search(r'SCHEDULE:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', str(notes))
                if schedule_time:
                    scheduled_time = datetime.strptime(schedule_time.group(1), '%Y-%m-%d %H:%M')
                    message_body += f"\n\nScheduled for: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"
            except Exception as e:
                pass  # Continue without scheduling if format is invalid

        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_number
        )
        
        return {
            "status": "success",
            "message_sid": message.sid,
            "message": f"Rights reminder sent successfully to {formatted_number}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send rights reminder: {str(e)}"
        }

def send_hearing_reminder(to_phone_number, case_ref, date, time, court, notes=None):
    """Send an SMS reminder about an upcoming court hearing.
    
    Args:
        to_phone_number (str): Recipient's phone number
        case_ref (str): Case reference number
        date (str): Date of the hearing
        time (str): Time of the hearing
        court (str): Court location
        notes (str, optional): Additional notes or scheduling information
    
    Returns:
        dict: Status of the message and message SID if successful
    """
    if not all([to_phone_number, case_ref, date, time, court]):
        return {
            "status": "error",
            "message": "Phone number, case reference, date, time and court location are required"
        }

    try:
        # Format the phone number
        try:
            formatted_number = format_phone_number(to_phone_number)
        except ValueError as ve:
            return {
                "status": "error",
                "message": f"Invalid phone number: {str(ve)}"
            }
        
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if all required credentials are available
        missing_creds = []
        if not account_sid: missing_creds.append("TWILIO_ACCOUNT_SID")
        if not auth_token: missing_creds.append("TWILIO_AUTH_TOKEN")
        if not from_number: missing_creds.append("TWILIO_PHONE_NUMBER")
        
        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing Twilio credentials: {', '.join(missing_creds)}. Please configure these environment variables."
            }
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Compose the hearing reminder message
        message_body = f"⚖️ Hearing Reminder - Case {case_ref}\n"
        message_body += f"📅 Date: {date}\n"
        message_body += f"⏰ Time: {time}\n"
        message_body += f"📍 Court: {court}"
        
        if notes:
            message_body += f"\n📝 Notes: {notes}"
        
        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_number
        )
        
        return {
            "status": "success",
            "message_sid": message.sid,
            "message": f"Hearing reminder sent successfully to {formatted_number}"
        }
        
    except TwilioRestException as e:
        error_message = "Failed to send hearing reminder: "
        if e.code == 20003:
            error_message += "Authentication error. Please check your Twilio credentials."
        elif e.code == 21211:
            error_message += "Invalid phone number format."
        elif e.code == 21608:
            error_message += "Unverified phone number. Please verify the recipient's number in your Twilio console."
        elif e.code == 21614:
            error_message += "Invalid sending phone number. Please check your Twilio phone number configuration."
        else:
            error_message += str(e)
        
        return {
            "status": "error",
            "message": error_message,
            "error_code": e.code
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error while sending hearing reminder: {str(e)}"
        }
    
    # Message templates for different hearing types
    templates = {
        "Regular Hearing": "⚖️ HEARING REMINDER\n📋 Case: {case}\n📅 Date: {date}\n⏰ Time: {time}\n🏛️ Court: {court}",
        "Urgent Hearing": "🚨 URGENT HEARING\n📋 Case: {case}\n📅 Date: {date}\n⏰ Time: {time}\n🏛️ Court: {court}",
        "Final Hearing": "⚖️ FINAL HEARING\n📋 Case: {case}\n📅 Date: {date}\n⏰ Time: {time}\n🏛️ Court: {court}"
    }
    if not all([to_phone_number, case_ref, date, time, court]):
        return {
            "status": "error",
            "message": "Phone number, case reference, date, time and court location are required"
        }

    try:
        # Format the phone number
        try:
            formatted_number = format_phone_number(to_phone_number)
        except ValueError as ve:
            return {
                "status": "error",
                "message": f"Invalid phone number: {str(ve)}"
            }
        
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Check if all required credentials are available
        missing_creds = []
        if not account_sid: missing_creds.append("TWILIO_ACCOUNT_SID")
        if not auth_token: missing_creds.append("TWILIO_AUTH_TOKEN")
        if not from_number: missing_creds.append("TWILIO_PHONE_NUMBER")
        
        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing Twilio credentials: {', '.join(missing_creds)}. Please configure these environment variables."
            }
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Use appropriate template based on hearing type
        hearing_type = "Regular Hearing"  # Default type
        if "URGENT" in str(notes).upper():
            hearing_type = "Urgent Hearing"
        elif "FINAL" in str(notes).upper():
            hearing_type = "Final Hearing"
            
        message_body = templates[hearing_type].format(
            case=case_ref,
            date=date,
            time=time,
            court=court
        )
        
        if notes:
            message_body += f"\nNotes: {notes}"
            
        message_body += "\nPlease arrive 30 minutes early."
        
        # Add message scheduling if specified in notes
        if "SCHEDULE" in str(notes).upper():
            # Extract scheduled time from notes (format: SCHEDULE: YYYY-MM-DD HH:MM)
            try:
                schedule_time = re.search(r'SCHEDULE:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', str(notes))
                if schedule_time:
                    scheduled_time = datetime.strptime(schedule_time.group(1), '%Y-%m-%d %H:%M')
                    message_body += f"\n\nScheduled for: {scheduled_time.strftime('%B %d, %Y at %I:%M %p')}"
            except Exception as e:
                pass  # Continue without scheduling if format is invalid

        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_number
        )
        
        return {
            "status": "success",
            "message_sid": message.sid,
            "message": f"Hearing reminder sent successfully to {formatted_number}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send hearing reminder: {str(e)}"
        }

def check_twilio_credentials():
    """
    Check if Twilio credentials are properly configured.
    
    Returns:
        bool: True if all required credentials are available, False otherwise
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    
    return all([account_sid, auth_token, from_number])