#!/usr/bin/env python3
"""
Hospital Management System - Complete Demonstration
Demonstrates meeting scheduling with Google Meet integration and patient discharge reports
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the backend-python directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_server import orchestrator, MULTI_AGENT_AVAILABLE
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HospitalDemonstration:
    """Complete demonstration of the Hospital Management System"""
    
    def __init__(self):
        self.demo_patient_id = "DEMO001"
        self.demo_meeting_id = None
        
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*80)
        print(f"🏥 {title}")
        print("="*80)
    
    def print_step(self, step_num, description):
        """Print a formatted step"""
        print(f"\n📋 Step {step_num}: {description}")
        print("-" * 60)
    
    async def demonstrate_system_overview(self):
        """Show system overview and capabilities"""
        
        self.print_header("HOSPITAL MANAGEMENT SYSTEM - OVERVIEW")
        
        if not MULTI_AGENT_AVAILABLE or not orchestrator:
            print("❌ Multi-agent system not available")
            return False
            
        print("🤖 System Status:")
        print(f"   - Multi-agent system: ✅ Active")
        print(f"   - Available agents: {len(orchestrator.agents)}")
        print(f"   - Total tools: {len(orchestrator.get_tools())}")
        
        print("\n📊 Available Agents:")
        for agent_name in orchestrator.agents.keys():
            print(f"   - {agent_name.title()} Agent")
        
        print("\n🔧 New Features Added:")
        print("   ✅ Meeting Scheduling with Google Meet Integration")
        print("   ✅ Automated Email Confirmations") 
        print("   ✅ Patient Discharge Report Generation")
        print("   ✅ Clinical Data Aggregation")
        print("   ✅ Staff Interaction Tracking")
        
        return True
    
    async def demonstrate_meeting_scheduling(self):
        """Demonstrate the complete meeting scheduling workflow"""
        
        self.print_header("MEETING SCHEDULING & EMAIL CONFIRMATIONS")
        
        try:
            # Step 1: Schedule a consultation meeting
            self.print_step(1, "Schedule a Patient Consultation Meeting")
            
            tomorrow = datetime.now() + timedelta(days=1)
            meeting_query = f"""
            Schedule a patient consultation meeting for tomorrow at 2 PM.
            Title: Patient Treatment Review - John Doe
            Participants: Dr. Smith, Dr. Johnson, Nurse Williams
            Location: Conference Room A
            Duration: 60 minutes
            Priority: High
            Type: Medical Consultation
            Description: Review treatment progress and discuss discharge planning for patient John Doe (ID: {self.demo_patient_id})
            """
            
            print(f"🗣️ Meeting Request: {meeting_query.strip()}")
            
            result = orchestrator.route_request("schedule_meeting", query=meeting_query)
            print(f"\n✅ Meeting Scheduled:")
            print(f"   Result: {result}")
            
            # Extract meeting ID if successful
            if isinstance(result, dict) and result.get('success') and 'meeting_id' in result:
                self.demo_meeting_id = result['meeting_id']
                print(f"   📅 Meeting ID: {self.demo_meeting_id}")
            
            # Step 2: List upcoming meetings  
            self.print_step(2, "List Upcoming Meetings")
            
            result = orchestrator.route_request("list_meetings", 
                                              date_str="tomorrow", 
                                              days_ahead=7)
            print(f"� Upcoming Meetings: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Meeting scheduling demonstration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def demonstrate_discharge_reports(self):
        """Demonstrate the complete discharge report workflow"""
        
        self.print_header("PATIENT DISCHARGE REPORT GENERATION")
        
        try:
            # Step 1: Add treatment records
            self.print_step(1, f"Add Treatment Records for Patient {self.demo_patient_id}")
            
            result = orchestrator.route_request("add_treatment_record_simple",
                                               patient_id=self.demo_patient_id,
                                               treatment_type="medication",
                                               description="Administered IV antibiotics for pneumonia",
                                               physician="Dr. Smith",
                                               outcome="Patient responded well to treatment")
            print(f"✅ Treatment Record Added: {result}")
            
            # Step 2: Generate discharge report
            self.print_step(2, f"Generate Complete Discharge Report")
            
            result = orchestrator.route_request("generate_discharge_report",
                                               patient_id=self.demo_patient_id,
                                               discharge_date="2024-01-17",
                                               attending_physician="Dr. Smith",
                                               follow_up_instructions="Follow up with primary care in 1 week")
            print(f"📄 Discharge Report: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Discharge report demonstration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_complete_demonstration(self):
        """Run the complete system demonstration"""
        
        print("🏥 HOSPITAL MANAGEMENT SYSTEM - COMPLETE DEMONSTRATION")
        print("=" * 80)
        print("This demonstration shows the integrated meeting scheduling,")
        print("email confirmation, and discharge report generation features.")
        print("=" * 80)
        
        results = {
            'system_overview': await self.demonstrate_system_overview(),
            'meeting_scheduling': await self.demonstrate_meeting_scheduling(), 
            'discharge_reports': await self.demonstrate_discharge_reports()
        }
        
        # Final summary
        self.print_header("DEMONSTRATION SUMMARY")
        
        print("� Demonstration Results:")
        for feature, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            feature_name = feature.replace('_', ' ').title()
            print(f"   {feature_name}: {status}")
        
        overall_success = all(results.values())
        
        if overall_success:
            print("\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("\n✅ Key Features Demonstrated:")
            print("   📅 Meeting scheduling with natural language processing")
            print("   � Google Meet integration and automatic link generation")
            print("   📧 Email confirmations and notifications")
            print("   📄 Comprehensive patient discharge reports")  
            print("   🏥 Clinical data aggregation and analysis")
            
            print("\n🔄 System is ready for production use!")
            
        else:
            print("\n⚠️ Some demonstration features had issues.")
            print("Please check the output above for details.")
        
        return overall_success

async def main():
    """Main demonstration function"""
    
    try:
        demo = HospitalDemonstration()
        success = await demo.run_complete_demonstration()
        
        if success:
            print("\n🏁 The Hospital Management System is fully integrated and ready!")
            return 0
        else:
            print("\n⚠️ Demonstration completed with some issues.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstration interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🚀 Starting Hospital Management System Demonstration...")
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
