/**
 * Direct MCP Client - Connects to hospital management MCP server
 * Similar to how Claude Desktop connects to MCP servers
 */

class MCPClient {
  constructor() {
    this.serverProcess = null;
    this.connected = false;
    this.tools = new Map();
    this.requestId = 0;
  }

  /**
   * Start the MCP server process and connect to it
   */
  async connect() {
    try {
      console.log('🚀 Starting MCP server connection...');
      
      // Start the MCP server process
      await this.startServer();
      
      // Initialize the connection
      await this.initialize();
      
      // List available tools
      await this.listTools();
      
      this.connected = true;
      console.log('✅ MCP Client connected successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to connect to MCP server:', error);
      return false;
    }
  }

  /**
   * Start the MCP server process
   */
  async startServer() {
    // For now, we'll assume the server is already running
    // In a real implementation, you might start the Python process here
    console.log('📡 Connecting to MCP server...');
  }

  /**
   * Initialize the MCP connection
   */
  async initialize() {
    // Send initialize request
    const initRequest = {
      jsonrpc: '2.0',
      id: this.getNextRequestId(),
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {
          roots: {
            listChanged: true
          },
          sampling: {}
        },
        clientInfo: {
          name: 'hospital-frontend',
          version: '1.0.0'
        }
      }
    };

    console.log('🔄 Initializing MCP connection...');
    // For now, we'll use the HTTP bridge approach
    // but structure it like a proper MCP client
  }

  /**
   * List all available tools from the server
   */
  async listTools() {
    try {
      const response = await fetch('http://localhost:8080/tools');
      const data = await response.json();
      
      // Extract tools array from the response
      const tools = data.tools || data;
      
      if (!Array.isArray(tools)) {
        throw new Error('Tools response is not an array');
      }
      
      // Store tools in our map
      tools.forEach(tool => {
        this.tools.set(tool.name, tool);
      });
      
      console.log('🛠️ Loaded MCP tools:', Array.from(this.tools.keys()));
      return Array.from(this.tools.values());
    } catch (error) {
      console.error('❌ Failed to list tools:', error);
      throw error;
    }
  }

  /**
   * Call a tool with arguments
   */
  async callTool(toolName, args = {}) {
    if (!this.connected) {
      throw new Error('MCP client not connected');
    }

    if (!this.tools.has(toolName)) {
      throw new Error(`Tool '${toolName}' not found`);
    }

    try {
      console.log(`🔧 Calling MCP tool: ${toolName}`, args);
      
      const response = await fetch(`http://localhost:8080/tools/${toolName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(args)
      });

      if (!response.ok) {
        throw new Error(`Tool call failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log(`✅ Tool result for ${toolName}:`, result);
      
      return result;
    } catch (error) {
      console.error(`❌ Tool call failed for ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Smart query analyzer and executor
   * Analyzes user intent and calls appropriate tools
   */
  async executeQuery(userMessage) {
    console.log('🤔 Analyzing user query:', userMessage);
    console.log('🔍 Original message:', userMessage);
    
    const message = userMessage.toLowerCase();
    console.log('🔍 Lowercase message:', message);

    try {
      // Patient operations
      if (message.includes('create') && (message.includes('patient') || message.includes('full name'))) {
        const patientData = this.extractPatientData(userMessage);
        if (patientData) {
          const result = await this.callTool('create_patient', patientData);
          return {
            success: true,
            operation: 'create_patient',
            result: result.result,
            message: 'Patient created successfully'
          };
        }
      }

      // Department operations
      if (message.includes('create') && message.includes('department')) {
        const deptData = this.extractDepartmentData(userMessage);
        if (deptData) {
          const result = await this.callTool('create_department', deptData);
          return {
            success: true,
            operation: 'create_department',
            result: result.result,
            message: 'Department created successfully'
          };
        }
      }

      // Room operations
      if (message.includes('create') && message.includes('room')) {
        const roomData = await this.extractRoomData(userMessage);
        if (roomData) {
          const result = await this.callTool('create_room', roomData);
          return {
            success: true,
            operation: 'create_room',
            result: result.result,
            message: 'Room created successfully'
          };
        }
      }

      // Bed operations
      if (message.includes('create') && message.includes('bed')) {
        const bedData = await this.extractBedData(userMessage);
        if (bedData) {
          const result = await this.callTool('create_bed', bedData);
          return {
            success: true,
            operation: 'create_bed',
            result: result.result,
            message: 'Bed created successfully'
          };
        }
      }

      // List operations
      if (message.includes('list') || message.includes('show')) {
        if (message.includes('patient')) {
          const result = await this.callTool('list_patients');
          return {
            success: true,
            operation: 'list_patients',
            result: result.result,
            message: `Found ${result.result.patients?.length || 0} patients`
          };
        }
        if (message.includes('bed')) {
          const result = await this.callTool('list_beds');
          return {
            success: true,
            operation: 'list_beds', 
            result: result.result,
            message: `Found beds information`
          };
        }
        if (message.includes('department')) {
          const result = await this.callTool('list_departments');
          return {
            success: true,
            operation: 'list_departments',
            result: result.result,
            message: `Found departments information`
          };
        }
        if (message.includes('staff')) {
          const result = await this.callTool('list_staff');
          return {
            success: true,
            operation: 'list_staff',
            result: result.result,
            message: `Found staff information`
          };
        }
        if (message.includes('room')) {
          const result = await this.callTool('list_rooms');
          return {
            success: true,
            operation: 'list_rooms',
            result: result.result,
            message: `Found rooms information`
          };
        }
      }

      return {
        success: false,
        message: 'No matching hospital operation found'
      };

    } catch (error) {
      console.error('❌ Query execution failed:', error);
      return {
        success: false,
        error: error.message,
        message: 'Operation failed'
      };
    }
  }

  /**
   * Extract patient data from user message
   */
  extractPatientData(message) {
    console.log('🔍 Extracting patient data from:', message);

    const patterns = {
      fullName: /(?:full name|name):?\s*([A-Za-z\s]+)(?:\s*,|\s*date|\s*dob|$)/i,
      firstName: /(?:first name):?\s*([A-Za-z]+)/i,
      lastName: /(?:last name):?\s*([A-Za-z]+)/i,
      dob: /(?:date of birth|dob):?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})/i,
      phone: /(?:phone|phone number):?\s*([\+\d\s\-\(\)]{7,15})/i,
      email: /(?:email):?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i,
      address: /(?:address):?\s*([^,]+?)(?:\s*emergency|\s*medical|\s*insurance|$)/i,
      gender: /(?:gender):?\s*(male|female|m|f)/i,
      emergencyContactName: /(?:emergency contact|emergency contact name):?\s*([A-Za-z\s]+)(?:\s*phone|\s*,|$)/i,
      emergencyContactPhone: /(?:emergency contact phone|emergency phone|contact phone):?\s*([\+\d\s\-\(\)]{7,15})/i,
      medicalHistory: /(?:medical history|history):?\s*([^,]+?)(?:\s*insurance|$)/i
    };

    const data = {};

    // Extract full name and split it
    const fullNameMatch = message.match(patterns.fullName);
    if (fullNameMatch) {
      const nameParts = fullNameMatch[1].trim().split(/\s+/);
      data.first_name = nameParts[0];
      data.last_name = nameParts.slice(1).join(' ') || nameParts[0];
    }

    // Extract individual fields
    const dobMatch = message.match(patterns.dob);
    if (dobMatch) {
      let dob = dobMatch[1];
      // Convert to YYYY-MM-DD format if needed
      if (dob.match(/\d{1,2}[-/]\d{1,2}[-/]\d{4}/)) {
        const parts = dob.split(/[-/]/);
        dob = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      data.date_of_birth = dob;
    }

    const phoneMatch = message.match(patterns.phone);
    if (phoneMatch) {
      data.phone = phoneMatch[1].trim();
    }

    const emailMatch = message.match(patterns.email);
    if (emailMatch) {
      data.email = emailMatch[1];
    }

    const addressMatch = message.match(patterns.address);
    if (addressMatch) {
      data.address = addressMatch[1].trim();
    }

    const genderMatch = message.match(patterns.gender);
    if (genderMatch) {
      const gender = genderMatch[1].toLowerCase();
      data.gender = gender === 'm' || gender === 'male' ? 'male' : 'female';
    }

    const emergencyNameMatch = message.match(patterns.emergencyContactName);
    if (emergencyNameMatch) {
      data.emergency_contact_name = emergencyNameMatch[1].trim();
    }

    const emergencyPhoneMatch = message.match(patterns.emergencyContactPhone);
    if (emergencyPhoneMatch) {
      data.emergency_contact_phone = emergencyPhoneMatch[1].trim();
    }

    const medicalHistoryMatch = message.match(patterns.medicalHistory);
    if (medicalHistoryMatch) {
      data.medical_history = medicalHistoryMatch[1].trim();
    }

    // Generate patient number
    if (data.first_name && data.last_name && data.date_of_birth) {
      data.patient_number = `P${Date.now().toString().slice(-6)}`;
      console.log('✅ Extracted patient data:', data);
      return data;
    }

    console.log('❌ Insufficient patient data');
    return null;
  }

  /**
   * Extract department data from user message
   */
  extractDepartmentData(message) {
    const patterns = {
      name: /(?:department|create department):?\s*:?\s*([A-Za-z\s]+?)(?:\s*,|\s*description|\s*floor|$)/i,
      description: /(?:description):?\s*([^,]+?)(?:\s*floor|\s*phone|$)/i,
      floor: /(?:floor|floor number):?\s*(\d+)/i,
      phone: /(?:phone):?\s*([\d\s\-\(\)]{7,15})/i,
      email: /(?:email):?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i
    };

    const data = {};

    const nameMatch = message.match(patterns.name);
    if (nameMatch) {
      data.name = nameMatch[1].trim();
    }

    const descMatch = message.match(patterns.description);
    if (descMatch) {
      data.description = descMatch[1].trim();
    }

    const floorMatch = message.match(patterns.floor);
    if (floorMatch) {
      data.floor_number = parseInt(floorMatch[1]);
    }

    const phoneMatch = message.match(patterns.phone);
    if (phoneMatch) {
      data.phone = phoneMatch[1].trim();
    }

    const emailMatch = message.match(patterns.email);
    if (emailMatch) {
      data.email = emailMatch[1];
    }

    if (data.name) {
      console.log('✅ Extracted department data:', data);
      return data;
    }

    return null;
  }

  /**
   * Extract room data from user message
   */
  async extractRoomData(message) {
    const patterns = {
      roomNumber: /(?:room|room number):?\s*([A-Za-z0-9]+)/i,
      departmentName: /(?:department):?\s*([A-Za-z\s]+?)(?:\s*,|\s*type|\s*floor|$)/i,
      roomType: /(?:type):?\s*(emergency|icu|standard|general|private|ward)/i,
      floor: /(?:floor):?\s*(\d+)/i,
      capacity: /(?:capacity):?\s*(\d+)/i
    };

    const data = {};

    const roomMatch = message.match(patterns.roomNumber);
    if (roomMatch) {
      data.room_number = roomMatch[1];
    }

    const deptMatch = message.match(patterns.departmentName);
    if (deptMatch) {
      const deptName = deptMatch[1].trim();
      // Get department ID by name
      const departmentId = await this.getDepartmentIdByName(deptName);
      if (departmentId) {
        data.department_id = departmentId;
      }
    }

    const typeMatch = message.match(patterns.roomType);
    if (typeMatch) {
      data.room_type = typeMatch[1];
    }

    const floorMatch = message.match(patterns.floor);
    if (floorMatch) {
      data.floor_number = parseInt(floorMatch[1]);
    }

    const capacityMatch = message.match(patterns.capacity);
    if (capacityMatch) {
      data.capacity = parseInt(capacityMatch[1]);
    }

    if (data.room_number && data.department_id) {
      return data;
    }

    return null;
  }

  /**
   * Extract bed data from user message
   */
  async extractBedData(message) {
    const patterns = {
      bedNumber: /(?:bed|bed number):?\s*([A-Za-z0-9]+)/i,
      roomNumber: /(?:room|room number):?\s*([A-Za-z0-9]+)/i,
      bedType: /(?:type):?\s*(standard|icu|emergency|pediatric|psychiatric)/i
    };

    const data = {};

    const bedMatch = message.match(patterns.bedNumber);
    if (bedMatch) {
      data.bed_number = bedMatch[1];
    }

    const roomMatch = message.match(patterns.roomNumber);
    if (roomMatch) {
      const roomNumber = roomMatch[1];
      // Get room ID by number
      const roomId = await this.getRoomIdByNumber(roomNumber);
      if (roomId) {
        data.room_id = roomId;
      }
    }

    const typeMatch = message.match(patterns.bedType);
    if (typeMatch) {
      data.bed_type = typeMatch[1];
    }

    // Default status
    data.status = 'available';

    if (data.bed_number && data.room_id) {
      return data;
    }

    return null;
  }

  /**
   * Get department ID by name
   */
  async getDepartmentIdByName(name) {
    try {
      const result = await this.callTool('list_departments');
      const departments = result.result?.departments || [];
      
      const dept = departments.find(d => 
        d.name.toLowerCase().includes(name.toLowerCase()) ||
        name.toLowerCase().includes(d.name.toLowerCase())
      );
      
      return dept ? dept.id : null;
    } catch (error) {
      console.error('Error getting department ID:', error);
      return null;
    }
  }

  /**
   * Get room ID by number
   */
  async getRoomIdByNumber(number) {
    try {
      const result = await this.callTool('list_rooms');
      const rooms = result.result?.rooms || [];
      
      const room = rooms.find(r => r.room_number === number);
      return room ? room.id : null;
    } catch (error) {
      console.error('Error getting room ID:', error);
      return null;
    }
  }

  /**
   * Get next request ID
   */
  getNextRequestId() {
    return ++this.requestId;
  }

  /**
   * Disconnect from the server
   */
  async disconnect() {
    this.connected = false;
    this.tools.clear();
    console.log('🔌 MCP Client disconnected');
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.connected;
  }

  /**
   * Get available tools
   */
  getTools() {
    return Array.from(this.tools.values());
  }
}

export default MCPClient;
