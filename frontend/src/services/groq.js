import HospitalToolsService from './hospitalTools.js';

class GroqService {
  constructor() {
    // Try to load API key from environment first, then fallback to manual setting
    this.apiKey = import.meta.env.VITE_GROQ_API_KEY || localStorage.getItem('groqApiKey') || '';
    this.baseUrl = 'https://api.groq.com/openai/v1/chat/completions';
    this.model = 'llama3-8b-8192'; // Updated to current Groq model
    this.maxTokens = 4096;
    
    console.log('🔑 Groq Service Debug:', {
      envApiKey: import.meta.env.VITE_GROQ_API_KEY ? 'Present (env)' : 'Missing (env)',
      localStorageKey: localStorage.getItem('groqApiKey') ? 'Present (localStorage)' : 'Missing (localStorage)',
      finalApiKey: this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing'
    });
    
    if (!this.apiKey) {
      console.warn('Groq API key not found. Please set VITE_GROQ_API_KEY in your .env file or configure it in the UI settings');
    }
  }

  // Method to update API key dynamically
  updateApiKey(newApiKey) {
    this.apiKey = newApiKey;
    console.log('🔄 Groq API key updated:', this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing');
  }

  get systemPrompt() {
    return `You are an intelligent AI assistant for a Hospital Management System with access to REAL hospital data through integrated MCP tools. You can help with:

🏥 **Core Capabilities:**
- **Patient Management**: View patient records, search by name (like "Arivu"), create new patients
- **Bed Management**: Check bed availability, assign/discharge patients, view bed status
- **Staff Management**: View doctors, nurses, and staff information by department
- **Equipment Tracking**: Monitor medical equipment status and maintenance
- **Supply Management**: Track inventory, identify low stock items, manage supplies
- **Appointment System**: Schedule and view appointments by doctor, patient, or date
- **Department Operations**: Manage hospital departments and room assignments

📊 **Available Hospital Tools (32 total):**
**Patient Tools**: list_patients, get_patient_by_id, create_patient
**Bed Tools**: list_beds, assign_bed_to_patient, discharge_bed, create_bed
**Staff Tools**: list_staff, create_staff
**Appointment Tools**: list_appointments, create_appointment
**Equipment Tools**: list_equipment, create_equipment, update_equipment_status, create_equipment_category
**Supply Tools**: list_supplies, create_supply, update_supply_stock, create_supply_category
**Department Tools**: list_departments, create_department, get_department_by_id
**Room Tools**: list_rooms, create_room
**User Tools**: list_users, create_user, get_user_by_id, update_user, delete_user
**Legacy Tools**: list_legacy_users, create_legacy_user
**Analytics**: log_agent_interaction for tracking usage

🔧 **How I Work:**
1. **Query Analysis**: I analyze your request to determine what hospital data you need
2. **Data Fetching**: I automatically call the appropriate MCP tools to get current data
3. **Smart Responses**: I provide accurate information using REAL hospital data, not generic responses
4. **Formatted Output**: I present data in tables, lists, and highlighted sections for clarity

🩺 **Medical Context:**
- All responses use actual hospital system data
- Patient confidentiality maintained in presentations
- Provide actionable insights for hospital operations
- Suggest best practices based on current hospital status

**Example Interactions:**
- "Show me patient Arivu" → Calls list_patients, finds Arivu's record
- "Available beds?" → Calls list_beds with status='available'
- "Today's appointments" → Calls list_appointments with today's date
- "Low stock supplies" → Calls list_supplies with low_stock_only=true
- "Staff in cardiology" → Calls list_staff filtered by department

I ALWAYS provide real data from your hospital system, never generic responses!`;
  }

  async generateResponse(userMessage, mcpData = null, conversationHistory = [], availableTools = []) {
    try {
      console.log('🤖 Groq Service Debug:', {
        apiKey: this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing',
        userMessage: userMessage.substring(0, 50) + '...',
        hasMcpData: !!mcpData,
        toolCount: availableTools.length
      });

      if (!this.apiKey) {
        throw new Error('Groq API key not configured');
      }

      // Step 1: Analyze if this is a CREATE/UPDATE operation
      const isWriteOperation = this.isWriteOperation(userMessage);
      let operationResult = null;
      
      if (isWriteOperation) {
        console.log('🔧 Detected write operation, attempting to execute...');
        operationResult = await this.executeWriteOperation(userMessage);
      }

      // Step 2: If no MCP data provided, try to fetch relevant data based on query
      if (!mcpData && !isWriteOperation) {
        console.log('📊 Fetching relevant data for query...');
        const toolResults = await HospitalToolsService.analyzeAndExecuteQuery(userMessage);
        if (toolResults.success) {
          mcpData = {
            type: 'hospital_data',
            description: `Hospital data from tools: ${toolResults.toolsCalled.join(', ')}`,
            data: toolResults.data,
            toolsCalled: toolResults.toolsCalled,
            errors: toolResults.errors
          };
        }
      }

      // Build messages for Groq's format (OpenAI compatible)
      const messages = [];
      
      // Add system message
      messages.push({
        role: 'system',
        content: this.systemPrompt
      });
      
      // Add conversation history
      if (conversationHistory.length > 0) {
        conversationHistory.slice(-10).forEach(msg => {
          messages.push({
            role: msg.role === 'ai_response' ? 'assistant' : msg.role,
            content: msg.content
          });
        });
      }

      // Build current message with context
      let currentContent = userMessage;
      
      // Add operation result if any
      if (operationResult) {
        currentContent += `\n\n**OPERATION EXECUTED:**\n`;
        currentContent += `Status: ${operationResult.success ? 'SUCCESS' : 'FAILED'}\n`;
        currentContent += `Details: ${JSON.stringify(operationResult, null, 2)}\n`;
      }
      
      if (mcpData) {
        if (mcpData.toolsCalled && mcpData.data) {
          // Use the formatted data from HospitalToolsService
          currentContent += `\n\n${HospitalToolsService.formatResultsForAI(mcpData)}`;
        } else {
          // Fallback to basic formatting for other data sources
          currentContent += `\n\n**Hospital System Data:**\n`;
          currentContent += `Type: ${mcpData.type || 'Unknown'}\n`;
          currentContent += `Description: ${mcpData.description || 'Hospital data'}\n`;
          
          if (mcpData.data) {
            if (Array.isArray(mcpData.data)) {
              currentContent += `\nData (${mcpData.data.length} records):\n`;
              currentContent += JSON.stringify(mcpData.data, null, 2);
            } else {
              currentContent += `\nData:\n`;
              currentContent += JSON.stringify(mcpData.data, null, 2);
            }
          }
        }
      }

      // Add available tools information
      if (availableTools.length > 0) {
        currentContent += `\n\n**Available Hospital Tools:** ${availableTools.length} tools available including patient management, bed allocation, staff scheduling, equipment tracking, and more.`;
      }

      messages.push({
        role: 'user',
        content: currentContent
      });

      // Instead of calling Groq API directly, route through MCP bridge
      const mcpBridgeUrl = import.meta.env.VITE_MCP_BRIDGE_URL || 'http://localhost:8080';
      
      const requestBody = {
        model: this.model,
        max_tokens: this.maxTokens,
        messages: messages,
        api_key: this.apiKey  // Pass API key to bridge
      };

      console.log('🔄 Calling Groq via MCP Bridge:', {
        url: `${mcpBridgeUrl}/groq`,
        messageCount: messages.length,
        hasMcpData: !!mcpData,
        hadOperation: !!operationResult,
        toolCount: availableTools.length
      });

      const response = await fetch(`${mcpBridgeUrl}/groq`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`MCP Bridge Groq API error: ${response.status} ${response.statusText} - ${errorData.error || 'Unknown error'}`);
      }

      const data = await response.json();
      
      if (!data.choices || !data.choices[0] || !data.choices[0].message) {
        throw new Error('Invalid response format from Groq API via MCP Bridge');
      }

      return {
        success: true,
        message: data.choices[0].message.content,
        usage: {
          inputTokens: data.usage?.prompt_tokens || 0,
          outputTokens: data.usage?.completion_tokens || 0
        },
        model: data.model,
        operationExecuted: !!operationResult,
        operationResult: operationResult
      };

    } catch (error) {
      console.error('❌ Groq API error:', error);
      return {
        success: false,
        error: error.message,
        message: `I apologize, but I encountered an error while processing your request: ${error.message}`
      };
    }
  }

  // Method to detect if user message is requesting a write operation
  isWriteOperation(userMessage) {
    const message = userMessage.toLowerCase();
    
    // Look for explicit create/write commands
    const writeKeywords = [
      'create', 'add', 'new', 'insert', 'register',
      'update', 'modify', 'change', 'edit',
      'assign', 'allocate', 'discharge',
      'delete', 'remove', 'cancel'
    ];
    
    // Look for structured data patterns that suggest creation
    const hasStructuredData = message.includes('bed number:') || 
                             message.includes('patient number:') ||
                             message.includes('room id:') ||
                             message.includes('bed type:') ||
                             /\w+\s*:\s*\w+/.test(message); // Any key:value pattern
    
    const hasWriteKeyword = writeKeywords.some(keyword => message.includes(keyword));
    
    console.log('🔍 Write operation detection:', {
      message: message.substring(0, 100) + '...',
      hasWriteKeyword,
      hasStructuredData,
      isWriteOperation: hasWriteKeyword || hasStructuredData
    });
    
    return hasWriteKeyword || hasStructuredData;
  }

  // Method to execute write operations based on user message
  async executeWriteOperation(userMessage) {
    try {
      const message = userMessage.toLowerCase();
      
      // Parse bed creation requests
      if (message.includes('create') && message.includes('bed')) {
        return await this.createBedFromMessage(userMessage);
      }
      
      // Parse patient creation requests
      if (message.includes('create') && message.includes('patient')) {
        return await this.createPatientFromMessage(userMessage);
      }
      
      // Parse bed assignment requests
      if (message.includes('assign') && message.includes('bed')) {
        return await this.assignBedFromMessage(userMessage);
      }
      
      // Parse appointment creation requests
      if (message.includes('create') && message.includes('appointment')) {
        return await this.createAppointmentFromMessage(userMessage);
      }
      
      console.log('⚠️ Write operation detected but not implemented for this type:', message);
      return null;
      
    } catch (error) {
      console.error('❌ Error executing write operation:', error);
      return {
        success: false,
        error: error.message,
        operation: 'write_operation'
      };
    }
  }

  // Parse and create bed from user message
  async createBedFromMessage(userMessage) {
    try {
      // Extract bed details from message with improved regex patterns
      const bedNumberMatch = userMessage.match(/bed number[:\s]*(\w+)/i) || 
                           userMessage.match(/bed number[:\s]+(\d+)/i) ||
                           userMessage.match(/number[:\s]*(\w+)/i);
                           
      const roomIdMatch = userMessage.match(/room id[:\s]*([a-f0-9-]{36})/i) ||
                         userMessage.match(/room id[^:]*:[^\s]*\s*([a-f0-9-]{36})/i) ||
                         userMessage.match(/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
                         
      const bedTypeMatch = userMessage.match(/bed type[:\s]*(\w+)/i) ||
                          userMessage.match(/type[:\s]*(\w+)/i);
                          
      const statusMatch = userMessage.match(/status[:\s]*(\w+)/i);
      
      console.log('🔍 Parsing bed creation request:', {
        originalMessage: userMessage,
        bedNumberMatch: bedNumberMatch ? bedNumberMatch[1] : null,
        roomIdMatch: roomIdMatch ? roomIdMatch[1] : null,
        bedTypeMatch: bedTypeMatch ? bedTypeMatch[1] : null,
        statusMatch: statusMatch ? statusMatch[1] : null
      });
      
      if (!bedNumberMatch || !roomIdMatch) {
        throw new Error('Missing required bed information (bed number and room ID)');
      }
      
      const bedData = {
        bed_number: bedNumberMatch[1],
        room_id: roomIdMatch[1],
        bed_type: bedTypeMatch ? bedTypeMatch[1] : undefined,
        status: statusMatch ? statusMatch[1] : 'available'
      };
      
      console.log('🛏️ Creating bed with data:', bedData);
      
      // Call the MCP tool
      const result = await HospitalToolsService.callTool('create_bed', bedData);
      
      return {
        success: result && result.success !== false && !result.error,
        operation: 'create_bed',
        data: result,
        input: bedData
      };
      
    } catch (error) {
      console.error('❌ Error creating bed:', error);
      return {
        success: false,
        error: error.message,
        operation: 'create_bed'
      };
    }
  }

  // Parse and create patient from user message
  async createPatientFromMessage(userMessage) {
    try {
      // Extract patient details from message
      const firstNameMatch = userMessage.match(/first name[:\s]*(\w+)/i);
      const lastNameMatch = userMessage.match(/last name[:\s]*(\w+)/i);
      const dobMatch = userMessage.match(/date of birth[:\s]*([0-9-]+)/i);
      const patientNumberMatch = userMessage.match(/patient number[:\s]*(\w+)/i);
      
      if (!firstNameMatch || !lastNameMatch || !dobMatch || !patientNumberMatch) {
        throw new Error('Missing required patient information (patient number, first name, last name, date of birth)');
      }
      
      const patientData = {
        patient_number: patientNumberMatch[1],
        first_name: firstNameMatch[1],
        last_name: lastNameMatch[1],
        date_of_birth: dobMatch[1]
      };
      
      console.log('👤 Creating patient with data:', patientData);
      
      // Call the MCP tool
      const result = await HospitalToolsService.callTool('create_patient', patientData);
      
      return {
        success: result && !result.error,
        operation: 'create_patient',
        data: result,
        input: patientData
      };
      
    } catch (error) {
      console.error('❌ Error creating patient:', error);
      return {
        success: false,
        error: error.message,
        operation: 'create_patient'
      };
    }
  }

  // Parse and assign bed from user message
  async assignBedFromMessage(userMessage) {
    try {
      // Extract assignment details from message
      const bedIdMatch = userMessage.match(/bed id[:\s]*([a-f0-9-]+)/i);
      const patientIdMatch = userMessage.match(/patient id[:\s]*([a-f0-9-]+)/i);
      const admissionDateMatch = userMessage.match(/admission date[:\s]*([0-9-]+)/i);
      
      if (!bedIdMatch || !patientIdMatch) {
        throw new Error('Missing required assignment information (bed ID and patient ID)');
      }
      
      const assignmentData = {
        bed_id: bedIdMatch[1],
        patient_id: patientIdMatch[1],
        admission_date: admissionDateMatch ? admissionDateMatch[1] : undefined
      };
      
      console.log('🔗 Assigning bed with data:', assignmentData);
      
      // Call the MCP tool
      const result = await HospitalToolsService.callTool('assign_bed_to_patient', assignmentData);
      
      return {
        success: result && !result.error,
        operation: 'assign_bed_to_patient',
        data: result,
        input: assignmentData
      };
      
    } catch (error) {
      console.error('❌ Error assigning bed:', error);
      return {
        success: false,
        error: error.message,
        operation: 'assign_bed_to_patient'
      };
    }
  }

  async analyzeQuery(userMessage) {
    try {
      // Simple analysis for hospital queries
      const message = userMessage.toLowerCase();
      
      const analysis = {
        intent: 'general_question',
        entityType: 'general',
        action: 'help',
        keywords: [],
        needsMCPData: false,
        confidence: 0.5
      };

      // Determine if this needs hospital data
      if (message.includes('patient') || message.includes('arivu')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'patient';
        analysis.action = message.includes('list') || message.includes('all') ? 'list' : 'find';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['patient'];
      } else if (message.includes('bed')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'bed';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['bed'];
      } else if (message.includes('staff') || message.includes('doctor') || message.includes('nurse')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'staff';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['staff'];
      } else if (message.includes('appointment')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'appointment';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['appointment'];
      } else if (message.includes('equipment')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'equipment';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['equipment'];
      } else if (message.includes('supply') || message.includes('inventory')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'supply';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['supply'];
      } else if (message.includes('department')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'department';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['department'];
      } else if (message.includes('room')) {
        analysis.intent = 'query_data';
        analysis.entityType = 'room';
        analysis.action = 'list';
        analysis.needsMCPData = true;
        analysis.confidence = 0.9;
        analysis.keywords = ['room'];
      } else if (message.includes('list') || message.includes('show') || message.includes('tell me about')) {
        analysis.needsMCPData = true;
        analysis.confidence = 0.7;
      }

      return analysis;
    } catch (error) {
      console.error('Query analysis error:', error);
      return {
        intent: 'general_question',
        entityType: 'general',
        action: 'help',
        keywords: [],
        needsMCPData: false,
        confidence: 0.1
      };
    }
  }

  // Generate a summary of data for better AI responses
  async generateDataSummary(data, dataType) {
    if (!data) return 'No data available';
    
    try {
      if (Array.isArray(data)) {
        return `Found ${data.length} ${dataType} records`;
      } else if (typeof data === 'object') {
        const keys = Object.keys(data);
        return `${dataType} data with ${keys.length} fields: ${keys.slice(0, 3).join(', ')}${keys.length > 3 ? '...' : ''}`;
      } else {
        return `${dataType}: ${String(data).substring(0, 100)}`;
      }
    } catch (error) {
      return `${dataType} data (summary unavailable)`;
    }
  }
}

export default new GroqService();
