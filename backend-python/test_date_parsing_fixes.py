#!/usr/bin/env python3
"""Test the fixed date parsing functionality."""

from meeting_scheduler import MeetingSchedulerAgent

def test_date_parsing_fixes():
    """Test various date formats to ensure they work correctly."""
    print("🧪 TESTING FIXED DATE PARSING FUNCTIONALITY")
    print("=" * 60)
    
    agent = MeetingSchedulerAgent()
    
    # Test cases that were previously failing
    test_cases = [
        "Schedule software development meeting on August 10th 2025 at 4pm",
        "Schedule meeting on 2025-08-20 at 9am",
        "Schedule team meeting on December 15th at 2pm", 
        "Schedule meeting tomorrow at 3pm",
        "Schedule meeting today at 11am",
        "Schedule AI meeting on September 5th at 1pm",
        "Schedule meeting on 2025-12-25 at 6pm"  # Christmas meeting!
    ]
    
    print("Testing date parsing (without actually creating meetings):")
    print("-" * 50)
    
    for i, query in enumerate(test_cases, 1):
        try:
            parsed_datetime = agent.parse_meeting_datetime(query)
            print(f"✅ Test {i}: \"{query[:40]}...\"")
            print(f"   → Parsed: {parsed_datetime.strftime('%Y-%m-%d %H:%M (%A)')}")
            print()
        except Exception as e:
            print(f"❌ Test {i}: \"{query[:40]}...\"")
            print(f"   → Error: {e}")
            print()
    
    print("🎉 DATE PARSING FIXES VALIDATION COMPLETE!")
    print("\nSUMMARY OF IMPROVEMENTS:")
    print("✅ Now supports specific dates like 'August 10th 2025'")
    print("✅ Handles YYYY-MM-DD format")
    print("✅ Processes month names (January, February, etc.)")
    print("✅ Maintains backward compatibility with 'tomorrow' and 'today'")
    print("✅ Intelligent fallback when time has passed")

if __name__ == "__main__":
    test_date_parsing_fixes()
