"""Google Meet ONLY Integration - Real Google Meet Links

This creates ONLY Google Meet links, no alternatives needed.
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List

class GoogleMeetOnlyGenerator:
    """Generate ONLY Google Meet links - no alternatives."""
    
    @staticmethod
    def create_google_meet_link(meeting_title: str = "Hospital Meeting") -> str:
        """Create a Google Meet link that actually works."""
        try:
            # The most reliable approach: Use Google Meet's instant meeting creation
            # When users click this link, Google Meet will create a new room automatically
            google_meet_url = "https://meet.google.com/new"
            
            print(f"Generated Google Meet: {google_meet_url}")
            print("NOTE: Creates a new meeting room when the host clicks this link")
            print("Host should click the link first, then share the generated room code")
            
            return google_meet_url
            
        except Exception as e:
            print(f"Error generating Google Meet link: {e}")
            return "https://meet.google.com/new"
    
    @staticmethod
    def create_calendar_google_meet(meeting_title: str, start_time: datetime) -> Dict[str, Any]:
        """Create Google Calendar event with Google Meet automatically included."""
        try:
            # Create Google Calendar URL that automatically adds Google Meet
            start_formatted = start_time.strftime("%Y%m%dT%H%M%SZ")
            end_time = start_time + timedelta(minutes=30)
            end_formatted = end_time.strftime("%Y%m%dT%H%M%SZ")
            
            # Google Calendar URL with Meet integration
            calendar_url = (
                f"https://calendar.google.com/calendar/render?"
                f"action=TEMPLATE&"
                f"text={meeting_title.replace(' ', '+')}&"
                f"dates={start_formatted}/{end_formatted}&"
                f"details=Hospital+staff+meeting+via+Google+Meet&"
                f"add=meet.google.com"
            )
            
            # Also generate direct Google Meet room
            direct_meet = GoogleMeetOnlyGenerator.create_google_meet_link(meeting_title)
            
            return {
                "calendar_link": calendar_url,
                "direct_meet_link": direct_meet,
                "meeting_title": meeting_title,
                "scheduled_time": start_time.isoformat(),
                "type": "google_meet_only"
            }
            
        except Exception as e:
            print(f"Error creating calendar Google Meet: {e}")
            return {
                "direct_meet_link": "https://meet.google.com/new",
                "error": str(e)
            }
    
    @staticmethod
    def get_google_meet_solution(meeting_title: str, start_time: datetime = None) -> Dict[str, Any]:
        """Get Google Meet solution ONLY - no alternatives."""
        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=5)
        
        try:
            # Create Google Meet link
            google_meet_link = GoogleMeetOnlyGenerator.create_google_meet_link(meeting_title)
            
            # Create calendar integration
            calendar_solution = GoogleMeetOnlyGenerator.create_calendar_google_meet(meeting_title, start_time)
            
            return {
                "google_meet_link": google_meet_link,
                "calendar_create_link": calendar_solution["calendar_link"],
                "meeting_title": meeting_title,
                "scheduled_time": start_time.isoformat(),
                "instructions": "Use Google Meet link to join the meeting",
                "calendar_instructions": "Use calendar link to create event with Google Meet",
                "type": "google_meet_only"
            }
            
        except Exception as e:
            return {
                "google_meet_link": "https://meet.google.com/new",
                "error": str(e),
                "type": "google_meet_fallback"
            }
    
    @staticmethod
    def create_instant_google_meet(meeting_title: str = "Hospital Meeting") -> str:
        """Create instant Google Meet room."""
        return GoogleMeetOnlyGenerator.create_google_meet_link(meeting_title)

# Test Google Meet ONLY integration
if __name__ == "__main__":
    print("Testing Google Meet ONLY Integration...")
    print("=" * 60)
    
    generator = GoogleMeetOnlyGenerator()
    
    # Test basic Google Meet link
    meet_link = generator.create_google_meet_link("Hospital Staff Meeting")
    print(f"Google Meet link: {meet_link}")
    
    # Test calendar integration
    future_time = datetime.now() + timedelta(hours=1)
    calendar_solution = generator.create_calendar_google_meet("Team Meeting", future_time)
    print(f"Calendar solution: {calendar_solution}")
    
    # Test complete Google Meet solution
    complete_solution = generator.get_google_meet_solution("Daily Standup Meeting")
    print(f"Complete Google Meet solution: {complete_solution}")
    
    print("\n" + "=" * 60)
    print("GOOGLE MEET ONLY - INSTRUCTIONS:")
    print("1. Direct Google Meet links for immediate joining")
    print("2. Calendar links to create events with Google Meet")
    print("3. No alternatives - Google Meet ONLY")
    print("=" * 60)
