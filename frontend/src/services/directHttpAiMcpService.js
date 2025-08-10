/**
 * Direct AI MCP Service - Uses HTTP transport directly to FastMCP server
 * No process manager required - communicates directly with Python backend
 */

import DirectHttpMCPClient from './directHttpMcpClient.js';

class DirectHttpAIMCPService {
  constructor() {
    this.mcpClient = new DirectHttpMCPClient();
    this.openaiApiKey = null;
    this.isInitialized = false;
  }

  /**
   * Initialize the service with OpenAI API key
   * serverConfig is optional since we connect directly to HTTP server
   */
  async initialize(openaiApiKey, serverConfig = null) {
    console.log('🚀 Initializing Direct HTTP AI-MCP Service...');
    
    if (!openaiApiKey) {
      console.error('❌ OpenAI API key is required');
      return false;
    }

    this.openaiApiKey = openaiApiKey;

    // Connect to the MCP server directly
    const connected = await this.mcpClient.connect();
    if (!connected) {
      console.error('❌ Failed to connect to MCP server');
      return false;
    }

    this.isInitialized = true;
    console.log('✅ Direct HTTP AI-MCP Service initialized successfully');
    
    return true;
  }

  /**
   * Get server information
   */
  getServerInfo() {
    return this.mcpClient.getServerInfo();
  }

  /**
   * Get available tools
   */
  getTools() {
    return this.mcpClient.getTools();
  }

  /**
   * Check if service is connected
   */
  isConnected() {
    return this.isInitialized && this.mcpClient.isConnectedToServer();
  }

  /**
   * Process user message using OpenAI and MCP tools (renamed from processMessage)
   */
  async processRequest(userMessage, onProgress = null) {
    return this.processMessage(userMessage, onProgress);
  }

  /**
   * Process user message using OpenAI and MCP tools
   */
  async processMessage(userMessage, onProgress = null) {
    if (!this.isInitialized) {
      throw new Error('Service not initialized');
    }

    console.log('💬 Processing message:', userMessage);

    try {
      // Step 1: Analyze the user's request
      if (onProgress) {
        onProgress({
          type: 'thinking',
          stage: 'analyzing',
          message: 'Analyzing your request...'
        });
      }

      // Get available tools for context
      const tools = this.mcpClient.getTools();
      
      // Step 2: Determine which tools to use
      const toolsNeeded = await this.determineRequiredTools(userMessage, tools);
      
      // Handle special cases where we need more information
      if (toolsNeeded.length > 0 && toolsNeeded[0].needsInput) {
        const requestType = toolsNeeded[0].name;
        let response = "";
        
        switch (requestType) {
          case '_ask_for_patient_details':
            response = "To create a new patient, I need:\n\n" +
                      "📝 **Required:** First Name, Last Name, Date of Birth (YYYY-MM-DD)\n" +
                      "📋 **Optional:** Gender, Phone, Email, Address\n\n" +
                      "**Example:** *Create patient John Doe born 1985-05-15*";
            break;
            
          case '_ask_for_staff_details':
            response = "To create a new staff member, I need:\n\n" +
                      "📝 **Required:** Employee ID, Department ID, Position\n" +
                      "📋 **Optional:** Specialization, Salary, Shift Pattern\n\n" +
                      "**Example:** *Create staff EMP001 in cardiology as doctor*";
            break;
            
          case '_ask_for_department_details':
            response = "To create a new department, I need:\n\n" +
                      "📝 **Required:** Department Name\n" +
                      "📋 **Optional:** Description, Floor Number, Head Doctor ID\n\n" +
                      "**Example:** *Create department Cardiology on floor 3*";
            break;
            
          case '_ask_for_appointment_details':
            response = "To create a new appointment, I need:\n\n" +
                      "📝 **Required:** Patient ID, Doctor ID, Department ID, Date (YYYY-MM-DD HH:MM)\n" +
                      "📋 **Optional:** Duration, Reason, Notes\n\n" +
                      "**Example:** *Create appointment for P001 with D001 in cardiology on 2025-08-10 10:00*";
            break;
            
          case '_ask_for_bed_details':
            response = "To create a new bed, I need:\n\n" +
                      "📝 **Required:** Bed Number, Room ID\n" +
                      "📋 **Optional:** Bed Type, Status\n\n" +
                      "**Example:** *Create bed B001 in room R001*";
            break;
            
          case '_ask_for_equipment_details':
            response = "To create new equipment, I need:\n\n" +
                      "📝 **Required:** Equipment ID, Name, Category ID\n" +
                      "📋 **Optional:** Model, Manufacturer, Department, Cost\n\n" +
                      "**Example:** *Create equipment EQ001 MRI Scanner in radiology*";
            break;
            
          case '_ask_for_supply_details':
            response = "To create a new supply item, I need:\n\n" +
                      "📝 **Required:** Item Code, Name, Category ID, Unit of Measure\n" +
                      "📋 **Optional:** Current Stock, Supplier, Cost\n\n" +
                      "**Example:** *Create supply SUP001 Bandages in medical supplies per piece*";
            break;
            
          case '_ask_for_room_details':
            response = "To create a new room, I need:\n\n" +
                      "📝 **Required:** Room Number, Department ID\n" +
                      "📋 **Optional:** Room Type, Capacity, Floor Number\n\n" +
                      "**Example:** *Create room R001 in cardiology department*";
            break;
            
          case '_ask_for_user_details':
            response = "To create a new user, I need:\n\n" +
                      "📝 **Required:** Username, Email, Role, First Name, Last Name\n" +
                      "📋 **Optional:** Phone\n\n" +
                      "**Example:** *Create user johndoe john.doe@hospital.com doctor John Doe*";
            break;
            
          default:
            response = "Please provide the required information for this operation.";
        }
        
        return {
          success: true,
          response: response,
          toolsUsed: [],
          toolResults: []
        };
      }
      
      if (onProgress) {
        onProgress({
          type: 'thinking',
          stage: 'planning',
          message: `Planning to use ${toolsNeeded.length} tool(s)...`
        });
      }

      // Step 3: Execute tools if needed
      let toolResults = [];
      if (toolsNeeded.length > 0) {
        if (onProgress) {
          onProgress({
            type: 'thinking',
            stage: 'executing',
            message: 'Executing hospital management operations...'
          });
        }

        for (const tool of toolsNeeded) {
          try {
            const result = await this.mcpClient.callTool(tool.name, tool.arguments);
            toolResults.push({
              tool: tool.name,
              result: result
            });
          } catch (error) {
            console.error(`❌ Tool ${tool.name} failed:`, error);
            toolResults.push({
              tool: tool.name,
              error: error.message
            });
          }
        }
      }

      // Step 4: Generate response using OpenAI
      if (onProgress) {
        onProgress({
          type: 'thinking',
          stage: 'generating',
          message: 'Generating response...'
        });
      }

      const response = await this.generateResponse(userMessage, toolResults, tools);
      
      console.log('🎯 Final AI response:', response);
      
      return {
        success: true,
        response: response,
        toolsUsed: toolsNeeded.map(t => t.name),
        toolResults: toolResults
      };

    } catch (error) {
      console.error('❌ Failed to process message:', error);
      return {
        success: false,
        error: error.message,
        response: 'Sorry, I encountered an error processing your request. Please try again.'
      };
    }
  }

  /**
   * Determine which tools are needed based on user input
   */
  async determineRequiredTools(userMessage, availableTools) {
    // Simple keyword-based tool mapping for better reliability
    const message = userMessage.toLowerCase();
    const toolsNeeded = [];
    
    console.log('🔍 Analyzing message:', message);
    
    // Check for structured data input (when user provides details directly)
    if (this.containsStructuredData(userMessage)) {
      const structuredTool = this.parseStructuredInput(userMessage);
      if (structuredTool) {
        return [structuredTool];
      }
    }
    
    // Patient operations
    if (message.includes('list patients') || message.includes('show patients') || message.includes('all patients') || message.includes('patients')) {
      toolsNeeded.push({ name: 'list_patients', arguments: {} });
    }
    
    // Enhanced patient creation with parameter extraction
    if (message.includes('create patient') || message.includes('add patient') || message.includes('new patient')) {
      const patientParams = this.extractPatientParameters(userMessage);
      if (patientParams.first_name && patientParams.last_name && patientParams.date_of_birth) {
        // Generate patient number if not provided
        if (!patientParams.patient_number) {
          patientParams.patient_number = `PAT${String(Math.floor(Math.random() * 9000) + 1000)}`;
        }
        toolsNeeded.push({ name: 'create_patient', arguments: patientParams });
      } else {
        return [{ name: '_ask_for_patient_details', needsInput: true }];
      }
    }
    
    if (message.includes('search patient') || message.includes('find patient')) {
      const searchParams = this.extractPatientSearchParameters(userMessage);
      toolsNeeded.push({ name: 'search_patients', arguments: searchParams });
    }
    
    // Staff operations
    if (message.includes('list staff') || message.includes('show staff') || message.includes('all staff') || message.includes('staff')) {
      toolsNeeded.push({ name: 'list_staff', arguments: {} });
    }
    
    // Enhanced staff creation with parameter extraction
    if (message.includes('create staff') || message.includes('add staff') || message.includes('new staff')) {
      const staffParams = this.extractStaffParameters(userMessage);
      if (staffParams.employee_id && staffParams.department_id && staffParams.position) {
        toolsNeeded.push({ name: 'create_staff', arguments: staffParams });
      } else {
        return [{ name: '_ask_for_staff_details', needsInput: true }];
      }
    }
    
    // Department operations
    if (message.includes('list departments') || message.includes('show departments') || message.includes('all departments') || message.includes('departments')) {
      toolsNeeded.push({ name: 'list_departments', arguments: {} });
    }
    
    // Enhanced department creation
    if (message.includes('create department') || message.includes('add department') || message.includes('new department')) {
      const deptParams = this.extractDepartmentParameters(userMessage);
      if (deptParams.name) {
        toolsNeeded.push({ name: 'create_department', arguments: deptParams });
      } else {
        return [{ name: '_ask_for_department_details', needsInput: true }];
      }
    }
    
    // Appointment operations
    if (message.includes('list appointments') || message.includes('show appointments') || message.includes('all appointments') || message.includes('appointments')) {
      toolsNeeded.push({ name: 'list_appointments', arguments: {} });
    }
    
    // Enhanced appointment creation
    if (message.includes('create appointment') || message.includes('book appointment') || message.includes('schedule appointment')) {
      const appointmentParams = this.extractAppointmentParameters(userMessage);
      if (appointmentParams.patient_id && appointmentParams.doctor_id && appointmentParams.appointment_date) {
        toolsNeeded.push({ name: 'create_appointment', arguments: appointmentParams });
      } else {
        return [{ name: '_ask_for_appointment_details', needsInput: true }];
      }
    }
    
    // Bed operations
    if (message.includes('list beds') || message.includes('show beds') || message.includes('all beds') || message.includes('beds')) {
      toolsNeeded.push({ name: 'list_beds', arguments: {} });
    }
    
    // Enhanced bed creation
    if (message.includes('create bed') || message.includes('add bed') || message.includes('new bed')) {
      const bedParams = this.extractBedParameters(userMessage);
      if (bedParams.bed_number && bedParams.room_id) {
        toolsNeeded.push({ name: 'create_bed', arguments: bedParams });
      } else {
        return [{ name: '_ask_for_bed_details', needsInput: true }];
      }
    }
    
    // Equipment operations
    if (message.includes('list equipment') || message.includes('show equipment') || message.includes('all equipment') || message.includes('equipment')) {
      toolsNeeded.push({ name: 'list_equipment', arguments: {} });
    }
    
    // Enhanced equipment creation
    if (message.includes('create equipment') || message.includes('add equipment') || message.includes('new equipment')) {
      const equipmentParams = this.extractEquipmentParameters(userMessage);
      if (equipmentParams.equipment_id && equipmentParams.name && equipmentParams.category_id) {
        toolsNeeded.push({ name: 'create_equipment', arguments: equipmentParams });
      } else {
        return [{ name: '_ask_for_equipment_details', needsInput: true }];
      }
    }
    
    // Supply operations
    if (message.includes('list supplies') || message.includes('show supplies') || message.includes('all supplies') || message.includes('supplies')) {
      toolsNeeded.push({ name: 'list_supplies', arguments: {} });
    }
    
    // Enhanced supply creation
    if (message.includes('create supply') || message.includes('add supply') || message.includes('new supply')) {
      const supplyParams = this.extractSupplyParameters(userMessage);
      if (supplyParams.item_code && supplyParams.name && supplyParams.category_id && supplyParams.unit_of_measure) {
        toolsNeeded.push({ name: 'create_supply', arguments: supplyParams });
      } else {
        return [{ name: '_ask_for_supply_details', needsInput: true }];
      }
    }
    
    // Room operations
    if (message.includes('list rooms') || message.includes('show rooms') || message.includes('all rooms') || message.includes('rooms')) {
      toolsNeeded.push({ name: 'list_rooms', arguments: {} });
    }
    
    // Enhanced room creation
    if (message.includes('create room') || message.includes('add room') || message.includes('new room')) {
      const roomParams = this.extractRoomParameters(userMessage);
      if (roomParams.room_number && roomParams.department_id) {
        toolsNeeded.push({ name: 'create_room', arguments: roomParams });
      } else {
        return [{ name: '_ask_for_room_details', needsInput: true }];
      }
    }
    
    // User operations
    if (message.includes('list users') || message.includes('show users') || message.includes('all users') || message.includes('users')) {
      toolsNeeded.push({ name: 'list_users', arguments: {} });
    }
    
    // Enhanced user creation
    if (message.includes('create user') || message.includes('add user') || message.includes('new user')) {
      const userParams = this.extractUserParameters(userMessage);
      if (userParams.username && userParams.email && userParams.role && userParams.first_name && userParams.last_name) {
        toolsNeeded.push({ name: 'create_user', arguments: userParams });
      } else {
        return [{ name: '_ask_for_user_details', needsInput: true }];
      }
    }
    
    console.log('🔧 Tools needed:', toolsNeeded);
    return toolsNeeded;
  }

  /**
   * Generate response using OpenAI
   */
  async generateResponse(userMessage, toolResults, availableTools) {
    // If no OpenAI API key, provide simple formatted response
    if (!this.openaiApiKey) {
      return this.formatToolResults(userMessage, toolResults);
    }

    const systemPrompt = `You are a helpful hospital management assistant. You have access to hospital management tools and have executed some operations.

Available tools:
${availableTools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n')}

Tool execution results:
${toolResults.map(result => {
  if (result.error) {
    return `❌ ${result.tool}: Error - ${result.error}`;
  } else {
    return `✅ ${result.tool}: ${JSON.stringify(result.result, null, 2)}`;
  }
}).join('\n\n')}

Please provide a helpful, friendly response based on the tool results. Format the data nicely for the user. Use emojis where appropriate.`;

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userMessage }
          ],
          temperature: 0.7,
          max_tokens: 2000
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;

    } catch (error) {
      console.error('❌ Failed to generate response:', error);
      return this.formatToolResults(userMessage, toolResults);
    }
  }

  /**
   * Format tool results without OpenAI
   */
  formatToolResults(userMessage, toolResults) {
    if (toolResults.length === 0) {
      return "I understand your request, but I couldn't find any specific operations to perform. Please try being more specific about what you'd like to do (e.g., 'list patients', 'show departments', etc.).";
    }

    let response = "";
    
    toolResults.forEach(result => {
      if (result.error) {
        response += `❌ **Error with ${result.tool}**: ${result.error}\n\n`;
      } else {
        // Handle both old format (result.result.content[0].text) and new direct format
        let data;
        if (result.result?.content?.[0]?.text) {
          // Old format - parse JSON from text
          try {
            data = JSON.parse(result.result.content[0].text);
          } catch (e) {
            data = result.result.content[0].text;
          }
        } else if (result.result) {
          // New format - data is already parsed
          data = result.result;
        }
        
        if (data) {
          try {
            if (Array.isArray(data) && data.length > 0) {
              response += `✅ **${result.tool.replace('_', ' ').toUpperCase()}**\n\n`;
              response += `Found ${data.length} record(s):\n\n`;
              data.forEach((item, index) => {
                response += `**${index + 1}.** `;
                if (item.first_name && item.last_name) {
                  response += `${item.first_name} ${item.last_name}`;
                  if (item.patient_number) response += ` (${item.patient_number})`;
                  if (item.email) response += ` - ${item.email}`;
                  if (item.phone) response += ` - ${item.phone}`;
                } else if (item.name) {
                  response += `${item.name}`;
                  if (item.description) response += ` - ${item.description}`;
                } else {
                  response += JSON.stringify(item, null, 2);
                }
                response += "\n";
              });
              response += "\n";
            } else if (Array.isArray(data) && data.length === 0) {
              response += `✅ **${result.tool.replace('_', ' ').toUpperCase()}**: No records found\n\n`;
            } else {
              response += `✅ **${result.tool.replace('_', ' ').toUpperCase()}**: ${JSON.stringify(data, null, 2)}\n\n`;
            }
          } catch {
            response += `✅ **${result.tool.replace('_', ' ').toUpperCase()}**: ${typeof data === 'string' ? data : JSON.stringify(data)}\n\n`;
          }
        } else {
          response += `✅ **${result.tool.replace('_', ' ').toUpperCase()}**: Operation completed successfully\n\n`;
        }
      }
    });

    return response.trim();
  }

  /**
   * Check if the message contains structured data (field: value format)
   */
  containsStructuredData(message) {
    // Look for patterns like "Field Name: Value" or "Required" or "Optional" sections
    const structuredPatterns = [
      /required/i,
      /optional/i,
      /\w+\s*:\s*\w+/,
      /bed\s+number\s*:/i,
      /room\s+id\s*:/i,
      /patient\s+number\s*:/i,
      /first\s+name\s*:/i,
      /last\s+name\s*:/i,
      /date\s+of\s+birth\s*:/i,
      /employee\s+id\s*:/i,
      /department\s*:/i
    ];
    
    return structuredPatterns.some(pattern => pattern.test(message));
  }

  /**
   * Parse structured input to determine the appropriate tool and parameters
   */
  parseStructuredInput(message) {
    const lines = message.split('\n').map(line => line.trim()).filter(line => line);
    const params = {};
    let operationType = null;
    
    // Extract field-value pairs
    for (const line of lines) {
      const colonMatch = line.match(/^([^:]+):\s*(.+)$/);
      if (colonMatch) {
        const field = colonMatch[1].trim().toLowerCase().replace(/\s+/g, '_');
        const value = colonMatch[2].trim();
        
        // Map common field names to parameter names
        const fieldMappings = {
          'bed_number': 'bed_number',
          'room_id': 'room_id',
          'bed_type': 'bed_type',
          'status': 'status',
          'first_name': 'first_name',
          'last_name': 'last_name',
          'date_of_birth': 'date_of_birth',
          'gender': 'gender',
          'phone': 'phone',
          'email': 'email',
          'address': 'address',
          'patient_number': 'patient_number',
          'employee_id': 'employee_id',
          'department_id': 'department_id',
          'department': 'department_id',
          'position': 'position',
          'name': 'name',
          'room_number': 'room_number',
          'appointment_date': 'appointment_date',
          'doctor_id': 'doctor_id',
          'patient_id': 'patient_id'
        };
        
        const mappedField = fieldMappings[field] || field;
        params[mappedField] = value;
      }
    }
    
    // Determine operation type based on provided fields
    if (params.bed_number && params.room_id) {
      operationType = 'create_bed';
    } else if (params.first_name && params.last_name && params.date_of_birth) {
      operationType = 'create_patient';
      // Generate patient number if not provided
      if (!params.patient_number) {
        params.patient_number = `PAT${String(Math.floor(Math.random() * 9000) + 1000)}`;
      }
    } else if (params.employee_id && params.department_id && params.position) {
      operationType = 'create_staff';
    } else if (params.name && !params.bed_number && !params.first_name) {
      operationType = 'create_department';
    } else if (params.room_number && params.department_id) {
      operationType = 'create_room';
    } else if (params.patient_id && params.doctor_id && params.appointment_date) {
      operationType = 'create_appointment';
    }
    
    if (operationType && Object.keys(params).length > 0) {
      console.log(`🎯 Detected structured input for: ${operationType}`, params);
      return { name: operationType, arguments: params };
    }
    
    return null;
  }

  /**
   * Extract patient parameters from natural language input
   */
  extractPatientParameters(message) {
    const params = {};
    const text = message.toLowerCase();
    
    // Extract names (look for "patient [first] [last]" or "[first] [last]")
    const namePatterns = [
      /patient\s+([a-zA-Z]+)\s+([a-zA-Z]+)/,
      /create\s+patient\s+([a-zA-Z]+)\s+([a-zA-Z]+)/,
      /add\s+patient\s+([a-zA-Z]+)\s+([a-zA-Z]+)/,
      /([a-zA-Z]+)\s+([a-zA-Z]+)/
    ];
    
    for (const pattern of namePatterns) {
      const match = message.match(pattern);
      if (match) {
        params.first_name = match[1];
        params.last_name = match[2];
        break;
      }
    }
    
    // Extract date of birth (YYYY-MM-DD format)
    const dobMatch = message.match(/(\d{4}-\d{2}-\d{2})/);
    if (dobMatch) {
      params.date_of_birth = dobMatch[1];
    } else {
      // Try alternative date formats
      const dobMatch2 = message.match(/born\s+(\d{4}-\d{2}-\d{2})/);
      if (dobMatch2) {
        params.date_of_birth = dobMatch2[1];
      }
    }
    
    // Extract gender
    if (text.includes('male') && !text.includes('female')) {
      params.gender = 'Male';
    } else if (text.includes('female')) {
      params.gender = 'Female';
    }
    
    // Extract phone (various formats)
    const phoneMatch = message.match(/(\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\+?\d{10,})/);
    if (phoneMatch) {
      params.phone = phoneMatch[1];
    }
    
    // Extract email
    const emailMatch = message.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    if (emailMatch) {
      params.email = emailMatch[1];
    }
    
    // Extract address (look for "address" keyword followed by text)
    const addressMatch = message.match(/address[:\s]+([^,]+(?:,\s*[^,]+)*)/i);
    if (addressMatch) {
      params.address = addressMatch[1].trim();
    }
    
    return params;
  }

  /**
   * Extract staff parameters from natural language input
   */
  extractStaffParameters(message) {
    const params = {};
    
    // Extract employee ID
    const empIdMatch = message.match(/emp(\d+)|employee\s+(\w+)|id\s+(\w+)/i);
    if (empIdMatch) {
      params.employee_id = empIdMatch[1] || empIdMatch[2] || empIdMatch[3];
    }
    
    // Extract department
    const deptMatch = message.match(/in\s+(\w+)|department\s+(\w+)/i);
    if (deptMatch) {
      params.department_id = deptMatch[1] || deptMatch[2];
    }
    
    // Extract position
    const positionMatch = message.match(/as\s+(\w+)|position\s+(\w+)/i);
    if (positionMatch) {
      params.position = positionMatch[1] || positionMatch[2];
    }
    
    return params;
  }

  /**
   * Extract department parameters from natural language input
   */
  extractDepartmentParameters(message) {
    const params = {};
    
    // Extract department name
    const nameMatch = message.match(/department\s+([a-zA-Z\s]+)/i);
    if (nameMatch) {
      params.name = nameMatch[1].trim();
    } else {
      const createMatch = message.match(/create\s+([a-zA-Z\s]+)\s+department/i);
      if (createMatch) {
        params.name = createMatch[1].trim();
      }
    }
    
    // Extract floor number
    const floorMatch = message.match(/floor\s+(\d+)/i);
    if (floorMatch) {
      params.floor_number = parseInt(floorMatch[1]);
    }
    
    return params;
  }

  /**
   * Extract appointment parameters from natural language input
   */
  extractAppointmentParameters(message) {
    const params = {};
    
    // Extract patient ID
    const patientMatch = message.match(/patient\s+(\w+)|for\s+(\w+)/i);
    if (patientMatch) {
      params.patient_id = patientMatch[1] || patientMatch[2];
    }
    
    // Extract doctor ID
    const doctorMatch = message.match(/doctor\s+(\w+)|with\s+(\w+)/i);
    if (doctorMatch) {
      params.doctor_id = doctorMatch[1] || doctorMatch[2];
    }
    
    // Extract department
    const deptMatch = message.match(/in\s+(\w+)|department\s+(\w+)/i);
    if (deptMatch) {
      params.department_id = deptMatch[1] || deptMatch[2];
    }
    
    // Extract date and time
    const dateMatch = message.match(/(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
      const timeMatch = message.match(/(\d{2}:\d{2})/);
      if (timeMatch) {
        params.appointment_date = `${dateMatch[1]} ${timeMatch[1]}`;
      } else {
        params.appointment_date = dateMatch[1];
      }
    }
    
    return params;
  }

  /**
   * Extract bed parameters from natural language input
   */
  extractBedParameters(message) {
    const params = {};
    
    // Extract bed number
    const bedMatch = message.match(/bed\s+(\w+)/i);
    if (bedMatch) {
      params.bed_number = bedMatch[1];
    }
    
    // Extract room ID
    const roomMatch = message.match(/room\s+(\w+)|in\s+(\w+)/i);
    if (roomMatch) {
      params.room_id = roomMatch[1] || roomMatch[2];
    }
    
    return params;
  }

  /**
   * Extract patient search parameters from natural language input
   */
  extractPatientSearchParameters(message) {
    const params = {};
    
    // Extract name for search
    const nameMatch = message.match(/find\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (nameMatch) {
      params.first_name = nameMatch[1];
      if (nameMatch[2]) {
        params.last_name = nameMatch[2];
      }
    }
    
    // Extract patient number
    const patientNumMatch = message.match(/patient\s+(\w+)/i);
    if (patientNumMatch) {
      params.patient_number = patientNumMatch[1];
    }
    
    return params;
  }

  /**
   * Extract equipment parameters from natural language input
   */
  extractEquipmentParameters(message) {
    const params = {};
    
    // Extract equipment ID
    const equipIdMatch = message.match(/equipment\s+(\w+)|eq(\d+)/i);
    if (equipIdMatch) {
      params.equipment_id = equipIdMatch[1] || `EQ${equipIdMatch[2]}`;
    }
    
    // Extract equipment name
    const nameMatch = message.match(/equipment\s+\w+\s+([a-zA-Z\s]+)/i);
    if (nameMatch) {
      params.name = nameMatch[1].trim();
    }
    
    // Extract category (basic mapping)
    if (message.toLowerCase().includes('mri') || message.toLowerCase().includes('scanner')) {
      params.category_id = 'radiology';
    } else if (message.toLowerCase().includes('monitor') || message.toLowerCase().includes('ventilator')) {
      params.category_id = 'medical';
    }
    
    return params;
  }

  /**
   * Extract supply parameters from natural language input
   */
  extractSupplyParameters(message) {
    const params = {};
    
    // Extract item code
    const itemMatch = message.match(/supply\s+(\w+)|sup(\d+)/i);
    if (itemMatch) {
      params.item_code = itemMatch[1] || `SUP${itemMatch[2]}`;
    }
    
    // Extract supply name
    const nameMatch = message.match(/supply\s+\w+\s+([a-zA-Z\s]+)/i);
    if (nameMatch) {
      params.name = nameMatch[1].trim();
    }
    
    // Basic unit mapping
    if (message.toLowerCase().includes('bandage') || message.toLowerCase().includes('syringe')) {
      params.unit_of_measure = 'piece';
      params.category_id = 'medical';
    }
    
    return params;
  }

  /**
   * Extract room parameters from natural language input
   */
  extractRoomParameters(message) {
    const params = {};
    
    // Extract room number
    const roomMatch = message.match(/room\s+(\w+)/i);
    if (roomMatch) {
      params.room_number = roomMatch[1];
    }
    
    // Extract department
    const deptMatch = message.match(/in\s+(\w+)|department\s+(\w+)/i);
    if (deptMatch) {
      params.department_id = deptMatch[1] || deptMatch[2];
    }
    
    return params;
  }

  /**
   * Extract user parameters from natural language input
   */
  extractUserParameters(message) {
    const params = {};
    
    // Extract username
    const userMatch = message.match(/user\s+(\w+)/i);
    if (userMatch) {
      params.username = userMatch[1];
    }
    
    // Extract email
    const emailMatch = message.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    if (emailMatch) {
      params.email = emailMatch[1];
    }
    
    // Extract role
    const roleMatch = message.match(/role\s+(\w+)|as\s+(\w+)/i);
    if (roleMatch) {
      params.role = roleMatch[1] || roleMatch[2];
    }
    
    // Extract names
    const nameMatch = message.match(/(\w+)\s+(\w+)(?:\s|$)/);
    if (nameMatch) {
      params.first_name = nameMatch[1];
      params.last_name = nameMatch[2];
    }
    
    return params;
  }

  /**
   * Disconnect from services
   */
  disconnect() {
    this.mcpClient.disconnect();
    this.isInitialized = false;
  }
}

export default DirectHttpAIMCPService;
