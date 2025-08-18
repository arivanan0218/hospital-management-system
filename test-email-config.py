#!/usr/bin/env python3
"""
Test script to verify email configuration works
Run this to test if email sending is working correctly
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def test_email_configuration():
    """Test the email configuration and send a test email"""
    
    print("Testing Email Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get email configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    email_username = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    from_email = os.getenv('EMAIL_FROM_ADDRESS', email_username)
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Email Username: {email_username}")
    print(f"From Email: {from_email}")
    print(f"Password Set: {'Yes' if email_password else 'No'}")
    print()
    
    # Check if credentials are available
    if not email_username or not email_password:
        print("❌ Error: Email credentials not configured!")
        print("Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables.")
        return False
    
    # Create test email
    test_subject = "Hospital Management System - Email Test"
    test_message = """
This is a test email from the Hospital Management System.

If you receive this email, the email configuration is working correctly!

Timestamp: """ + str(os.popen('date').read().strip()) + """
Environment: Testing
Server: """ + smtp_server + """:" + str(smtp_port) + """

Best regards,
Hospital Management System
"""
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"Hospital Management System <{from_email}>"
        msg['To'] = email_username  # Send test email to yourself
        msg['Subject'] = test_subject
        msg.attach(MIMEText(test_message, 'plain'))
        
        print("Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("Starting TLS encryption...")
            server.starttls()
            
            print("Logging in...")
            server.login(email_username, email_password)
            
            print("Sending test email...")
            server.send_message(msg)
        
        print()
        print("✅ SUCCESS: Test email sent successfully!")
        print(f"Check your inbox at: {email_username}")
        return True
        
    except Exception as e:
        print()
        print("❌ ERROR: Failed to send test email!")
        print(f"Error details: {str(e)}")
        print()
        print("Common issues:")
        print("1. Gmail App Password not set correctly")
        print("2. Less secure app access disabled")
        print("3. 2-Factor Authentication not enabled")
        print("4. Network/firewall blocking SMTP")
        return False

if __name__ == "__main__":
    success = test_email_configuration()
    sys.exit(0 if success else 1)
