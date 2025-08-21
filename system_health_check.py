#!/usr/bin/env python3
"""
Comprehensive Hospital Management System Health Check
=====================================================

This script performs a complete system check and validates all recent updates.
"""

import os
import sys
import json
import requests
import asyncio
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🏥 {title}")
    print(f"{'='*60}")

def print_subsection(title):
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def check_file_exists(file_path, description=""):
    """Check if a file exists and return status"""
    if os.path.exists(file_path):
        print(f"✅ {description or file_path}: Found")
        return True
    else:
        print(f"❌ {description or file_path}: Missing")
        return False

def check_backend_components():
    """Check all backend components"""
    print_section("BACKEND COMPONENTS CHECK")
    
    backend_files = {
        "backend-python/multi_agent_server.py": "Multi-Agent Server (Main Entry Point)",
        "backend-python/.env": "Environment Configuration",
        "backend-python/database.py": "Database Models",
        "backend-python/meeting_scheduler.py": "Meeting Scheduler Agent",
        "backend-python/agents/staff_agent.py": "Staff Management Agent",
        "backend-python/agents/room_bed_agent.py": "Room & Bed Management Agent",
        "backend-python/agents/google_meet_api.py": "Google Meet Integration",
        "backend-python/pyproject.toml": "Python Dependencies",
        "backend-python/Dockerfile": "Docker Configuration",
        "backend-python/start.sh": "Deployment Startup Script"
    }
    
    all_good = True
    for file_path, description in backend_files.items():
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_frontend_components():
    """Check all frontend components"""
    print_section("FRONTEND COMPONENTS CHECK")
    
    frontend_files = {
        "frontend/src/components/DirectMCPChatbot.jsx": "Main Frontend Component",
        "frontend/src/services/directHttpMcpClient.js": "MCP Client Service",
        "frontend/package.json": "Frontend Dependencies",
        "frontend/Dockerfile": "Frontend Docker Configuration",
        "frontend/vite.config.js": "Vite Build Configuration"
    }
    
    all_good = True
    for file_path, description in frontend_files.items():
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_deployment_files():
    """Check deployment configuration files"""
    print_section("DEPLOYMENT CONFIGURATION CHECK")
    
    deployment_files = {
        "docker-compose.yml": "Docker Compose Configuration",
        "nginx.conf": "Nginx Proxy Configuration",
        "aws-infrastructure.yml": "AWS Infrastructure",
        "backend-python/start.sh": "Backend Startup Script",
        ".gitignore": "Git Ignore Rules"
    }
    
    all_good = True
    for file_path, description in deployment_files.items():
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_environment_variables():
    """Check environment variables configuration"""
    print_section("ENVIRONMENT VARIABLES CHECK")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv("backend-python/.env")
    
    required_vars = {
        'DATABASE_URL': 'Database Connection',
        'GEMINI_API_KEY': 'Google Gemini API',
        'SMTP_SERVER': 'Email SMTP Server',
        'SMTP_PORT': 'Email SMTP Port',
        'EMAIL_USERNAME': 'Email Username',
        'EMAIL_PASSWORD': 'Email Password',
        'EMAIL_FROM_NAME': 'Email From Name',
        'EMAIL_FROM_ADDRESS': 'Email From Address'
    }
    
    all_good = True
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            if 'PASSWORD' in var_name or 'API_KEY' in var_name:
                print(f"✅ {description} ({var_name}): ***configured***")
            else:
                print(f"✅ {description} ({var_name}): {value}")
        else:
            print(f"❌ {description} ({var_name}): NOT SET")
            all_good = False
    
    return all_good

def check_recent_fixes():
    """Check if recent fixes are properly applied"""
    print_section("RECENT FIXES VERIFICATION")
    
    fixes_applied = []
    
    # Check 1: Room dropdown fix
    print_subsection("Room Dropdown Fix")
    try:
        with open("frontend/src/components/DirectMCPChatbot.jsx", 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for simplified room dropdown (no IIFE)
            if 'Array.isArray(roomOptions) ? roomOptions.map(room =>' in content and '(() => {' not in content.split('roomOptions.map')[0].split('\n')[-1]:
                print("✅ Room dropdown simplified (removed IIFE)")
                fixes_applied.append("room_dropdown")
            else:
                print("⚠️ Room dropdown may still have complex IIFE structure")
            
            # Check for consistent loading pattern
            if 'const rooms = roomsResponse?.result?.content?.[0]?.text' in content:
                print("✅ Room loading uses consistent pattern")
                fixes_applied.append("room_loading")
            else:
                print("⚠️ Room loading pattern may be inconsistent")
                
    except Exception as e:
        print(f"❌ Could not verify room dropdown fix: {e}")
    
    # Check 2: Staff model fix
    print_subsection("Staff Model Fix")
    try:
        with open("backend-python/agents/staff_agent.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'serialize_model' in content and 'staff.user.first_name' in content:
                print("✅ Staff model includes User relationship serialization")
                fixes_applied.append("staff_model")
            else:
                print("⚠️ Staff model User relationship may not be properly serialized")
                
    except Exception as e:
        print(f"❌ Could not verify staff model fix: {e}")
    
    # Check 3: Room status field
    print_subsection("Room Status Field Fix")
    try:
        with open("backend-python/database.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'status = Column(String(20), default="available")' in content:
                print("✅ Room model includes status field")
                fixes_applied.append("room_status")
            else:
                print("⚠️ Room status field may be missing")
                
    except Exception as e:
        print(f"❌ Could not verify room status fix: {e}")
    
    # Check 4: Google OAuth setup
    print_subsection("Google OAuth Setup")
    oauth_files = [
        "backend-python/agents/google_meet_api.py",
        "backend-python/token.pickle"
    ]
    
    oauth_configured = True
    for file_path in oauth_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Present")
        else:
            print(f"⚠️ {file_path}: Missing (may need re-authentication)")
            oauth_configured = False
    
    if oauth_configured:
        fixes_applied.append("google_oauth")
    
    # Check 5: Email deployment guides
    print_subsection("Email Deployment Support")
    deployment_guides = [
        "EMAIL-DEPLOYMENT-FIX.md",
        "verify_deployment_email.py",
        "diagnose_email_deployment.py"
    ]
    
    guides_present = True
    for guide in deployment_guides:
        if os.path.exists(guide):
            print(f"✅ {guide}: Available")
        else:
            print(f"⚠️ {guide}: Missing")
            guides_present = False
    
    if guides_present:
        fixes_applied.append("email_deployment_guides")
    
    return fixes_applied

def check_server_connectivity():
    """Check if servers are running and accessible"""
    print_section("SERVER CONNECTIVITY CHECK")
    
    servers = {
        'http://localhost:8000': 'Backend MCP Server',
        'http://localhost:5173': 'Frontend Development Server'
    }
    
    connectivity_status = {}
    for url, name in servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                print(f"✅ {name}: Accessible ({response.status_code})")
                connectivity_status[name] = True
            else:
                print(f"⚠️ {name}: Unexpected status {response.status_code}")
                connectivity_status[name] = False
        except requests.exceptions.RequestException:
            print(f"❌ {name}: Not accessible")
            connectivity_status[name] = False
    
    return connectivity_status

def check_api_endpoints():
    """Check key API endpoints"""
    print_section("API ENDPOINTS CHECK")
    
    if not requests.get('http://localhost:8000', timeout=2).status_code:
        print("❌ Backend server not running - skipping API tests")
        return False
    
    endpoints_to_test = [
        ('list_rooms', 'Room Listing API'),
        ('list_departments', 'Department Listing API'),
        ('list_staff', 'Staff Listing API'),
        ('list_users', 'User Listing API')
    ]
    
    all_working = True
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.post(
                'http://localhost:8000/tools/call',
                json={'params': {'name': endpoint, 'arguments': {}}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['result']['content'][0]['text']
                data = json.loads(content)
                
                if data.get('success') and 'data' in data.get('result', {}):
                    count = len(data['result']['data'])
                    print(f"✅ {description}: Working ({count} items)")
                else:
                    print(f"⚠️ {description}: Returned unsuccessful result")
                    all_working = False
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                all_working = False
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            all_working = False
    
    return all_working

def generate_system_report():
    """Generate comprehensive system report"""
    print_section("COMPREHENSIVE SYSTEM REPORT")
    
    # Run all checks
    backend_ok = check_backend_components()
    frontend_ok = check_frontend_components()
    deployment_ok = check_deployment_files()
    env_ok = check_environment_variables()
    fixes = check_recent_fixes()
    connectivity = check_server_connectivity()
    api_ok = check_api_endpoints()
    
    # Summary
    print_section("SYSTEM STATUS SUMMARY")
    
    print(f"📦 Backend Components: {'✅ All Present' if backend_ok else '❌ Some Missing'}")
    print(f"🎨 Frontend Components: {'✅ All Present' if frontend_ok else '❌ Some Missing'}")
    print(f"🚀 Deployment Config: {'✅ Complete' if deployment_ok else '❌ Incomplete'}")
    print(f"⚙️ Environment Variables: {'✅ Configured' if env_ok else '❌ Missing Variables'}")
    print(f"🔧 Recent Fixes Applied: {len(fixes)}/5 ({', '.join(fixes)})")
    print(f"🌐 Server Connectivity: {sum(connectivity.values())}/{len(connectivity)} servers accessible")
    print(f"🔌 API Endpoints: {'✅ Working' if api_ok else '❌ Issues Found'}")
    
    # Overall system health
    total_checks = 7
    passed_checks = sum([backend_ok, frontend_ok, deployment_ok, env_ok, len(fixes) >= 4, sum(connectivity.values()) >= 1, api_ok])
    health_percentage = (passed_checks / total_checks) * 100
    
    print(f"\n🏥 OVERALL SYSTEM HEALTH: {health_percentage:.0f}% ({passed_checks}/{total_checks} checks passed)")
    
    if health_percentage >= 90:
        print("🎉 EXCELLENT: System is fully operational!")
        return True
    elif health_percentage >= 75:
        print("✅ GOOD: System is mostly operational with minor issues")
        return True
    elif health_percentage >= 50:
        print("⚠️ FAIR: System has several issues that need attention")
        return False
    else:
        print("❌ POOR: System needs significant fixes")
        return False

if __name__ == "__main__":
    print("🏥 Hospital Management System - Comprehensive Health Check")
    print(f"Date: {os.popen('date').read().strip() if os.name != 'nt' else 'Windows'}")
    print(f"Location: {os.getcwd()}")
    
    try:
        system_healthy = generate_system_report()
        sys.exit(0 if system_healthy else 1)
    except Exception as e:
        print(f"\n❌ System check failed with error: {e}")
        sys.exit(1)
