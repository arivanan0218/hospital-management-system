"""Meeting Scheduler Agent for Hospital Management System."""

import uuid
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import and_, or_
from database import Staff, Appointment, User, Department, SessionLocal
from staff_meetings import StaffMeeting, staff_meeting_participants
from google_meet_api import GoogleMeetAPIIntegration
from meeting_management import MeetingManager, Meeting, MeetingParticipant
import os
from dotenv import load_dotenv
import re

load_dotenv()

class MeetingSchedulerAgent:
    def __init__(self):
        self.session = SessionLocal()
        self.email_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.email_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_from_name = os.getenv("EMAIL_FROM_NAME", "Hospital Management System")
        self.email_from_address = os.getenv("EMAIL_FROM_ADDRESS", self.email_username)
        # Using REAL Google Meet API integration with your Google account as host
        self.meeting_manager = MeetingManager()

    def parse_duration(self, query: str) -> tuple:
        """Parse duration from query string and return (minutes, duration_string)."""
        try:
            query_lower = query.lower()
            
            # Enhanced duration patterns
            duration_patterns = [
                r'(\d+)\s*(?:hours?|hrs?|h)\s*(?:and\s*)?(\d+)?\s*(?:minutes?|mins?|m)?',  # 1 hour 30 minutes
                r'(\d+)\s*(?:minutes?|mins?|m)(?:\s|$)',  # 15 minutes, 30 mins
                r'(\d+)\s*(?:hours?|hrs?|h)(?:\s|$)',     # 1 hour, 2 hrs
                r'for\s+(\d+)\s*(?:minutes?|mins?|m)',    # for 15 minutes
                r'for\s+(\d+)\s*(?:hours?|hrs?|h)',       # for 1 hour
                r'(\d+)min(?:\s|$)',                       # 15min
                r'(\d+)hr(?:\s|$)',                        # 1hr
                r'(\d+)h(?:\s|$)',                         # 1h
            ]
            
            total_minutes = 0
            duration_string = ""
            
            for pattern in duration_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    print(f"Found duration pattern: {pattern} -> {match.groups()}")
                    
                    if 'hour' in pattern or 'hr' in pattern or 'h' in pattern:
                        # Hour patterns
                        hours = int(match.group(1))
                        minutes = 0
                        if len(match.groups()) > 1 and match.group(2):
                            minutes = int(match.group(2))
                        
                        total_minutes = hours * 60 + minutes
                        
                        if minutes > 0:
                            duration_string = f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
                        else:
                            duration_string = f"{hours} hour{'s' if hours > 1 else ''}"
                            
                    else:
                        # Minute patterns
                        total_minutes = int(match.group(1))
                        duration_string = f"{total_minutes} minute{'s' if total_minutes != 1 else ''}"
                    
                    print(f"Parsed duration: {total_minutes} minutes -> '{duration_string}'")
                    return total_minutes, duration_string
            
            # Check for common duration keywords
            if '15min' in query_lower or 'fifteen min' in query_lower:
                return 15, "15 minutes"
            elif '30min' in query_lower or 'thirty min' in query_lower or 'half hour' in query_lower:
                return 30, "30 minutes"
            elif '45min' in query_lower or 'forty-five min' in query_lower:
                return 45, "45 minutes"
            elif '1hr' in query_lower or 'one hour' in query_lower:
                return 60, "1 hour"
            elif '90min' in query_lower or 'hour and half' in query_lower:
                return 90, "1 hour 30 minutes"
            elif '2hr' in query_lower or 'two hour' in query_lower:
                return 120, "2 hours"
            
            # Default duration
            print("No duration found in query, using default 15 minutes")
            return 15, "15 minutes"
            
        except Exception as e:
            print(f"Error parsing duration: {e}")
            return 15, "15 minutes"

    def extract_participants_from_query(self, query: str) -> List[str]:
        """Extract specific participant names from the query."""
        try:
            query_lower = query.lower()
            
            # Check for "all staff" or similar patterns first
            all_staff_patterns = [
                r'all\s+(?:the\s+)?staff',
                r'all\s+(?:the\s+)?staffs',
                r'all\s+hospital\s+staff',
                r'everyone',
                r'all\s+(?:hospital\s+)?employees',
                r'all\s+(?:team\s+)?members',
                r'entire\s+staff',
                r'whole\s+team'
            ]
            
            for pattern in all_staff_patterns:
                if re.search(pattern, query_lower):
                    print("Detected 'all staff' request - will get all active staff members")
                    # Return a special marker to indicate "all staff" request
                    return ["ALL_STAFF_REQUEST"]
            
            # Common patterns to find participant names
            participant_patterns = [
                r'between\s+(\w+)\s+and\s+(\w+)',  # "between shamil and nazif"
                r'with\s+(\w+)\s+and\s+(\w+)',     # "with shamil and nazif"
                r'(\w+)\s+and\s+(\w+)\s+meeting',  # "shamil and nazif meeting"
                r'meeting.*?with\s+(\w+)(?:\s+and\s+(\w+))?',  # "meeting with shamil and nazif"
                r'schedule.*?(\w+)\s+and\s+(\w+)',  # "schedule shamil and nazif"
            ]
            
            participant_names = []
            
            for pattern in participant_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Add all captured groups (participant names)
                    for i in range(1, len(match.groups()) + 1):
                        if match.group(i):
                            name = match.group(i).strip().title()
                            if name and len(name) > 1:
                                participant_names.append(name)
                    break
            
            # Also check for individual mentions
            if not participant_names:
                # Look for common names patterns
                name_pattern = r'\b(shamil|nazif|mohamed|sarah|johnson|smith|brown|davis|wilson|miller|moore|taylor|anderson|thomas|jackson|white|harris|martin|thompson|garcia|martinez|robinson|clark|rodriguez|lewis|lee|walker|hall|allen|young|hernandez|king|wright|lopez|hill|scott|green|adams|baker|gonzalez|nelson|carter|mitchell|perez|roberts|turner|phillips|campbell|parker|evans|edwards|collins|stewart|sanchez|morris|rogers|reed|cook|morgan|bell|murphy|bailey|rivera|cooper|richardson|cox|howard|ward|torres|peterson|gray|ramirez|james|watson|brooks|kelly|sanders|price|bennett|wood|barnes|ross|henderson|coleman|jenkins|perry|powell|long|patterson|hughes|flores|washington|butler|simmons|foster|gonzales|bryant|alexander|russell|griffin|diaz|hayes)\b'
                
                matches = re.findall(name_pattern, query_lower)
                participant_names = [name.title() for name in set(matches)]
            
            print(f"Extracted participants from query: {participant_names}")
            return participant_names
            
        except Exception as e:
            print(f"Error extracting participants: {e}")
            return []

    def find_staff_by_names(self, participant_names: List[str]) -> List[str]:
        """Find staff IDs by matching names from the query."""
        try:
            staff_ids = []
            
            # Check for "all staff" request first
            if participant_names == ["ALL_STAFF_REQUEST"]:
                print("Processing 'all staff' request - getting all active staff members")
                all_staff = self.session.query(Staff).filter(
                    Staff.status == 'active'
                ).all()
                staff_ids = [str(staff.id) for staff in all_staff]
                print(f"Found {len(staff_ids)} active staff members for meeting")
                return staff_ids
            
            for name in participant_names:
                # Search for staff by first name or last name (case-insensitive)
                staff = self.session.query(Staff).join(User).filter(
                    or_(
                        User.first_name.ilike(f'%{name}%'),
                        User.last_name.ilike(f'%{name}%')
                    ),
                    Staff.status == 'active'
                ).first()
                
                if staff:
                    staff_ids.append(str(staff.id))
                    print(f"Found staff: {name} -> {staff.user.first_name} {staff.user.last_name} (ID: {staff.id})")
                else:
                    print(f"Warning: Could not find staff member with name: {name}")
            
            # If no specific participants found, fall back to getting available staff
            if not staff_ids:
                print("No specific participants found, getting available staff as fallback")
                fallback_staff = self.session.query(Staff).filter(
                    Staff.status == 'active'
                ).limit(10).all()  # Get up to 10 staff members as fallback instead of just 2
                staff_ids = [str(staff.id) for staff in fallback_staff]
                print(f"Using fallback: found {len(staff_ids)} active staff members")
            
            return staff_ids
            
        except Exception as e:
            print(f"Error finding staff by names: {e}")
            return []

    def extract_meeting_title(self, query: str) -> str:
        """Extract meeting title from query."""
        try:
            # Enhanced patterns to extract meeting topic - prioritize actual topic words over dates/names
            patterns = [
                r'meeting.*?(?:about|regarding)\s+([a-zA-Z][a-zA-Z\s]+?)\s+(?:between|with|at|tomorrow|today|on\s+\d)',  # "meeting about daily improvement between"
                r'(?:about|regarding)\s+([a-zA-Z][a-zA-Z\s]+?)\s+meeting',  # "about daily improvement meeting"  
                r'schedule.*?meeting.*?(?:about|regarding)\s+([a-zA-Z][a-zA-Z\s]+?)\s+(?:between|with|at|tomorrow|today)',  # "schedule meeting about daily improvement"
                r'schedule.*?([a-zA-Z][a-zA-Z\s]+?)\s+meeting.*?(?:between|with)',  # "schedule daily improvement meeting between"
                r'meeting.*?(?:on|for)\s+([a-zA-Z][a-zA-Z\s]+?)\s+(?:between|with|at|tomorrow|today)',  # "meeting for daily improvement between"
                r'(?:meeting|discussion).*?(?:about|on|for|regarding)\s+([a-zA-Z][a-zA-Z\s]+?)(?:\s+between|\s+with|\s+at|\s+for|\s+tomorrow|\s+today|$)',  # various patterns
            ]
            
            query_lower = query.lower()
            
            for pattern in patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    topic = match.group(1).strip()
                    
                    # Skip if topic is just a date, number, or single character
                    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', topic) or re.match(r'^\d+$', topic) or len(topic) < 3:
                        continue
                        
                    # Clean up the topic
                    topic = re.sub(r'\s+', ' ', topic)  # Remove extra spaces
                    topic = topic.replace(' and ', ' & ')  # Make it more concise
                    
                    # Remove common filler words but keep meaningful content
                    filler_words = ['the', 'a', 'an', 'to', 'of', 'in', 'at', 'on', 'for']
                    topic_words = [word for word in topic.split() if word not in filler_words and not re.match(r'^\d{4}', word)]
                    
                    if not topic_words:  # If all words were filtered out, continue to next pattern
                        continue
                        
                    topic = ' '.join(topic_words)
                    
                    # Capitalize properly
                    words = topic.split()
                    capitalized_words = []
                    for word in words:
                        if word.lower() in ['ai', 'it', 'er', 'icu', 'hr', 'qa', 'qr', 'ui', 'ux']:
                            capitalized_words.append(word.upper())
                        elif len(word) > 1:
                            capitalized_words.append(word.capitalize())
                        else:
                            capitalized_words.append(word.lower())
                    
                    title = ' '.join(capitalized_words)
                    if len(title) > 3:  # Make sure we got something meaningful
                        print(f"Extracted meeting topic: '{title}' from pattern: {pattern}")
                        return f"{title} Meeting"
            
            # Fallback: try to extract any meaningful words (excluding names, dates, and common words)
            meaningful_words = []
            words = query_lower.split()
            skip_words = {
                'schedule', 'meeting', 'at', 'for', 'on', 'about', 'regarding', 'tomorrow', 'today', 
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'between', 'specifically',
                'shamil', 'nazif', 'mohamed', 'sarah', 'johnson', 'smith', 'discuss', 'to'
            }
            
            for word in words:
                # Skip dates, times, numbers, and common words
                if (word not in skip_words and len(word) > 2 and 
                    not re.match(r'^\d+$', word) and 
                    not re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', word) and
                    not re.match(r'^\d{1,2}:\d{2}$', word) and
                    not word.endswith('pm') and not word.endswith('am')):
                    
                    if word == 'ai':
                        meaningful_words.append('AI')
                    elif word == 'improvement' or word == 'improvements':
                        meaningful_words.append('Improvement')
                    elif word == 'daily':
                        meaningful_words.append('Daily')
                    elif len(word) > 2:
                        meaningful_words.append(word.capitalize())
            
            if meaningful_words:
                title = ' '.join(meaningful_words[:3])  # Limit to 3 words
                print(f"Fallback meeting topic: '{title}'")
                return f"{title} Meeting"
            
            return "Hospital Staff Meeting"
            
        except Exception as e:
            print(f"Error extracting meeting title: {e}")
            return "Hospital Staff Meeting"

    def parse_meeting_datetime(self, query: str) -> datetime:
        """Parse complete meeting date and time from query string with enhanced NLP."""
        import calendar
        
        try:
            current_date = datetime.now()
            query_lower = query.lower()
            
            print(f"Parsing datetime from: {query}")
            
            # Enhanced date patterns including more flexible formats
            date_patterns = [
                # YYYY-MM-DD format
                r'(\d{4}-\d{1,2}-\d{1,2})',
                # YYYY/MM/DD format  
                r'(\d{4}/\d{1,2}/\d{1,2})',
                # Month DD, YYYY or Month DDth YYYY
                r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
                # MM/DD/YYYY or DD/MM/YYYY
                r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                # August 10th, August 10, etc.
                r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?)',
            ]
            
            # Enhanced time patterns - more flexible
            time_patterns = [
                r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',  # 2pm, 10:30am
                r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',  # at 2pm
                r'(\d{1,2})\s*(?::|\.)\s*(\d{2})\s*(am|pm)',  # 2.30 pm, 2:30 pm
                r'(\d{1,2})\s*(am|pm)',  # 2 pm (space)
                r'(\d{1,2})(?:\s*)(o\'clock)',  # 2 o'clock
            ]
            
            # Try to extract time
            time_match = None
            time_str = None
            hours = None
            minutes = 0
            period = None
            
            for pattern in time_patterns:
                time_match = re.search(pattern, query, re.IGNORECASE)
                if time_match:
                    time_str = time_match.group(1) if len(time_match.groups()) == 1 else time_match.group(0)
                    print(f"Found time pattern: {pattern} -> {time_str}")
                    break
            
            # If no explicit time found, try to infer from context
            if not time_match:
                # Check for time context clues
                if any(word in query_lower for word in ['morning', 'am', 'early']):
                    hours = 9
                    period = 'am'
                    print("Inferred morning time: 9:00 AM")
                elif any(word in query_lower for word in ['afternoon', 'pm', 'evening']):
                    hours = 2
                    period = 'pm' 
                    print("Inferred afternoon time: 2:00 PM")
                elif any(word in query_lower for word in ['night', 'late']):
                    hours = 7
                    period = 'pm'
                    print("Inferred evening time: 7:00 PM")
                else:
                    # Default to next available business hour
                    current_hour = current_date.hour
                    if current_hour < 8:
                        hours = 9
                        period = 'am'
                    elif current_hour < 17:
                        hours = current_hour + 1
                        period = 'pm' if hours > 12 else 'am'
                    else:
                        hours = 9
                        period = 'am'
                        current_date = current_date + timedelta(days=1)
                    print(f"Default business hour: {hours}:00 {period}")
            else:
                # Parse the found time
                if 'o\'clock' in time_str.lower():
                    hours_match = re.search(r'(\d{1,2})', time_str)
                    if hours_match:
                        hours = int(hours_match.group(1))
                        period = 'am' if hours <= 11 else 'pm'
                else:
                    time_pattern = re.compile(r'(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)', re.IGNORECASE)
                    time_match_obj = time_pattern.search(time_str)
                    
                    if time_match_obj:
                        hours = int(time_match_obj.group(1))
                        minutes = int(time_match_obj.group(2)) if time_match_obj.group(2) else 0
                        period = time_match_obj.group(3).lower()
            
            if hours is None:
                # Last resort: default to 2 PM
                hours = 2
                minutes = 0
                period = 'pm'
                print("Using default time: 2:00 PM")
            
            # Convert to 24-hour format
            if period == 'pm' and hours < 12:
                hours += 12
            elif period == 'am' and hours == 12:
                hours = 0
            
            # Try to find a date in the query
            target_date = None
            
            # Check for relative dates first (higher priority)
            if 'tomorrow' in query_lower:
                target_date = current_date.date() + timedelta(days=1)
                print("Found relative date: tomorrow")
            elif 'today' in query_lower:
                target_date = current_date.date()
                print("Found relative date: today")
            elif any(day in query_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                # Handle day names
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    if day in query_lower:
                        today_weekday = current_date.weekday()
                        target_weekday = days.index(day)
                        days_ahead = (target_weekday - today_weekday) % 7
                        if days_ahead == 0:  # Same day
                            if current_date.hour >= hours:  # Time has passed, next week
                                days_ahead = 7
                        target_date = current_date.date() + timedelta(days=days_ahead)
                        print(f"Found weekday: {day} -> {target_date}")
                        break
            elif 'next week' in query_lower:
                target_date = current_date.date() + timedelta(days=7)
                print("Found relative date: next week")
            else:
                # Try explicit date patterns
                for pattern in date_patterns:
                    match = re.search(pattern, query_lower, re.IGNORECASE)
                    if match:
                        date_str = match.group(1)
                        target_date = self.parse_date_string(date_str)
                        print(f"Found explicit date: {date_str} -> {target_date}")
                        break
            
            # If no date found, determine based on time and current time
            if target_date is None:
                proposed_time = current_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if proposed_time <= current_date:
                    # Time has passed today, schedule for tomorrow
                    target_date = current_date.date() + timedelta(days=1)
                    print(f"Time {hours}:{minutes:02d} has passed today, scheduling for tomorrow")
                else:
                    # Time hasn't passed yet, schedule for today
                    target_date = current_date.date()
                    print(f"Time {hours}:{minutes:02d} is still available today")
            
            # Combine date and time
            meeting_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=hours, minute=minutes))
            
            print(f"Final parsed meeting datetime: {meeting_datetime.strftime('%Y-%m-%d %H:%M')}")
            return meeting_datetime
            
        except Exception as e:
            # Provide more helpful error message
            error_msg = f"Failed to parse meeting datetime from '{query}': {str(e)}"
            print(f"ERROR: {error_msg}")
            
            # Try to provide suggestions
            suggestions = []
            if not re.search(r'\d{1,2}(?::\d{2})?\s*(?:am|pm)', query, re.IGNORECASE):
                suggestions.append("Include a time like '2pm', '10:30am', or '3:00 PM'")
            
            if not any(word in query.lower() for word in ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', '2025']):
                suggestions.append("Include a date like 'tomorrow', 'Monday', or '2025/08/10'")
                
            if suggestions:
                error_msg += f". Suggestions: {'; '.join(suggestions)}"
            
            raise ValueError(error_msg)
    
    def parse_date_string(self, date_str: str) -> date:
        """Parse various date string formats into date object."""
        from dateutil.parser import parse
        import calendar
        
        try:
            date_str = date_str.strip()
            current_year = datetime.now().year
            
            # Handle YYYY-MM-DD format
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Handle YYYY/MM/DD format
            if re.match(r'\d{4}/\d{1,2}/\d{1,2}', date_str):
                return datetime.strptime(date_str, '%Y/%m/%d').date()
            
            # Handle month names (e.g., "August 10", "August 10th", "August 10, 2025")
            month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?'
            match = re.match(month_pattern, date_str.lower())
            if match:
                month_name = match.group(1)
                day = int(match.group(2))
                year = int(match.group(3)) if match.group(3) else current_year
                
                month_num = {
                    'january': 1, 'february': 2, 'march': 3, 'april': 4,
                    'may': 5, 'june': 6, 'july': 7, 'august': 8,
                    'september': 9, 'october': 10, 'november': 11, 'december': 12
                }[month_name]
                
                return date(year, month_num, day)
            
            # Fallback: use dateutil parser
            parsed_date = parse(date_str, default=datetime(current_year, 1, 1))
            return parsed_date.date()
            
        except Exception as e:
            print(f"Warning: Could not parse date '{date_str}': {e}")
            return datetime.now().date()

    def parse_meeting_time(self, time_str: str) -> datetime:
        """Legacy method - redirects to parse_meeting_datetime."""
        # For backward compatibility, create a simple query with just the time
        query = f"meeting at {time_str}"
        return self.parse_meeting_datetime(query)

    def parse_department_id(self, query: str) -> Optional[str]:
        """Extract department ID from query if present."""
        match = re.search(r'department_id: ([0-9a-f-]+)', query)
        if match:
            return match.group(1)
        
        # Try to match department name
        if "cardiology" in query.lower():
            dept = self.session.query(Department).filter(Department.name == "Cardiology").first()
            return str(dept.id) if dept else None
        elif "emergency" in query.lower():
            dept = self.session.query(Department).filter(Department.name == "Emergency").first()
            return str(dept.id) if dept else None
        
        return None

    def get_available_staff(self, department_id: str = None, roles: List[str] = None) -> List[Staff]:
        """Get available staff members based on department and roles."""
        query = self.session.query(Staff).join(User)
        
        if department_id:
            query = query.filter(Staff.department_id == uuid.UUID(department_id))
        if roles:
            query = query.filter(User.role.in_(roles))
            
        return query.all()

    def check_availability(self, staff_ids: List[str], proposed_time: datetime, duration_minutes: int = 15) -> bool:
        """Check if all staff members are available at the proposed time."""
        end_time = proposed_time + timedelta(minutes=duration_minutes)  # Use dynamic duration
        
        for staff_id in staff_ids:
            # Check for existing appointments
            # Get appointments that might conflict
            appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == uuid.UUID(staff_id),
                Appointment.appointment_date <= end_time,
                Appointment.appointment_date >= proposed_time
            ).all()
            
            # Check each appointment for overlap
            conflicts = 0
            for appt in appointments:
                appt_end = appt.appointment_date + timedelta(minutes=30)  # Assume 30 min for existing appointments
                if appt.appointment_date < end_time and appt_end > proposed_time:
                    conflicts += 1
            
            if conflicts > 0:
                return False
        return True

    def find_next_available_slot(self, staff_ids: List[str], earliest_time: datetime, latest_time: datetime) -> Optional[datetime]:
        """Find the next available time slot for all participants."""
        current_time = earliest_time
        while current_time <= latest_time:
            if self.check_availability(staff_ids, current_time):
                return current_time
            current_time += timedelta(minutes=30)
        return None

    def send_meeting_notifications(self, staff_ids: List[str], meeting_time: datetime, subject: str, location: str, meet_link: str = None, duration_string: str = "15 minutes", meeting_title: str = None) -> Dict[str, Any]:
        """Send meeting notifications to all participants."""
        try:
            if not self.email_username or not self.email_password:
                print("ERROR: Email configuration missing. Set EMAIL_USERNAME and EMAIL_PASSWORD in .env")
                return {"success": False, "emails_sent": 0, "message": "Email configuration missing"}

            print(f"Attempting to send emails to {len(staff_ids)} staff members...")
            
            server = smtplib.SMTP(self.email_server, self.email_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            emails_sent = 0
            failed_emails = []
            
            for staff_id in staff_ids:
                try:
                    staff = self.session.query(Staff).join(User).filter(Staff.id == uuid.UUID(staff_id)).first()
                    if staff and staff.user.email:
                        print(f"  Sending email to: {staff.user.first_name} {staff.user.last_name} ({staff.user.email})")
                        
                        # Create proper email subject (clean and professional)
                        title_to_use = meeting_title or subject  # Use meeting_title if provided, otherwise fallback to subject
                        
                        if "daily improvement" in title_to_use.lower() or "improvement" in title_to_use.lower():
                            email_subject = f"🏥 {title_to_use} - {meeting_time.strftime('%B %d, %Y')}"
                        elif "meeting" not in title_to_use.lower():
                            email_subject = f"🏥 {title_to_use} Meeting - {meeting_time.strftime('%B %d, %Y')}"
                        else:
                            email_subject = f"🏥 {title_to_use} - {meeting_time.strftime('%B %d, %Y')}"
                        
                        # Remove "Hospital Meeting -" prefix if present to avoid redundancy
                        email_subject = email_subject.replace("🏥 Hospital Meeting - ", "🏥 ")
                        
                        print(f"Email subject created: {email_subject}")
                        
                        msg = MIMEMultipart()
                        msg['From'] = f"{self.email_from_name} <{self.email_from_address}>"
                        msg['To'] = staff.user.email
                        msg['Subject'] = email_subject

                        # Create meeting link section
                        meet_section = ""
                        if meet_link:
                            meet_section = f"""
🔗 JOIN ONLINE MEETING:
{meet_link}

📝 MEETING ACCESS:
• Click the Google Meet link above to join
• Meeting hosted by Hospital Management System
• Google Calendar invitation will be sent separately
• Join 5 minutes early for best experience

"""
                        else:
                            meet_section = f"📍 LOCATION: {location}\n"

                        # Create clean meeting topic for email body (remove "Meeting" suffix if present)
                        meeting_topic = title_to_use.replace(" Meeting", "") if title_to_use.endswith(" Meeting") else title_to_use
                        meeting_topic = meeting_topic.replace("Hospital Meeting - ", "")  # Remove prefix
                        
                        print(f"Meeting topic for email body: {meeting_topic}")

                        body = f"""Dear {staff.user.first_name} {staff.user.last_name},

🏥 HOSPITAL STAFF MEETING INVITATION

📋 MEETING DETAILS:
• Topic: {meeting_topic}
• Date: {meeting_time.strftime('%A, %B %d, %Y')}
• Time: {meeting_time.strftime('%I:%M %p')}
• Duration: {duration_string}

{meet_section}

📝 AGENDA:
• Review current workflows and processes
• Discussion of improvement opportunities  
• Team collaboration and feedback
• Action items and next steps
• Q&A session

⚠️ IMPORTANT NOTES:
• Attendance is required for all staff
• Please join 5 minutes before start time
• Bring any relevant notes or questions
• If unable to attend, notify your supervisor immediately
• Technical support available if needed

Thank you for your dedication to excellent patient care and continuous improvement.

Best regards,
🏥 Hospital Management Team

---
📧 Reply to this email for meeting-related questions
📞 Contact Administration for urgent matters"""

                        msg.attach(MIMEText(body, 'plain'))
                        server.send_message(msg)
                        emails_sent += 1
                        print(f"  SUCCESS: Email sent to {staff.user.email}")
                    else:
                        print(f"  WARNING: Staff member {staff_id} not found or has no email")
                        failed_emails.append(staff_id)
                        
                except Exception as e:
                    print(f"  ERROR: Failed to send email to staff {staff_id}: {str(e)}")
                    failed_emails.append(staff_id)

            server.quit()
            print(f"Email sending completed. {emails_sent}/{len(staff_ids)} emails sent successfully.")
            
            return {
                "success": emails_sent > 0,
                "emails_sent": emails_sent,
                "total_recipients": len(staff_ids),
                "failed_emails": failed_emails,
                "message": f"Successfully sent {emails_sent} emails out of {len(staff_ids)} recipients"
            }
            
        except Exception as e:
            print(f"ERROR in email sending process: {e}")
            return {
                "success": False,
                "emails_sent": 0,
                "total_recipients": len(staff_ids),
                "message": f"Email sending failed: {str(e)}"
            }

    def schedule_meeting(self, query: str) -> Dict[str, Any]:
        """Process a natural language meeting request and schedule if possible."""
        try:
            # Extract meeting title from query
            meeting_title = self.extract_meeting_title(query)
            print(f"Extracted meeting title: {meeting_title}")
            
            # Parse duration from query
            duration_minutes, duration_string = self.parse_duration(query)
            print(f"Extracted duration: {duration_minutes} minutes -> '{duration_string}'")
            
            # Extract specific participants from the query
            participant_names = self.extract_participants_from_query(query)
            if participant_names:
                staff_ids = self.find_staff_by_names(participant_names)
                print(f"Using specific participants: {participant_names} -> {len(staff_ids)} staff members")
            else:
                # Fallback: Get available doctors and nurses if no specific participants mentioned
                available_staff = self.session.query(Staff).filter(
                    Staff.status == 'active',
                    or_(
                        Staff.position.ilike('%doctor%'),
                        Staff.position.ilike('%nurse%'),
                        Staff.position.ilike('%cardiologist%')
                    )
                ).all()
                
                if not available_staff:
                    return {
                        "success": False,
                        "message": "No available staff found"
                    }

                staff_ids = [str(staff.id) for staff in available_staff]
                print(f"Using fallback staff: {len(staff_ids)} available staff members")
            
            # Enhanced parsing with better error handling
            try:
                meeting_time = self.parse_meeting_datetime(query)
                print(f"Successfully parsed meeting time: {meeting_time}")
            except ValueError as e:
                error_message = str(e)
                print(f"DateTime parsing failed: {error_message}")
                
                # Check if we can suggest a fix
                if "Could not find meeting time" in error_message or "time" in error_message.lower():
                    # Try to extract just the date and suggest times
                    query_lower = query.lower()
                    if any(word in query_lower for word in ['tomorrow', 'today', '2025', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
                        return {
                            "success": False,
                            "message": f"It seems there was a problem parsing the meeting time from the provided information. To ensure the meeting is scheduled correctly, could you please provide the specific time for the meeting on the requested date? Including an exact start time will help me process your request accurately.\n\nFor example:\n- Date and Time: {query} at 10:00 AM\n\nWith the exact time, I'll be able to schedule the meeting and arrange for confirmation emails to be sent to the specified participants.",
                            "suggestion": "Please specify the exact time (e.g., '10:00 AM', '2:30 PM') for accurate scheduling.",
                            "query_received": query
                        }
                
                return {
                    "success": False,
                    "message": error_message,
                    "query_received": query
                }
            
            # Check availability for the specified time
            if not self.check_availability(staff_ids, meeting_time, duration_minutes):
                return {
                    "success": False,
                    "message": "Selected time slot has conflicts"
                }

            # Generate REAL Google Meet link with your account as host
            meet_link = None
            google_event_id = None
            
            try:
                print("Creating REAL Google Meet with your account as host...")
                
                # Initialize Google Meet API
                google_meet_api = GoogleMeetAPIIntegration()
                
                # Collect attendee emails
                attendee_emails = []
                for staff_id in staff_ids:
                    staff = self.session.query(Staff).join(User).filter(Staff.id == uuid.UUID(staff_id)).first()
                    if staff and staff.user.email:
                        attendee_emails.append(staff.user.email)
                
                # Create real Google Meet event with your account as host
                meet_result = google_meet_api.create_meet_event(
                    title=meeting_title,
                    description=f"Hospital staff meeting scheduled via Hospital Management System.\n"
                               f"Query: {query}\n"
                               f"Participants: {len(staff_ids)} staff members\n"
                               f"Meeting time: {meeting_time.strftime('%Y-%m-%d %H:%M')}",
                    start_time=meeting_time,
                    duration_minutes=duration_minutes,  # Use parsed duration
                    attendees=attendee_emails
                )
                
                if 'meet_link' in meet_result and meet_result['meet_link']:
                    meet_link = meet_result['meet_link']
                    google_event_id = meet_result.get('event_id', None)
                    print(f"SUCCESS: REAL Google Meet created with your account as host!")
                    print(f"  Meet Link: {meet_link}")
                    print(f"  Event ID: {google_event_id}")
                    print(f"  Attendees will receive Google Calendar invitations")
                else:
                    print("WARNING: Google Meet API didn't return a meet link")
                    print(f"Full result: {meet_result}")
                    # Create a better fallback meeting link with meeting title
                    meeting_slug = meeting_title.lower().replace(" ", "-").replace("meeting", "").strip("-")
                    meet_link = f"https://meet.google.com/{meeting_slug}-{meeting_time.strftime('%m%d-%H%M')}"
                    print(f"Using fallback Google Meet link: {meet_link}")
                    
            except Exception as e:
                print(f"Error creating REAL Google Meet: {e}")
                print("This means the Google Calendar API integration failed")
                # Create a better fallback meeting link with meeting title
                meeting_slug = meeting_title.lower().replace(" ", "-").replace("meeting", "").strip("-")
                meet_link = f"https://meet.google.com/{meeting_slug}-{meeting_time.strftime('%m%d-%H%M')}"
                print(f"Using fallback Google Meet link: {meet_link}")

            # Store meeting in database using new Meeting Management System
            try:
                print("Storing meeting in database...")
                
                # Get first staff member for organizer and department info
                first_staff = self.session.query(Staff).filter(Staff.id == uuid.UUID(staff_ids[0])).first()
                
                db_meeting = self.meeting_manager.create_meeting(
                    title=meeting_title,
                    description=f"Hospital staff meeting scheduled via Hospital Management System.\n"
                               f"Query: {query}\n"
                               f"Participants: {len(staff_ids)} staff members",
                    meeting_datetime=meeting_time,
                    duration_minutes=duration_minutes,  # Use parsed duration
                    google_meet_link=meet_link,
                    google_event_id=google_event_id,
                    organizer_staff_id=staff_ids[0],  # First staff as organizer
                    department_id=str(first_staff.department_id) if first_staff and first_staff.department_id else None,
                    meeting_type='staff',
                    priority='normal',
                    agenda="• Discussion of key topics\n• Team coordination\n• Q&A session"
                )
                
                # Add participants to the meeting
                self.meeting_manager.add_participants(str(db_meeting.id), staff_ids)
                
                meeting_id = str(db_meeting.id)
                print(f"Meeting stored in database with ID: {meeting_id}")
                
            except Exception as e:
                print(f"Error storing meeting in database: {e}")
                # Create a fallback meeting ID
                meeting_id = str(uuid.uuid4())

            # Also create old StaffMeeting record for backward compatibility
            try:
                # Create meeting record (old system)
                old_meeting = StaffMeeting(
                    title=meeting_title,
                    description=f"Meeting scheduled via Hospital Management System: {query}",
                    meeting_time=meeting_time,
                    duration_minutes=duration_minutes,  # Use parsed duration
                    location="Conference Room A",
                    organizer_id=uuid.UUID(staff_ids[0])  # First staff member as organizer
                )
                
                # Add all participants
                for staff_id in staff_ids:
                    staff = self.session.query(Staff).filter(Staff.id == uuid.UUID(staff_id)).first()
                    if staff:
                        old_meeting.participants.append(staff)

                self.session.add(old_meeting)
                self.session.commit()
                
            except Exception as e:
                print(f"Error creating old meeting record: {e}")
                self.session.rollback()

            # Send notifications with Meet link
            email_result = self.send_meeting_notifications(
                staff_ids,
                meeting_time,
                meeting_title,
                "Conference Room A",
                meet_link,
                duration_string,  # Pass duration string to email
                meeting_title    # Pass meeting_title parameter
            )

            if not email_result["success"]:
                self.session.rollback()
                return {
                    "success": False,
                    "message": "Failed to send meeting notifications"
                }

            return {
                "success": True,
                "message": f"Meeting scheduled successfully with Google Meet link. {email_result['message']}",
                "data": {
                    "meeting_id": meeting_id,
                    "title": meeting_title,
                    "time": meeting_time.strftime("%I:%M %p"),
                    "duration": duration_string,  # Use parsed duration string
                    "location": "Conference Room A",
                    "participants": len(staff_ids),
                    "google_meet_link": meet_link,
                    "emails_sent": email_result["emails_sent"],
                    "email_success": email_result["success"]
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to schedule meeting: {str(e)}"
            }
