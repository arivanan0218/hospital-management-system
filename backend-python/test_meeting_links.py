"""Test Meeting Links - Verify they work in browser"""

from real_google_meet_alternative import RealGoogleMeetGenerator
import webbrowser

def test_meeting_links():
    """Test and optionally open meeting links in browser."""
    
    print("🔗 TESTING MEETING LINKS")
    print("=" * 50)
    
    # Generate test links
    generator = RealGoogleMeetGenerator()
    
    # Test Google Meet link
    google_link = generator.create_instant_meeting("Test Meeting")
    print(f"Google Meet: {google_link}")
    
    # Test Jitsi link
    jitsi_link = generator.create_jitsi_meeting("Test Meeting")
    print(f"Jitsi Meet: {jitsi_link}")
    
    # Test complete solution
    solution = generator.create_working_meet_solution("Test Meeting")
    primary_link = solution["primary_link"]
    backup_link = solution.get("google_meet_link")
    
    print(f"\nPRIMARY (Recommended): {primary_link}")
    print(f"BACKUP: {backup_link}")
    
    print("\n" + "=" * 50)
    print("TESTING INSTRUCTIONS:")
    print("1. Copy and paste these links in your browser")
    print("2. Jitsi Meet links should work immediately")
    print("3. Google Meet links may require sign-in")
    print("4. Test with multiple browser tabs to simulate participants")
    print("=" * 50)
    
    # Ask user if they want to open links
    response = input("\nDo you want to open the primary link in browser? (y/n): ")
    if response.lower() == 'y':
        try:
            print(f"Opening: {primary_link}")
            webbrowser.open(primary_link)
            print("✅ Link opened in browser!")
        except Exception as e:
            print(f"❌ Error opening browser: {e}")
            print(f"Please manually open: {primary_link}")

if __name__ == "__main__":
    test_meeting_links()
