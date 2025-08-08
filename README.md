# Hospital Management System

A modern, AI-powered hospital management system built with containerized microservices architecture. This system provides comprehensive hospital operations management through an intelligent chatbot interface.

## 🏗️ Architecture Overview

This hospital management system is a **3-tier containerized application** with the following components:

1. **Backend Python (Port 8000)** - MCP Server with PostgreSQL database
2. **MCP Process Manager (Port 3001)** - Node.js service for managing MCP servers  
3. **Frontend React (Port 80)** - User interface with AI chatbot integration
4. **PostgreSQL Database (Port 5432)** - Data persistence layer

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  MCP Process     │    │  Backend        │    │   PostgreSQL    │
│   React App     │───▶│  Manager         │───▶│  Python MCP     │───▶│   Database      │
│   (Port 80)     │    │  (Port 3001)     │    │  (Port 8000)    │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- API keys for AI services (at least one required):
  - `GEMINI_API_KEY` (Required for backend AI features)
  - `VITE_OPENAI_API_KEY` (For OpenAI GPT)
  - `VITE_CLAUDE_API_KEY` (For Claude AI)
  - `VITE_GROQ_API_KEY` (For Groq AI)
  - `VITE_GOOGLE_API_KEY` (For Google AI)

### Installation & Deployment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arivanan0218/hospital-management-system.git
   cd hospital-management-system
   
   # Switch to docker branch for latest deployment features
   git checkout docker
   ```

2. **Environment Setup**:
   ```bash
   # Copy environment template
   cp .env.docker .env
   
   # Edit .env file with your API keys
   # nano .env  # or use your preferred editor
   ```

3. **Deploy with Docker**:

   **Windows:**
   ```cmd
   deploy.bat start
   ```

   **Linux/Mac:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh start
   ```

4. **Access the Application**:
   - **Frontend**: http://localhost
   - **MCP Manager**: http://localhost:3001
   - **Backend API**: http://localhost:8000
   - **Database**: localhost:5432

## 📋 System Components

### 1. Database Layer (`backend-python/database.py`)

**Purpose**: Defines the complete hospital data model using SQLAlchemy ORM

**Core Models**:
- **`User`** - Authentication and basic user info (doctors, nurses, admins)
- **`Department`** - Hospital departments with head doctors
- **`Patient`** - Patient records with medical history
- **`Staff`** - Employee information linked to users and departments
- **`Room`** & **`Bed`** - Physical hospital infrastructure
- **`Equipment`** & **`EquipmentCategory`** - Medical equipment tracking
- **`Supply`** & **`SupplyCategory`** - Inventory management
- **`Appointment`** - Patient-doctor scheduling
- **`InventoryTransaction`** - Supply stock movements
- **`AgentInteraction`** - AI chatbot interaction logging

**Key Features**:
- UUID primary keys for security
- Automatic timestamps (`created_at`, `updated_at`)
- Comprehensive relationships between entities
- Data migration from JSON to PostgreSQL

### 2. MCP Server (`backend-python/comprehensive_server.py`)

**Purpose**: Model Context Protocol server providing 35+ hospital management tools to AI

**Available Tools**:

#### User Management
- `create_user` - Create new system users
- `list_users` - List all users
- `get_user_by_id` - Get user details
- `update_user` - Update user information
- `delete_user` - Remove users

#### Patient Management
- `create_patient` - Register new patients
- `list_patients` - List all patients
- `get_patient_by_id` - Get patient details by UUID or patient number (case-insensitive)
- `search_patients` - Search patients by name, phone, email, or patient number (all case-insensitive)

#### Department Management
- `create_department` - Create hospital departments
- `list_departments` - List all departments
- `get_department_by_id` - Get department details

#### Bed & Room Management
- `create_room` - Create hospital rooms
- `list_rooms` - List all rooms
- `create_bed` - Create beds in rooms
- `list_beds` - List beds with status
- `assign_bed_to_patient` - Assign beds to patients
- `discharge_bed` - Discharge patients from beds

#### Appointment Management
- `create_appointment` - Schedule appointments
- `list_appointments` - List appointments (filtered by doctor/patient/date)

#### Equipment Management
- `create_equipment` - Add medical equipment
- `list_equipment` - List equipment by status/department
- `update_equipment_status` - Update equipment status
- `create_equipment_category` - Create equipment categories

#### Supply Management
- `create_supply` - Add supply items
- `list_supplies` - List supplies (with low stock filter)
- `update_supply_stock` - Update inventory levels
- `create_supply_category` - Create supply categories

#### Staff Management
- `create_staff` - Add staff members
- `list_staff` - List staff by department/status

### 3. MCP Process Manager (`mcp-process-manager/server.js`)

**Purpose**: Node.js middleware that spawns and manages MCP server processes

**Key Features**:
- **Process Management**: Spawns Python MCP server as child process
- **WebSocket Communication**: Real-time bidirectional communication
- **Error Handling**: Process monitoring and restart capabilities
- **CORS Support**: Cross-origin requests for frontend integration
- **Tool Discovery**: Automatically discovers available MCP tools

### 4. Frontend Application (`frontend/src/`)

**Main Components**:

#### `DirectMCPChatbot.jsx` - Main chat interface with:
- **Message Management**: Conversation history with timestamps
- **AI Integration**: Multiple AI providers (OpenAI, Claude, Groq, Google)
- **Thinking Mode**: Shows AI reasoning process
- **Connection Management**: Handles MCP server connectivity
- **Error Handling**: User-friendly error messages

#### `directAiMcpService.js` - Service layer handling:
- **OpenAI Integration**: Uses GPT models for natural language processing
- **Conversation Memory**: Maintains chat history for context
- **Tool Calling**: Converts AI requests to MCP tool calls
- **Response Processing**: Formats AI responses with tool results

## 🔄 Complete Workflow & Code Explanation

### System Initialization Flow

#### 1. **Docker Container Startup** (`docker-compose.yml`)
```yaml
# Services start in dependency order:
postgres → backend-python → mcp-manager → frontend
```

**How it works**:
- **PostgreSQL** starts first with health checks
- **Backend Python** waits for database health check to pass
- **MCP Manager** waits for backend to be ready
- **Frontend** starts last and connects to all services

#### 2. **Database Initialization** (`backend-python/database.py`)
```python
# Auto-creates all tables on startup
Base.metadata.create_all(bind=engine)

# Migrates existing JSON data if available
def migrate_json_to_db():
    # Reads users.json and populates database
    for user_data in users_data:
        user = LegacyUser(name=user_data["name"], ...)
        db.add(user)
```

**Working Mechanism**:
- SQLAlchemy models define database schema
- Auto-generates UUID primary keys
- Establishes foreign key relationships
- Creates indexes for performance

#### 3. **MCP Server Startup** (`backend-python/comprehensive_server.py`)
```python
# FastMCP initializes and registers all tools
mcp = FastMCP("hospital-management-system")

@mcp.tool()
def create_patient(patient_number: str, first_name: str, ...):
    # Tool automatically becomes available to AI
    db = get_db_session()
    patient = Patient(patient_number=patient_number, ...)
    db.add(patient)
    db.commit()
    return serialize_model(patient)
```

**How Tools Work**:
- Each `@mcp.tool()` decorator registers a function as an AI tool
- Functions include type hints for automatic parameter validation
- Database sessions handle transactions automatically
- Return values are serialized to JSON for AI consumption

### User Interaction Flow

#### 1. **Frontend Loading** (`frontend/src/App.jsx`)
```jsx
function App() {
  return (
    <div className="App">
      <DirectMCPChatbot />  {/* Main chatbot interface */}
    </div>
  );
}
```

#### 2. **Chatbot Initialization** (`frontend/src/components/DirectMCPChatbot.jsx`)
```jsx
const initializeService = async () => {
  // Create MCP service instance
  aiMcpServiceRef.current = new DirectAIMCPService();
  
  // Connect to MCP process manager
  const initialized = await aiMcpServiceRef.current.initialize(
    openaiApiKey,
    containerizedConfig  // Points to Python MCP server
  );
  
  if (initialized) {
    setIsConnected(true);
    // Ready to process user queries
  }
};
```

**Working Flow**:
1. User enters OpenAI API key
2. Frontend creates `DirectAIMCPService` instance
3. Service connects to MCP Process Manager on port 3001
4. Process Manager spawns Python MCP server process
5. Connection established, tools discovered

#### 3. **Message Processing** (`frontend/src/services/directAiMcpService.js`)
```javascript
async processRequest(userMessage) {
  // Add to conversation history for context
  this.addToConversationHistory('user', userMessage);
  
  // Get available tools from MCP server
  const tools = await this.mcpClient.getTools();
  
  // Send to OpenAI with tools and conversation context
  const response = await this.callOpenAI(userMessage, tools);
  
  // If AI wants to use tools, execute them
  if (response.tool_calls) {
    for (const toolCall of response.tool_calls) {
      const result = await this.mcpClient.callTool(
        toolCall.function.name,
        JSON.parse(toolCall.function.arguments)
      );
      // Add tool results to conversation
    }
  }
  
  return finalResponse;
}
```

**Step-by-Step Process**:
1. **User Input**: User types natural language query
2. **Context Building**: Add message to conversation history
3. **Tool Discovery**: Get current available MCP tools
4. **AI Processing**: Send to OpenAI with tools and context
5. **Tool Execution**: If AI decides to use tools, execute them
6. **Result Integration**: Combine AI response with tool results
7. **Response Display**: Show final response to user

### Deep Dive: MCP Communication Flow

#### 1. **Process Manager Bridge** (`mcp-process-manager/server.js`)
```javascript
class MCPProcessManager {
  async startMCPServer(config) {
    // Spawn Python MCP server as child process
    this.mcpProcess = spawn(config.command, config.args, spawnOptions);
    
    // Set up JSON-RPC communication
    this.mcpProcess.stdout.on('data', (data) => {
      const messages = data.toString().split('\n');
      messages.forEach(msg => this.handleMCPMessage(msg));
    });
  }
  
  async callTool(toolName, args) {
    // Create JSON-RPC request
    const request = {
      jsonrpc: "2.0",
      id: ++this.requestId,
      method: "tools/call",
      params: { name: toolName, arguments: args }
    };
    
    // Send to Python process and wait for response
    return new Promise((resolve) => {
      this.pendingRequests.set(request.id, resolve);
      this.mcpProcess.stdin.write(JSON.stringify(request) + '\n');
    });
  }
}
```

**Communication Protocol**:
1. **HTTP/WebSocket Layer**: Frontend ↔ Process Manager
2. **JSON-RPC Layer**: Process Manager ↔ Python MCP Server
3. **Database Layer**: MCP Server ↔ PostgreSQL

#### 2. **Tool Execution Chain**
```
User: "Create patient John Doe"
     ↓
Frontend: DirectMCPChatbot.sendMessage()
     ↓
Service: DirectAIMCPService.processRequest()
     ↓
OpenAI: Analyzes request, decides to call create_patient tool
     ↓
Client: DirectMCPClient.callTool("create_patient", {...})
     ↓
Manager: MCPProcessManager.callTool() via JSON-RPC
     ↓
Server: comprehensive_server.create_patient() function
     ↓
Database: INSERT INTO patients VALUES (...)
     ↓
Response: Patient record returned through chain
     ↓
Display: "✅ Patient John Doe created successfully"
```

### Example Interactions with Code Flow

#### **Scenario 1: Creating a Patient**
```
User Input: "Create a new patient named John Doe, born on 1990-05-15"
```

**Code Execution Flow**:

1. **Frontend Processing** (`DirectMCPChatbot.jsx`):
```jsx
const sendMessage = async () => {
  const userMessage = inputMessage.trim();
  
  // Add user message to chat
  setMessages(prev => [...prev, {
    text: userMessage,
    sender: 'user',
    timestamp: new Date().toLocaleTimeString()
  }]);
  
  // Process with AI service
  const response = await aiMcpServiceRef.current.processRequest(userMessage);
};
```

2. **AI Service Processing** (`directAiMcpService.js`):
```javascript
async processRequest(userMessage) {
  // Get available tools
  const tools = await this.mcpClient.getTools();
  
  // Send to OpenAI with context
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    headers: { 'Authorization': `Bearer ${this.openaiApiKey}` },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: this.conversationHistory,
      tools: tools,  // Include hospital management tools
      tool_choice: 'auto'
    })
  });
  
  // AI decides to call create_patient tool
  if (response.tool_calls) {
    const toolCall = response.tool_calls[0];
    // toolCall.function.name = "create_patient"
    // toolCall.function.arguments = {"patient_number": "P001", "first_name": "John", ...}
    
    const result = await this.mcpClient.callTool(
      toolCall.function.name,
      JSON.parse(toolCall.function.arguments)
    );
  }
}
```

3. **MCP Client Communication** (`directMcpClient.js`):
```javascript
async callTool(toolName, args) {
  const response = await fetch(`${this.baseUrl}/mcp/call-tool`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tool: toolName,
      arguments: args
    })
  });
  
  return response.json();
}
```

4. **Process Manager Execution** (`server.js`):
```javascript
app.post('/mcp/call-tool', async (req, res) => {
  const { tool, arguments } = req.body;
  
  try {
    // Forward to Python MCP server via JSON-RPC
    const result = await mcpManager.callTool(tool, arguments);
    res.json({ success: true, result });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});
```

5. **Python MCP Server Execution** (`comprehensive_server.py`):
```python
@mcp.tool()
def create_patient(patient_number: str, first_name: str, last_name: str, 
                  date_of_birth: str, gender: str = None, phone: str = None,
                  email: str = None, address: str = None) -> Dict[str, Any]:
    """Create a new patient."""
    if not DATABASE_AVAILABLE:
        return {"error": "Database not available"}
    
    db = get_db_session()
    try:
        # Parse date string to date object
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        
        # Create new patient record
        patient = Patient(
            patient_number=patient_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            phone=phone,
            email=email,
            address=address
        )
        
        # Save to database
        db.add(patient)
        db.commit()
        
        # Return serialized patient data
        return {
            "success": True,
            "message": f"Patient {first_name} {last_name} created successfully",
            "patient": serialize_model(patient)
        }
        
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create patient: {str(e)}"}
    finally:
        db.close()
```

**Database Impact**:
```sql
-- Generated SQL by SQLAlchemy
INSERT INTO patients (
    id, patient_number, first_name, last_name, 
    date_of_birth, gender, phone, email, address,
    created_at, updated_at
) VALUES (
    gen_random_uuid(), 'P001', 'John', 'Doe',
    '1990-05-15', NULL, NULL, NULL, NULL,
    NOW(), NOW()
);
```

**Final Response Chain**:
```
Database → Python MCP → Process Manager → Frontend → User
"✅ Patient John Doe (P001) created successfully. 
 Patient ID: 550e8400-e29b-41d4-a716-446655440000"
```

#### **Scenario 2: Checking Bed Availability**
```
User Input: "Show me all available beds in the ICU department"
```

**Code Execution Flow**:

1. **AI Analysis**: OpenAI determines this requires two tool calls:
   - `list_departments` (to find ICU department ID)
   - `list_beds` (to filter by department and status)

2. **Tool Call Sequence**:
```javascript
// First tool call
await mcpClient.callTool('list_departments', {});
// Returns: [{id: "dept-123", name: "ICU", ...}, ...]

// AI extracts ICU department ID
const icuDeptId = "dept-123";

// Second tool call
await mcpClient.callTool('list_beds', {
  status: 'available',
  department_filter: icuDeptId
});
```

3. **Python Tool Execution**:
```python
@mcp.tool()
def list_beds(status: str = None) -> Dict[str, Any]:
    """List all beds, optionally filtered by status."""
    db = get_db_session()
    try:
        query = db.query(Bed)
        if status:
            query = query.filter(Bed.status == status)
        
        beds = query.all()
        return {
            "success": True,
            "beds": [serialize_model(bed) for bed in beds],
            "total_count": len(beds)
        }
    finally:
        db.close()
```

4. **SQL Query Generated**:
```sql
SELECT beds.id, beds.bed_number, beds.room_id, beds.status,
       rooms.room_number, departments.name as dept_name
FROM beds 
JOIN rooms ON beds.room_id = rooms.id
JOIN departments ON rooms.department_id = departments.id
WHERE beds.status = 'available' 
  AND departments.id = 'dept-123';
```

5. **AI Response Formatting**:
```
"I found 5 available beds in the ICU department:
- Bed ICU-01 in Room 301
- Bed ICU-02 in Room 301  
- Bed ICU-05 in Room 302
- Bed ICU-08 in Room 303
- Bed ICU-12 in Room 305

All beds are ready for patient assignment."
```

### Error Handling & Recovery

#### **Database Connection Issues**
```python
def get_db_session() -> Session:
    """Get database session with error handling."""
    try:
        return SessionLocal()
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise Exception("Database unavailable")
```

#### **MCP Process Recovery**
```javascript
// Process Manager monitors child process
this.mcpProcess.on('exit', (code) => {
  console.log(`MCP process exited with code ${code}`);
  if (code !== 0) {
    // Attempt restart
    this.restartMCPServer();
  }
});
```

#### **Frontend Error Handling**
```jsx
const sendMessage = async () => {
  try {
    const response = await aiMcpServiceRef.current.processRequest(userMessage);
    // Handle successful response
  } catch (error) {
    setMessages(prev => [...prev, {
      text: `❌ Error: ${error.message}`,
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    }]);
  }
};
```

## 🛠️ Technology Stack

### Backend
- **Python 3.12+** with FastMCP framework
- **PostgreSQL 15** for data persistence
- **SQLAlchemy 2.0** for ORM and migrations
- **Pydantic** for data validation
- **FastAPI** for web framework

### Frontend
- **React 19** with Vite build system
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Markdown** for message formatting
- **Axios** for HTTP requests

### Infrastructure
- **Docker & Docker Compose** for containerization
- **Node.js** for MCP process management
- **WebSockets** for real-time communication
- **Nginx** for frontend serving

## 🎯 Key Features & Technical Implementation

- ✅ **Complete Hospital Management**: Patients, staff, departments, equipment, supplies
  - *Implementation*: 12 database models with full CRUD operations via MCP tools
  - *Code*: SQLAlchemy ORM with automatic relationship mapping and UUID primary keys

- ✅ **AI-Powered Interface**: Natural language interaction with hospital data  
  - *Implementation*: OpenAI GPT-4 with function calling, conversation memory, and context awareness
  - *Code*: Tool descriptions auto-generated from Python function signatures and docstrings

- ✅ **Real-time Operations**: Live updates through WebSocket connections
  - *Implementation*: Express.js WebSocket server with process monitoring and automatic reconnection
  - *Code*: Event-driven architecture with message queuing and error recovery

- ✅ **Multi-AI Support**: Works with OpenAI, Claude, Groq, and Google AI
  - *Implementation*: Abstracted AI service layer with provider-specific adapters
  - *Code*: Environment variable configuration for seamless provider switching

- ✅ **Containerized Deployment**: Easy setup with Docker
  - *Implementation*: Multi-stage Docker builds with health checks and dependency management
  - *Code*: Docker Compose orchestration with network isolation and volume persistence

- ✅ **Comprehensive Logging**: All AI interactions are tracked
  - *Implementation*: Database logging with interaction metadata, performance metrics, and audit trails
  - *Code*: `AgentInteraction` model captures query, response, execution time, and confidence scores

- ✅ **Scalable Architecture**: Modular design for easy expansion
  - *Implementation*: Microservices pattern with clear separation of concerns
  - *Code*: Plugin-based tool registration system for adding new hospital management features

## 🔧 Code Architecture Deep Dive

### 1. **Database Layer Architecture**

#### **Model Relationships**
```python
# Example: Patient-Bed-Room-Department relationship chain
class Patient(Base):
    beds = relationship("Bed", back_populates="patient")  # One-to-many
    
class Bed(Base):
    patient_id = Column(UUID, ForeignKey("patients.id"))  # Many-to-one
    patient = relationship("Patient", back_populates="beds")
    room = relationship("Room", back_populates="beds")
    
class Room(Base):
    department = relationship("Department", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")
```

**How it Works**:
- **Automatic Join Queries**: SQLAlchemy automatically generates JOIN statements
- **Lazy Loading**: Related objects loaded on-demand for performance
- **Cascade Operations**: Deleting a room can cascade to beds if configured

#### **Case-Insensitive Patient Search Implementation**
```python
@mcp.tool()
def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """Get a patient by ID or patient number (case-insensitive)."""
    try:
        # First try UUID format
        patient_uuid = uuid.UUID(patient_id)
        patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
    except ValueError:
        # If not UUID, search by patient_number using case-insensitive ILIKE
        patient = db.query(Patient).filter(
            Patient.patient_number.ilike(patient_id)  # Case-insensitive search
        ).first()
```

**How it Works**:
- **ILIKE Operator**: PostgreSQL's case-insensitive LIKE operator
- **Flexible Matching**: `pat-em-9925` matches `PAT-EM-9925`
- **UUID Handling**: Still supports exact UUID matches
- **Backward Compatible**: All existing queries continue to work

#### **Enhanced Search Capabilities**
```python
@mcp.tool()
def search_patients(patient_number: str = None, first_name: str = None, ...):
    """All search parameters support case-insensitive partial matching."""
    # Uses ILIKE with wildcards for flexible searching
    if patient_number:
        query = query.filter(Patient.patient_number.ilike(f"%{patient_number}%"))
    if first_name:
        query = query.filter(Patient.first_name.ilike(f"%{first_name}%"))
```

**Search Examples**:
- `search_patients(first_name="john")` finds "John", "JOHN", "Johnny"
- `search_patients(patient_number="em-99")` finds "PAT-EM-9925", "DOC-EM-9901"

### 2. **MCP Tool Registration System**

#### **Automatic Tool Discovery**
```python
@mcp.tool()  # Decorator automatically registers function as MCP tool
def create_patient(patient_number: str, first_name: str, ...) -> Dict[str, Any]:
    """Create a new patient."""  # Docstring becomes tool description
    # Function parameters become tool parameters with type validation
```

**Tool Schema Generation**:
```json
{
  "name": "create_patient",
  "description": "Create a new patient.",
  "parameters": {
    "type": "object",
    "properties": {
      "patient_number": {"type": "string"},
      "first_name": {"type": "string"},
      "last_name": {"type": "string"}
    },
    "required": ["patient_number", "first_name", "last_name"]
  }
}
```

### 3. **Frontend State Management**

#### **Message State Flow**
```jsx
// Message state with conversation context
const [messages, setMessages] = useState([]);
const [conversationHistory, setConversationHistory] = useState([]);

// Add message with automatic scrolling
const addMessage = (message) => {
  setMessages(prev => [...prev, {
    ...message,
    id: Date.now(),
    timestamp: new Date().toLocaleTimeString()
  }]);
  
  // Auto-scroll to bottom
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
};
```

#### **Connection State Management**
```jsx
const [isConnected, setIsConnected] = useState(false);
const [connectionError, setConnectionError] = useState('');

useEffect(() => {
  // Monitor connection status
  const checkConnection = async () => {
    try {
      const status = await mcpClient.getStatus();
      setIsConnected(status.connected);
    } catch (error) {
      setIsConnected(false);
      setConnectionError(error.message);
    }
  };
  
  const interval = setInterval(checkConnection, 5000);
  return () => clearInterval(interval);
}, []);
```

### 4. **Process Communication Protocol**

#### **JSON-RPC Message Format**
```javascript
// Request from Process Manager to MCP Server
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "tools/call",
  "params": {
    "name": "create_patient",
    "arguments": {
      "patient_number": "P001",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}

// Response from MCP Server
{
  "jsonrpc": "2.0",
  "id": 123,
  "result": {
    "success": true,
    "message": "Patient created successfully",
    "patient": { /* patient data */ }
  }
}
```

#### **Process Lifecycle Management**
```javascript
class MCPProcessManager {
  constructor() {
    this.mcpProcess = null;
    this.isConnected = false;
    this.pendingRequests = new Map();  // Track ongoing requests
    this.requestId = 0;
  }
  
  async startMCPServer(config) {
    // Spawn process with proper stdio configuration
    this.mcpProcess = spawn(config.command, config.args, {
      stdio: ['pipe', 'pipe', 'pipe'],  // stdin, stdout, stderr
      env: { ...process.env, ...config.env }
    });
    
    // Set up message handling
    this.setupMessageHandling();
    this.setupErrorHandling();
    this.setupProcessMonitoring();
  }
}
```

## 📁 Project Structure

```
hospital-management-system/
├── backend-python/              # Python MCP Server
│   ├── comprehensive_server.py  # Main MCP server with tools
│   ├── database.py             # Database models and setup
│   ├── pyproject.toml          # Python dependencies
│   └── Dockerfile              # Backend container config
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API services
│   │   └── App.jsx            # Main app component
│   ├── package.json           # Frontend dependencies
│   └── Dockerfile             # Frontend container config
├── mcp-process-manager/        # Node.js MCP Manager
│   ├── server.js              # Process management server
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile             # Manager container config
├── docker-compose.yml          # Multi-container orchestration
├── deploy.bat                  # Windows deployment script
├── deploy.sh                   # Linux/Mac deployment script
└── README.md                   # This file
```

## 🔧 Development & Management Commands

### Docker Management
```bash
# Start all services
deploy.bat start          # Windows
./deploy.sh start         # Linux/Mac

# Stop all services
deploy.bat stop           # Windows
./deploy.sh stop          # Linux/Mac

# View logs
deploy.bat logs           # Windows
./deploy.sh logs          # Linux/Mac

# Clean up
deploy.bat cleanup        # Windows
./deploy.sh cleanup       # Linux/Mac
```

### Manual Docker Commands
```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Development Workflow Commands

#### **Database Operations**
```bash
# Access PostgreSQL directly
docker exec -it hospital-postgres psql -U postgres -d hospital_management

# View database logs
docker logs hospital-postgres

# Backup database
docker exec hospital-postgres pg_dump -U postgres hospital_management > backup.sql

# Restore database
docker exec -i hospital-postgres psql -U postgres hospital_management < backup.sql
```

#### **Backend Development**
```bash
# Access Python container
docker exec -it hospital-backend-python bash

# Run Python shell with database access
docker exec -it hospital-backend-python python3 -c "
from database import SessionLocal, Patient
db = SessionLocal()
patients = db.query(Patient).all()
print(f'Total patients: {len(patients)}')
"

# Test MCP server directly
docker exec -it hospital-backend-python python3 comprehensive_server.py
```

#### **Frontend Development**
```bash
# Access frontend container
docker exec -it hospital-frontend sh

# View build logs
docker logs hospital-frontend

# Rebuild frontend only
docker-compose build frontend
docker-compose up -d frontend
```

#### **MCP Process Manager Debug**
```bash
# View MCP manager logs
docker logs hospital-mcp-manager

# Test MCP endpoint directly
curl http://localhost:3001/tools

# Monitor WebSocket connections
curl -H "Upgrade: websocket" -H "Connection: Upgrade" \
     -H "Sec-WebSocket-Key: test" http://localhost:3001/
```

### Performance Monitoring

#### **Database Performance**
```sql
-- Connect to PostgreSQL and run performance queries
docker exec -it hospital-postgres psql -U postgres -d hospital_management

-- Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public';

-- Check active connections
SELECT 
    pid, 
    usename, 
    application_name, 
    client_addr, 
    state,
    query_start,
    query
FROM pg_stat_activity;

-- Index usage statistics
SELECT 
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes;
```

#### **Container Resource Usage**
```bash
# Monitor container resource usage
docker stats

# Specific container monitoring
docker stats hospital-postgres hospital-backend-python hospital-mcp-manager hospital-frontend

# Memory usage by container
docker exec hospital-backend-python cat /proc/meminfo

# Disk usage
docker system df
```

#### **Application Performance Metrics**
```bash
# API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3001/tools

# Database query performance
docker exec -it hospital-postgres psql -U postgres -d hospital_management -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### Code Quality & Testing

#### **Python Code Quality**
```bash
# Run in backend-python directory
docker exec -it hospital-backend-python bash

# Install development dependencies
pip install black isort flake8 mypy pytest

# Format code
black comprehensive_server.py database.py

# Sort imports
isort comprehensive_server.py database.py

# Lint code
flake8 comprehensive_server.py database.py

# Type checking
mypy comprehensive_server.py database.py
```

#### **Frontend Code Quality**
```bash
# Access frontend container
docker exec -it hospital-frontend sh

# Run ESLint
npm run lint

# Fix linting issues
npm run lint -- --fix

# Build optimization analysis
npm run build -- --analyze
```

#### **Testing Commands**
```bash
# Backend testing
docker exec -it hospital-backend-python python3 -m pytest tests/

# Frontend testing
docker exec -it hospital-frontend npm test

# Integration testing
docker exec -it hospital-mcp-manager npm test

# Load testing (using curl)
for i in {1..100}; do
  curl -X POST http://localhost:3001/mcp/call-tool \
    -H "Content-Type: application/json" \
    -d '{"tool": "list_patients", "arguments": {}}' &
done
wait
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   ```bash
   # Check PostgreSQL container
   docker logs hospital-postgres
   
   # Verify database is ready
   docker exec -it hospital-postgres pg_isready -U postgres
   ```

2. **MCP Server Issues**:
   ```bash
   # Check backend logs
   docker logs hospital-backend-python
   
   # Verify MCP tools are available
   curl http://localhost:3001/tools
   ```

3. **Frontend Not Loading**:
   ```bash
   # Check frontend container
   docker logs hospital-frontend
   
   # Verify environment variables
   docker exec -it hospital-frontend env | grep VITE_
   ```

4. **Patient ID Format Issues**:
   ```
   Error: "badly formed hexadecimal UUID string"
   
   Solution: Use the correct ID format:
   - UUID format: 550e8400-e29b-41d4-a716-446655440000
   - Patient number: PAT-EM-9925, pat-em-9925, Pat-Em-9925 (case-insensitive)
   - Or use search_patients tool to find by name/phone/email
   ```

### Common User Query Issues

1. **Finding Patients (Case-Insensitive)**:
   ```
   ✅ All of these work now:
   - "Get patient PAT-EM-9925"
   - "Get patient pat-em-9925" 
   - "Get patient Pat-Em-9925"
   - "Search for patient with number pat-em-9925"
   - "Find patient named john doe"
   - "Search for patient with phone 555-1234"
   ```

2. **Using Correct Tools**:
   ```
   # For human-readable IDs (case-insensitive), use either tool:
   User: "Find patient pat-em-9925"
   AI: Uses get_patient_by_id(patient_id="pat-em-9925") ✅
   AI: Or uses search_patients(patient_number="pat-em-9925") ✅
   
   # For UUID lookups:
   User: "Get details for patient 550e8400-e29b-41d4-a716-446655440000"
   AI: Uses get_patient_by_id(patient_id="550e8400-e29b-41d4-a716-446655440000")
   
   # For flexible searches (all case-insensitive):
   User: "Find patient named JOHN DOE"
   AI: Uses search_patients(first_name="JOHN", last_name="DOE") ✅
   ```

### Port Conflicts
If you encounter port conflicts, modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8080:80"    # Frontend (change from 80:80)
  - "3002:3001"  # MCP Manager (change from 3001:3001)
  - "8001:8000"  # Backend (change from 8000:8000)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review Docker logs for specific error messages

---

**Built with ❤️ for modern healthcare management**
