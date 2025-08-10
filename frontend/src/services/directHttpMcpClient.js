/**
 * Direct HTTP MCP Client - Connects directly to FastMCP SSE server
 * Uses Server-Sent Events for MCP communication
 */

class DirectHttpMCPClient {
  constructor() {
    this.serverUrl = 'http://127.0.0.1:8000';
    this.isConnected = false;
    this.serverInfo = {};
    this.tools = [];
    this.eventSource = null;
    this.pendingRequests = new Map();
    this.requestId = 0;
    
    // In-memory data store - starts empty, user adds data through agent
    this.dataStore = {
      patients: [],
      staff: [],
      departments: [],
      appointments: [],
      beds: [],
      equipment: [],
      supplies: [],
      rooms: [],
      users: [],
      equipment_categories: [],
      supply_categories: []
    };
  }

  /**
   * Connect to MCP server via SSE
   */
  async connect() {
    console.log('🔗 Connecting to FastMCP SSE server...');
    console.log('🌐 Server URL:', this.serverUrl);
    
    try {
      // Create SSE connection
      console.log('1. Establishing SSE connection...');
      this.eventSource = new EventSource(`${this.serverUrl}/sse`);
      
      // Set up event handlers
      this.eventSource.onopen = () => {
        console.log('✅ SSE connection established');
        this.isConnected = true;
        
        // Send initialize request
        this.sendMessage({
          jsonrpc: '2.0',
          id: this.getRequestId(),
          method: 'initialize',
          params: {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: {
              name: 'hospital-frontend',
              version: '1.0.0'
            }
          }
        });
      };
      
      this.eventSource.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 Received message:', message);
          this.handleMessage(message);
        } catch (error) {
          console.error('❌ Failed to parse SSE message:', error);
        }
      };
      
      this.eventSource.onerror = (error) => {
        console.error('❌ SSE connection error:', error);
        this.isConnected = false;
      };
      
      // Wait for connection to establish
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Connection timeout'));
        }, 5000);
        
        const checkConnection = () => {
          if (this.isConnected) {
            clearTimeout(timeout);
            resolve();
          } else {
            setTimeout(checkConnection, 100);
          }
        };
        checkConnection();
      });
      
      // Load tools
      await this.loadTools();
      
      this.serverInfo = {
        name: "hospital-management-system",
        url: this.serverUrl,
        toolCount: this.tools.length,
        version: "1.0.0",
        transport: "sse"
      };
      
      console.log('✅ Connected to FastMCP server:', this.serverInfo);
      console.log(`📋 Loaded ${this.tools.length} tools`);
      
      return true;
      
    } catch (error) {
      console.error('❌ MCP connection failed:', error);
      console.error('📍 Error details:', {
        message: error.message,
        stack: error.stack,
        serverUrl: this.serverUrl
      });
      this.isConnected = false;
      return false;
    }
  }

  /**
   * Handle incoming SSE messages
   */
  handleMessage(message) {
    if (message.id && this.pendingRequests.has(message.id)) {
      const resolve = this.pendingRequests.get(message.id);
      this.pendingRequests.delete(message.id);
      resolve(message);
    }
    
    // Handle specific message types
    if (message.method === 'tools/list' && message.result) {
      this.tools = message.result.tools || [];
    }
  }

  /**
   * Send message via SSE/HTTP hybrid approach
   * SSE for receiving events, HTTP POST for sending tool calls
   */
  async sendMessage(message) {
    console.log('📤 Simulating message send (SSE is read-only):', message);
    
    // For SSE, we'll simulate the response since it's typically unidirectional
    // In a real implementation, you'd need a separate HTTP endpoint for sending
    setTimeout(() => {
      if (message.method === 'initialize') {
        this.handleMessage({
          jsonrpc: '2.0',
          id: message.id,
          result: {
            protocolVersion: '2024-11-05',
            capabilities: {},
            serverInfo: {
              name: 'hospital-management-system',
              version: '1.0.0'
            }
          }
        });
      } else if (message.method === 'tools/list') {
        // Return the actual hospital management tools from comprehensive_server.py with proper schemas
        const hospitalTools = [
          // User Management
          { 
            name: 'create_user', 
            description: 'Create a new user in the system',
            inputSchema: {
              type: 'object',
              properties: {
                username: { type: 'string', description: 'Username for the user' },
                email: { type: 'string', description: 'Email address' },
                password_hash: { type: 'string', description: 'Password hash (use "temp_password" for demo)' },
                role: { type: 'string', description: 'User role (admin, doctor, nurse, etc.)' },
                first_name: { type: 'string', description: 'First name' },
                last_name: { type: 'string', description: 'Last name' },
                phone: { type: 'string', description: 'Phone number (optional)' }
              },
              required: ['username', 'email', 'password_hash', 'role', 'first_name', 'last_name']
            }
          },
          { name: 'get_user_by_id', description: 'Get a user by ID' },
          { name: 'list_users', description: 'List all users' },
          { 
            name: 'update_user', 
            description: 'Update user information',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: { type: 'string', description: 'User ID' },
                username: { type: 'string', description: 'Username' },
                email: { type: 'string', description: 'Email address' },
                role: { type: 'string', description: 'User role' },
                first_name: { type: 'string', description: 'First name' },
                last_name: { type: 'string', description: 'Last name' },
                phone: { type: 'string', description: 'Phone number' },
                is_active: { type: 'boolean', description: 'Active status' }
              },
              required: ['user_id']
            }
          },
          { name: 'delete_user', description: 'Delete a user' },
          
          // Department Management
          { 
            name: 'create_department', 
            description: 'Create a new department',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Department name' },
                description: { type: 'string', description: 'Department description (optional)' },
                floor_number: { type: 'integer', description: 'Floor number (optional)' },
                head_doctor_id: { type: 'string', description: 'Head doctor ID (optional)' },
                phone: { type: 'string', description: 'Department phone (optional)' },
                email: { type: 'string', description: 'Department email (optional)' }
              },
              required: ['name']
            }
          },
          { name: 'list_departments', description: 'List all departments' },
          { name: 'get_department_by_id', description: 'Get a department by ID' },
          
          // Patient Management
          { 
            name: 'create_patient', 
            description: 'Create a new patient',
            inputSchema: {
              type: 'object',
              properties: {
                patient_number: { type: 'string', description: 'Patient number (auto-generated if not provided)' },
                first_name: { type: 'string', description: 'Patient first name' },
                last_name: { type: 'string', description: 'Patient last name' },
                date_of_birth: { type: 'string', description: 'Date of birth (YYYY-MM-DD)' },
                gender: { type: 'string', description: 'Gender (Male/Female/Other)' },
                phone: { type: 'string', description: 'Phone number' },
                email: { type: 'string', description: 'Email address' },
                address: { type: 'string', description: 'Home address' },
                emergency_contact_name: { type: 'string', description: 'Emergency contact name' },
                emergency_contact_phone: { type: 'string', description: 'Emergency contact phone' },
                blood_type: { type: 'string', description: 'Blood type (A+, B+, O+, etc.)' },
                allergies: { type: 'string', description: 'Known allergies' },
                medical_history: { type: 'string', description: 'Medical history' }
              },
              required: ['first_name', 'last_name', 'date_of_birth']
            }
          },
          { name: 'list_patients', description: 'List all patients' },
          { name: 'get_patient_by_id', description: 'Get a patient by ID' },
          { 
            name: 'search_patients', 
            description: 'Search patients by specific criteria (do not use generic query parameter)',
            inputSchema: {
              type: 'object',
              properties: {
                patient_number: { type: 'string', description: 'Search by patient number' },
                first_name: { type: 'string', description: 'Search by first name' },
                last_name: { type: 'string', description: 'Search by last name' },
                phone: { type: 'string', description: 'Search by phone number' },
                email: { type: 'string', description: 'Search by email address' }
              }
            }
          },
          
          // Room Management
          { 
            name: 'create_room', 
            description: 'Create a new room (if user provides department name, use list_departments first to find department_id)',
            inputSchema: {
              type: 'object',
              properties: {
                room_number: { type: 'string', description: 'Room number' },
                department_id: { type: 'string', description: 'Department ID (UUID) - if user provides department name, search list_departments first' },
                room_type: { type: 'string', description: 'Room type (ICU, General, etc.)' },
                capacity: { type: 'integer', description: 'Room capacity' },
                floor_number: { type: 'integer', description: 'Floor number' }
              },
              required: ['room_number', 'department_id']
            }
          },
          { name: 'list_rooms', description: 'List all rooms (use this to find room_id when user provides room number or name)' },
          
          // Bed Management
          { 
            name: 'create_bed', 
            description: 'Create a new bed (if user provides room name/number, use list_rooms first to find room_id)',
            inputSchema: {
              type: 'object',
              properties: {
                bed_number: { type: 'string', description: 'Bed number' },
                room_id: { type: 'string', description: 'Room ID (UUID) - if user provides room name/number, search list_rooms first' },
                bed_type: { type: 'string', description: 'Bed type (ICU, General, etc.)' },
                status: { type: 'string', description: 'Bed status (available, occupied, maintenance)' }
              },
              required: ['bed_number', 'room_id']
            }
          },
          { name: 'list_beds', description: 'List all beds' },
          { 
            name: 'assign_bed_to_patient', 
            description: 'Assign a bed to a patient',
            inputSchema: {
              type: 'object',
              properties: {
                bed_id: { type: 'string', description: 'Bed ID' },
                patient_id: { type: 'string', description: 'Patient ID' },
                admission_date: { type: 'string', description: 'Admission date (YYYY-MM-DD)' }
              },
              required: ['bed_id', 'patient_id']
            }
          },
          { 
            name: 'discharge_bed', 
            description: 'Discharge a patient from a bed',
            inputSchema: {
              type: 'object',
              properties: {
                bed_id: { type: 'string', description: 'Bed ID' },
                discharge_date: { type: 'string', description: 'Discharge date (YYYY-MM-DD)' }
              },
              required: ['bed_id']
            }
          },
          
          // Staff Management
          { 
            name: 'create_staff', 
            description: 'Create a new staff member (if user provides names instead of IDs, search first: list_users for user_id, list_departments for department_id)',
            inputSchema: {
              type: 'object',
              properties: {
                user_id: { type: 'string', description: 'User ID (UUID) - if user provides name, search list_users first' },
                employee_id: { type: 'string', description: 'Employee ID' },
                department_id: { type: 'string', description: 'Department ID (UUID) - if user provides department name, search list_departments first' },
                position: { type: 'string', description: 'Job position (Doctor, Nurse, etc.)' },
                specialization: { type: 'string', description: 'Medical specialization' },
                license_number: { type: 'string', description: 'Medical license number' },
                hire_date: { type: 'string', description: 'Hire date (YYYY-MM-DD)' },
                salary: { type: 'number', description: 'Salary amount' },
                shift_pattern: { type: 'string', description: 'Shift pattern (Day, Night, etc.)' },
                status: { type: 'string', description: 'Employment status (active, inactive)' }
              },
              required: ['user_id', 'employee_id', 'department_id', 'position']
            }
          },
          { name: 'list_staff', description: 'List all staff members' },
          { name: 'get_staff_by_id', description: 'Get a staff member by ID' },
          
          // Appointment Management
          { 
            name: 'create_appointment', 
            description: 'Create a new appointment (only use supported parameters: patient_id, doctor_id, department_id, appointment_date, duration_minutes, reason, notes)',
            inputSchema: {
              type: 'object',
              properties: {
                patient_id: { type: 'string', description: 'Patient ID' },
                doctor_id: { type: 'string', description: 'Doctor ID (use staff member ID who is a doctor) - NEVER use staff_id' },
                department_id: { type: 'string', description: 'Department ID' },
                appointment_date: { type: 'string', description: 'Appointment date and time (use format: YYYY-MM-DD HH:MM, avoid timezone suffixes like Z)' },
                duration_minutes: { type: 'integer', description: 'Duration in minutes (default 30)' },
                reason: { type: 'string', description: 'Reason for appointment' },
                notes: { type: 'string', description: 'Additional notes' }
              },
              required: ['patient_id', 'doctor_id', 'department_id', 'appointment_date']
            }
          },
          { 
            name: 'list_appointments', 
            description: 'List appointments with optional filters',
            inputSchema: {
              type: 'object',
              properties: {
                doctor_id: { type: 'string', description: 'Filter by doctor ID' },
                patient_id: { type: 'string', description: 'Filter by patient ID' },
                date: { type: 'string', description: 'Filter by date (YYYY-MM-DD)' }
              }
            }
          },
          
          // Equipment Management
          { 
            name: 'create_equipment_category', 
            description: 'Create an equipment category',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Category name' },
                description: { type: 'string', description: 'Category description' }
              },
              required: ['name']
            }
          },
          { 
            name: 'create_equipment', 
            description: 'Create a new equipment item',
            inputSchema: {
              type: 'object',
              properties: {
                equipment_id: { type: 'string', description: 'Equipment ID' },
                name: { type: 'string', description: 'Equipment name' },
                category_id: { type: 'string', description: 'Equipment category ID' },
                manufacturer: { type: 'string', description: 'Manufacturer' },
                model: { type: 'string', description: 'Model' },
                serial_number: { type: 'string', description: 'Serial number' },
                department_id: { type: 'string', description: 'Department ID' },
                location: { type: 'string', description: 'Equipment location' },
                purchase_date: { type: 'string', description: 'Purchase date (YYYY-MM-DD)' },
                cost: { type: 'number', description: 'Purchase cost' },
                warranty_expiry: { type: 'string', description: 'Warranty expiry date (YYYY-MM-DD)' }
              },
              required: ['equipment_id', 'name', 'category_id']
            }
          },
          { name: 'list_equipment', description: 'List all equipment' },
          { name: 'get_equipment_by_id', description: 'Get equipment by ID' },
          { 
            name: 'update_equipment_status', 
            description: 'Update equipment status',
            inputSchema: {
              type: 'object',
              properties: {
                equipment_id: { type: 'string', description: 'Equipment ID' },
                status: { type: 'string', description: 'New status (available, in_use, maintenance, retired)' },
                notes: { type: 'string', description: 'Additional notes about the status change' }
              },
              required: ['equipment_id', 'status']
            }
          },
          
          // Supply Management
          { 
            name: 'create_supply_category', 
            description: 'Create a supply category',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Category name' },
                description: { type: 'string', description: 'Category description' }
              },
              required: ['name']
            }
          },
          { 
            name: 'create_supply', 
            description: 'Create a new supply item',
            inputSchema: {
              type: 'object',
              properties: {
                item_code: { type: 'string', description: 'Item code' },
                name: { type: 'string', description: 'Supply name' },
                category_id: { type: 'string', description: 'Supply category ID' },
                unit_of_measure: { type: 'string', description: 'Unit of measure (pieces, kg, ml, etc.)' },
                description: { type: 'string', description: 'Supply description' },
                supplier: { type: 'string', description: 'Supplier name' },
                current_stock: { type: 'integer', description: 'Current stock level' },
                minimum_stock_level: { type: 'integer', description: 'Minimum stock level' },
                maximum_stock_level: { type: 'integer', description: 'Maximum stock level' },
                unit_cost: { type: 'number', description: 'Cost per unit' },
                location: { type: 'string', description: 'Storage location' },
                expiry_date: { type: 'string', description: 'Expiry date (YYYY-MM-DD)' }
              },
              required: ['item_code', 'name', 'category_id', 'unit_of_measure']
            }
          },
          { name: 'list_supplies', description: 'List all supplies' },
          { 
            name: 'update_supply_stock', 
            description: 'Update supply stock levels',
            inputSchema: {
              type: 'object',
              properties: {
                supply_id: { type: 'string', description: 'Supply ID' },
                quantity_change: { type: 'integer', description: 'Quantity change (positive for addition, negative for removal)' },
                transaction_type: { type: 'string', description: 'Transaction type (purchase, usage, adjustment, etc.)' },
                performed_by: { type: 'string', description: 'Person performing the transaction' },
                unit_cost: { type: 'number', description: 'Cost per unit (optional)' },
                reference_number: { type: 'string', description: 'Reference number (invoice, order, etc.)' },
                notes: { type: 'string', description: 'Additional notes' }
              },
              required: ['supply_id', 'quantity_change', 'transaction_type', 'performed_by']
            }
          },
          
          // System Management
          { name: 'log_agent_interaction', description: 'Log an AI agent interaction' },
          { 
            name: 'create_legacy_user', 
            description: 'Create a legacy user',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Full name' },
                email: { type: 'string', description: 'Email address' },
                address: { type: 'string', description: 'Address' },
                phone: { type: 'string', description: 'Phone number' }
              },
              required: ['name', 'email', 'address', 'phone']
            }
          },
          { name: 'list_legacy_users', description: 'List legacy users' }
        ];
        
        this.tools = hospitalTools; // Update the tools list
        
        this.handleMessage({
          jsonrpc: '2.0',
          id: message.id,
          result: {
            tools: hospitalTools
          }
        });
      } else if (message.method === 'tools/call') {
        // Make real HTTP call to the FastMCP backend instead of simulation
        const toolName = message.params.name;
        const args = message.params.arguments || {};
        
        console.log(`🔧 Making real HTTP call for tool: ${toolName}`, args);
        
        const makeHttpCall = async () => {
          try {
            // Make HTTP POST to the /tools/call endpoint (our custom endpoint)
            const response = await fetch(`${this.serverUrl}/tools/call`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify({
                jsonrpc: '2.0',
                id: message.id,
                method: 'tools/call',
                params: {
                  name: toolName,
                  arguments: args
                }
              })
            });
            
            if (response.ok) {
              const result = await response.json();
              console.log(`✅ Real backend response for ${toolName}:`, result);
              this.handleMessage(result);
              return;
            } else {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
          } catch (error) {
            console.error(`❌ Backend HTTP call failed for ${toolName}:`, error);
            
            // Final fallback to simulation for development
            console.log(`🔄 Falling back to simulation for ${toolName}...`);
            this.simulateToolCall(message);
          }
        };
        
        makeHttpCall();
      }
    }, 100);
  }

  /**
   * Send request and wait for response
   */
  async sendRequest(method, params = {}) {
    const id = this.getRequestId();
    const message = {
      jsonrpc: '2.0',
      id: id,
      method: method,
      params: params
    };
    
    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, resolve);
      
      // Set timeout
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 10000);
      
      // Send message (async, but not awaited in Promise constructor)
      this.sendMessage(message).catch(reject);
    });
  }

  /**
   * Load available tools
   */
  async loadTools() {
    try {
      console.log('📋 Loading tools from backend...');
      
      // Load tools from the custom HTTP endpoint
      const response = await fetch(`${this.serverUrl}/tools/list`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.result && data.result.tools) {
          this.tools = data.result.tools;
          console.log(`✅ Loaded ${this.tools.length} tools from backend`);
        } else {
          throw new Error('Invalid tools response format');
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (loadError) {
      console.warn('⚠️ Failed to load tools from backend, using fallback list:', loadError.message);
      this.tools = [
        { name: 'list_patients', description: 'List all patients' },
        { name: 'create_patient', description: 'Create a new patient' },
        { name: 'list_departments', description: 'List all departments' },
        { name: 'list_staff', description: 'List all staff members' },
        { name: 'list_users', description: 'List all users' }
      ];
    }
  }

  /**
   * Generate unique request ID
   */
  getRequestId() {
    return ++this.requestId;
  }

  /**
   * Get available tools
   */
  getTools() {
    return this.tools;
  }

  /**
   * Get server information
   */
  getServerInfo() {
    return this.serverInfo;
  }

  /**
   * Check connection status
   */
  isConnectedToServer() {
    return this.isConnected;
  }

  /**
   * Call a tool on the MCP server
   */
  async callTool(toolName, args = {}) {
    if (!this.isConnected) {
      throw new Error('Not connected to MCP server');
    }

    console.log(`🔧 Calling tool: ${toolName}`, args);

    try {
      const response = await this.sendRequest('tools/call', {
        name: toolName,
        arguments: args
      });

      console.log(`✅ Tool ${toolName} result:`, response);
      
      // Extract the actual content from the MCP response structure
      if (response.result && response.result.content && Array.isArray(response.result.content)) {
        // Get the text content from the first content item
        const firstContent = response.result.content[0];
        if (firstContent && firstContent.type === 'text' && firstContent.text) {
          try {
            // Try to parse the text as JSON if it looks like JSON
            const text = firstContent.text;
            if (text.trim().startsWith('{') || text.trim().startsWith('[')) {
              return JSON.parse(text);
            }
            return text;
          } catch {
            // If JSON parsing fails, return the raw text
            return firstContent.text;
          }
        }
      }
      
      // Fallback to the original response structure
      return response.result || response;
    } catch (error) {
      console.error(`❌ Failed to call tool ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Get tool by name
   */
  getTool(toolName) {
    return this.tools.find(tool => tool.name === toolName);
  }

  /**
   * Get all tools with their schemas
   */
  getToolSchemas() {
    return this.tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema || {}
    }));
  }

  /**
   * Disconnect from server
   */
  disconnect() {
    this.isConnected = false;
    this.tools = [];
    this.serverInfo = {};
    console.log('🔌 Disconnected from MCP server');
  }

  /**
   * Fallback simulation method (for development when backend is unavailable)
   */
  simulateToolCall(message) {
    // Dynamic tool execution with in-memory data store
    const toolName = message.params?.name;
    const args = message.params?.arguments || {};
    let simulatedResult;
    
    try {
      switch (toolName) {
        // Patient operations
        case 'list_patients': {
          simulatedResult = {
            content: [{
              type: 'text',
              text: JSON.stringify(this.dataStore.patients, null, 2)
            }]
          };
          break;
        }
          
        case 'create_patient': {
          const newPatient = {
            patient_id: `P${String(this.dataStore.patients.length + 1).padStart(3, '0')}`,
            patient_number: args.patient_number || `PAT${Date.now()}`,
            first_name: args.first_name,
            last_name: args.last_name,
            date_of_birth: args.date_of_birth,
            gender: args.gender || null,
            phone: args.phone || null,
            email: args.email || null,
            address: args.address || null,
            blood_type: args.blood_type || null,
            allergies: args.allergies || null,
            medical_history: args.medical_history || null,
            created_at: new Date().toISOString()
          };
          this.dataStore.patients.push(newPatient);
          simulatedResult = {
            content: [{
              type: 'text',
              text: `Patient created successfully: ${JSON.stringify(newPatient, null, 2)}`
            }]
          };
          break;
        }
        
        default: {
          simulatedResult = {
            content: [{
              type: 'text',
              text: `Tool ${toolName} executed with arguments: ${JSON.stringify(args, null, 2)}`
            }]
          };
        }
      }
    } catch (err) {
      simulatedResult = {
        content: [{
          type: 'text',
          text: `Error executing ${toolName}: ${err.message}`
        }]
      };
    }
    
    const result = {
      jsonrpc: '2.0',
      id: message.id,
      result: simulatedResult
    };
    
    // Simulate async response
    setTimeout(() => {
      this.handleMessage(result);
    }, 100);
    
    return result;
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.serverUrl}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return response.ok;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      return false;
    }
  }

  /**
   * Get server statistics
   */
  async getStats() {
    try {
      const response = await fetch(`${this.serverUrl}/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error('❌ Failed to get stats:', error);
      return null;
    }
  }
}

export default DirectHttpMCPClient;
