"""Test email functionality."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def test_email():
    """Test email sending functionality."""
    load_dotenv()
    
    # Get email configuration
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_from_name = os.getenv("EMAIL_FROM_NAME", "Hospital Management System")
    email_from_address = os.getenv("EMAIL_FROM_ADDRESS", email_username)
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Email Username: {email_username}")
    print(f"Email Password: {'*' * len(email_password) if email_password else 'None'}")
    print(f"From Name: {email_from_name}")
    print(f"From Address: {email_from_address}")
    
    if not email_username or not email_password:
        print("ERROR: Email username or password not configured!")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = f"{email_from_name} <{email_from_address}>"
        msg['To'] = email_username  # Send to self for testing
        msg['Subject'] = "Test Email from Hospital Management System"
        
        body = """
        This is a test email from the Hospital Management System.
        
        If you receive this email, the email configuration is working correctly.
        
        Best regards,
        Hospital Management System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        print("Starting TLS...")
        
        print("Logging in...")
        server.login(email_username, email_password)
        
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(email_from_address, email_username, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    test_email()
