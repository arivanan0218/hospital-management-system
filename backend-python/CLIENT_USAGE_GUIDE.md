# Hospital Management System - Client Usage Guide

## 🚀 How to Run the Agentic AI Client

### Prerequisites

1. **Database Setup**
   ```powershell
   # Make sure PostgreSQL is running and database is set up
   python setup_database.py
   ```

2. **Environment Check**
   ```powershell
   # Verify all dependencies are installed
   python -c "import mcp, sqlalchemy, psycopg2; print('✅ All dependencies available')"
   ```

### 🎯 Running the Client

#### Option 1: Direct Execution
```powershell
# Navigate to the backend-python directory
cd c:\Users\Arivanan\hospital-management-system\backend-python

# Run the client
python client.py
```

#### Option 2: Using Python Module
```powershell
# From the project root
python -m backend-python.client
```

### 📋 Client Modes

When you run `python client.py`, you'll see:

```
🏥 Hospital Management System - Agentic AI Client
Choose mode:
1. Comprehensive Demo (All Features)
2. Interactive Mode (Manual Control)
3. Agentic AI Mode (Autonomous Operation)
Enter choice (1, 2, or 3):
```

#### Mode 1: Comprehensive Demo
- **Purpose**: Demonstrates all 32+ MCP tools
- **Duration**: ~5-10 minutes
- **Output**: Shows every feature in action
- **Use Case**: First-time setup verification, showcasing capabilities

```powershell
# Example output:
👥 === USER MANAGEMENT DEMO ===
🏢 === DEPARTMENT MANAGEMENT DEMO ===
🤒 === PATIENT MANAGEMENT DEMO ===
🛏️  === BED MANAGEMENT AGENT DEMO ===
🔧 === EQUIPMENT TRACKER AGENT DEMO ===
📦 === SUPPLY INVENTORY AGENT DEMO ===
```

#### Mode 2: Interactive Mode
- **Purpose**: Manual control with full agentic AI features
- **Duration**: User-controlled
- **Output**: Menu-driven interface
- **Use Case**: Testing specific features, manual operations

```powershell
# Interactive menu options:
=== BASIC OPERATIONS ===
1. User Management
2. Department Management
3. Patient Management
4. Bed Management (AI Agent)
5. Equipment Management (AI Agent)
6. Supply Management (AI Agent)
7. Staff Management (AI Agent)
8. Appointment Management
9. Agent Logging
10. Legacy Support

=== AGENTIC AI FEATURES ===
11. Analyze Hospital State
12. Autonomous Management
13. Intelligent Patient Admission
14. Smart Resource Optimization
15. Run Full Agentic Demo
```

#### Mode 3: Agentic AI Mode
- **Purpose**: Autonomous operation with intelligent decision-making
- **Duration**: ~3-5 minutes
- **Output**: AI analysis and recommendations
- **Use Case**: Production-like autonomous hospital management

```powershell
# Example output:
🧠 === AGENTIC AI ANALYSIS ===
📊 Hospital State Analysis:
   👥 Users: 4
   🏢 Departments: 3
   🤒 Patients: 5
   🛏️  Bed Occupancy: 75.0%
   🔧 Equipment Issues: 0
   📦 Supply Alerts: 1
   📅 Appointments: 4

💡 AI Recommendations:
   1. Restock 1 low-inventory items
   2. Patient capacity exceeds available beds
```

### 🛠️ Troubleshooting

#### Common Issues and Solutions

1. **Import Errors**
   ```powershell
   # If you see "ModuleNotFoundError"
   pip install fastmcp sqlalchemy psycopg2-binary python-dotenv
   ```

2. **Database Connection Issues**
   ```powershell
   # Test database connection
   python database.py
   
   # Reset database if needed
   python setup_database.py
   ```

3. **MCP Server Connection Issues**
   ```powershell
   # Test the MCP server independently
   python comprehensive_server.py
   
   # Check if server starts without errors
   ```

4. **Permission Issues**
   ```powershell
   # Run PowerShell as Administrator if needed
   # Or check file permissions
   ```

### 🔧 Advanced Usage

#### Running Specific Functions
```powershell
# Test only the connection
python -c "
import asyncio
from client import HospitalManagementClient

async def test():
    client = HospitalManagementClient()
    await client.connect()
    print('✅ Connection successful')
    await client.disconnect()

asyncio.run(test())
"
```

#### Testing CRUD Operations
```powershell
# Test create operations
python test_client.py
```

#### Running in Background
```powershell
# For autonomous monitoring (Windows)
Start-Process python -ArgumentList "client.py" -WindowStyle Hidden

# Or use Task Scheduler for production deployment
```

### 📊 Expected Outputs

#### Successful Connection
```
🔌 Connecting to server...
🔗 Initializing session...
✅ Connected to Hospital Management MCP Server
🛠️  Loaded 32 tools
```

#### CRUD Operations Working
```
✅ Demo data creation completed!
📝 Testing CREATE operations:
User creation: True
Patient creation: True
📖 Testing READ operations:
List users: 4
List patients: 5
List departments: 3
```

#### AI Analysis
```
📊 Hospital State Analysis:
   👥 Users: 4
   🏢 Departments: 3
   🤒 Patients: 5
   🛏️  Bed Occupancy: 75.0%
   🔧 Equipment Issues: 0
   📦 Supply Alerts: 1
```

### 🔍 Monitoring and Logging

#### Check Client Performance
```powershell
# Monitor client execution
python -c "
import time
start = time.time()
# Run your client operations
print(f'Execution time: {time.time() - start:.2f} seconds')
"
```

#### View Database Changes
```powershell
# Check what the client created
python -c "
from database import get_db_summary
summary = get_db_summary()
print(summary)
"
```

### 🚀 Production Deployment

#### As a Windows Service
```powershell
# Install pywin32 for service support
pip install pywin32

# Create service script (service_wrapper.py)
# Register as Windows service
```

#### Scheduled Execution
```powershell
# Use Windows Task Scheduler
schtasks /create /tn "HospitalAI" /tr "python c:\path\to\client.py" /sc daily /st 09:00
```

### 📈 Performance Monitoring

#### Memory Usage
```powershell
# Monitor memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

#### Response Time Testing
```powershell
# Test response times
python -c "
import asyncio
import time
from client import HospitalManagementClient

async def benchmark():
    client = HospitalManagementClient()
    await client.connect()
    
    start = time.time()
    await client.analyze_hospital_state()
    print(f'Analysis time: {time.time() - start:.2f}s')
    
    await client.disconnect()

asyncio.run(benchmark())
"
```

### 🆘 Emergency Commands

#### Stop All Operations
```powershell
# Kill all Python processes (use carefully!)
taskkill /F /IM python.exe

# Or use Ctrl+C in the terminal
```

#### Quick Health Check
```powershell
# Verify system health
python -c "
from database import test_connection
from comprehensive_server import main as test_server
print('Database:', 'OK' if test_connection() else 'FAILED')
"
```

#### Reset Everything
```powershell
# Nuclear option - reset entire system
python setup_database.py
python client.py
```

## 📞 Support Commands

```powershell
# Check Python version
python --version

# Check installed packages
pip list | findstr -i "mcp sqlalchemy psycopg2"

# Check database status
python -c "import psycopg2; print('PostgreSQL driver OK')"

# Test MCP framework
python -c "import mcp; print('MCP framework OK')"
```

This guide should help you successfully run and manage the Hospital Management System Agentic AI client!
