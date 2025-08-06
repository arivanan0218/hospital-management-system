"""
Manual Email Sender for Existing Google Meet Links
==================================================

Use this to send emails for meetings that have already been created.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv
from database import SessionLocal, Staff, User

load_dotenv()

class ManualEmailSender:
    def __init__(self):
        self.email_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.email_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_from_name = os.getenv("EMAIL_FROM_NAME", "Hospital Management System")
        self.email_from_address = os.getenv("EMAIL_FROM_ADDRESS", self.email_username)
        self.session = SessionLocal()

    def send_meeting_email(self, 
                          google_meet_link: str,
                          meeting_topic: str,
                          meeting_time: str,
                          duration: str = "15 minutes",
                          additional_notes: str = ""):
        """Send email notifications for an existing Google Meet link."""
        
        try:
            # Get all active staff
            staff_members = self.session.query(Staff).join(User).filter(
                User.role.in_(['doctor', 'nurse', 'admin', 'technician'])
            ).all()
            
            print(f"Sending emails for Google Meet: {google_meet_link}")
            print(f"Found {len(staff_members)} staff members to notify")
            
            success_count = 0
            failed_count = 0
            
            for staff in staff_members:
                try:
                    # Create email content
                    msg = MIMEMultipart()
                    msg['From'] = f"{self.email_from_name} <{self.email_from_address}>"
                    msg['To'] = staff.user.email
                    msg['Subject'] = f"URGENT: Hospital Meeting - {meeting_topic}"
                    
                    # Email body
                    body = f"""Dear {staff.user.first_name} {staff.user.last_name},

HOSPITAL MEETING INVITATION

MEETING DETAILS:
• Subject: {meeting_topic}
• Date & Time: {meeting_time}
• Duration: {duration}
• Location: Google Meet Video Conference

GOOGLE MEET VIDEO CONFERENCE (HOSTED BY HOSPITAL):
{google_meet_link}

INSTRUCTIONS: 
• Click the Google Meet link above to join the video meeting
• Please join 5 minutes early
• This meeting is hosted by the Hospital Management System
• You may also receive a Google Calendar invitation

AGENDA:
• Discussion of important topics
• Team updates and coordination
• Q&A session
{additional_notes}

IMPORTANT REMINDERS:
• Have your notes ready
• Ensure stable internet connection for video conference
• If unable to attend, notify your department head immediately

Thank you for your commitment to excellent patient care.

Best regards,
Hospital Management Team

---
For technical support: Contact IT Department
Meeting Link: {google_meet_link}
"""

                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Send email
                    with smtplib.SMTP(self.email_server, self.email_port) as server:
                        server.starttls()
                        server.login(self.email_username, self.email_password)
                        text = msg.as_string()
                        server.sendmail(self.email_from_address, staff.user.email, text)
                    
                    print(f"  ✅ Email sent successfully to: {staff.user.first_name} {staff.user.last_name} ({staff.user.email})")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed to send email to {staff.user.email}: {str(e)}")
                    failed_count += 1
            
            print(f"\nEMAIL SUMMARY:")
            print(f"✅ Successfully sent: {success_count}")
            print(f"❌ Failed to send: {failed_count}")
            print(f"📧 Total attempts: {success_count + failed_count}")
            
            return {
                "success": success_count > 0,
                "total_sent": success_count,
                "total_failed": failed_count,
                "google_meet_link": google_meet_link
            }
            
        except Exception as e:
            print(f"Error in email sending process: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.session.close()

def send_meeting_emails(google_meet_link: str, 
                       meeting_topic: str, 
                       meeting_time: str,
                       duration: str = "15 minutes",
                       additional_notes: str = ""):
    """Quick function to send emails for a Google Meet link."""
    sender = ManualEmailSender()
    return sender.send_meeting_email(
        google_meet_link=google_meet_link,
        meeting_topic=meeting_topic,
        meeting_time=meeting_time,
        duration=duration,
        additional_notes=additional_notes
    )

if __name__ == "__main__":
    # Example usage for your current meeting
    result = send_meeting_emails(
        google_meet_link="https://meet.google.com/koq-xhjf-dkt",
        meeting_topic="AI Development Discussion",
        meeting_time="Tonight at 08:00 PM",
        duration="15 minutes",
        additional_notes="\n• Please bring your development notes\n• We'll discuss AI integration strategies\n• Prepare questions about current projects"
    )
    
    print(f"\nFinal Result: {result}")
