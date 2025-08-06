from meeting_scheduler import MeetingSchedulerAgent

agent = MeetingSchedulerAgent()
print("Testing fixed date parsing:")

test_cases = [
    "Schedule meeting on August 10th 2025 at 4pm",
    "Schedule meeting on 2025-08-20 at 9am", 
    "Schedule meeting tomorrow at 3pm"
]

for query in test_cases:
    try:
        result = agent.parse_meeting_datetime(query)
        print(f"SUCCESS: {query} -> {result.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"ERROR: {query} -> {e}")
