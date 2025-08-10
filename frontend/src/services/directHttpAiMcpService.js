/**
 * Direct HTTP AI MCP Service - Claude Desktop Style
 * Uses HTTP transport directly to FastMCP server with OpenAI function calling
 */

import DirectHttpMCPClient from './directHttpMcpClient.js';

class DirectHttpAIMCPService {
  /**
   * Return the agent's 'today' as the actual current date (localized, readable)
   */
  getTodayDate() {
    const now = new Date();
    return now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  constructor() {
    this.mcpClient = new DirectHttpMCPClient();
    this.openaiApiKey = null;
    this.isInitialized = false;
    this.conversationHistory = []; // Add conversation memory
    this.maxHistoryLength = 10; // Keep last 20 messages to manage token usage
    this.verboseMode = true; // Toggle for response style
    this.previousQuestions = []; // Track user's previous questions for duplicate detection
  }

  /**
   * Initialize the service with OpenAI API key
   * _serverConfig is optional since we connect directly to HTTP server
   */
  async initialize(openaiApiKey, _serverConfig = null) {
    console.log('🚀 Initializing Direct HTTP AI-MCP Service (Claude Desktop Style)...');
    
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
    console.log('✅ Direct HTTP AI-MCP Service initialized successfully (Claude Desktop Style)');
    
    return true;
  }

  /**
   * Get server information
   */
  getServerInfo() {
    return this.mcpClient.getServerInfo();
  }

  /**
   * Get available tools in OpenAI function calling format
   */
  getToolsForOpenAI() {
    const tools = this.mcpClient.getTools();
    return tools.map(tool => ({
      type: 'function',
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.inputSchema || {
          type: 'object',
          properties: {},
          required: []
        }
      }
    }));
  }

  /**
   * Get server information and status
   */
  getServerStatus() {
    const serverInfo = this.getServerInfo();
    return serverInfo;
  }

  /**
   * Check if service is connected
   */
  isConnected() {
    return this.isInitialized && this.mcpClient.isConnectedToServer();
  }

  /**
   * Process natural language request with conversation memory (Claude Desktop Style)
   */
  async processRequest(userMessage) {
    if (!this.isInitialized) {
      throw new Error('Service not initialized');
    }

    const agentStart = Date.now();
    console.log('🤖 [Hospital AI] Processing request:', userMessage);
    console.log(`[Agent] Today is: ${this.getTodayDate()}`);

    try {
      // Add user message to conversation history
      this.addToConversationHistory('user', userMessage);

      // Get current status and tools
      const availableTools = this.getToolsForOpenAI();
      const serverInfo = this.getServerInfo();
      
      console.log(`📋 Available tools: ${availableTools.length}`);
      console.log(`💭 Conversation history length: ${this.conversationHistory.length}`);
      
      // Call OpenAI with function calling and conversation history (CLAUDE DESKTOP STYLE)
      let gptResponse;
      let allFunctionResults = [];
      let iterationCount = 0;
      const maxIterations = 5; // Prevent infinite loops
      let openAITotal = 0;
      let toolTotal = 0;

      // Initial OpenAI call
      const openAIStart = Date.now();
      gptResponse = await this.callOpenAI(userMessage, availableTools, serverInfo);
      openAITotal += Date.now() - openAIStart;

      // Support multiple rounds of function calls (CLAUDE DESKTOP PATTERN)
      while (gptResponse.choices[0].message.tool_calls && iterationCount < maxIterations) {
        console.log(`� [Hospital AI] Function call iteration ${iterationCount + 1}`);

        // Execute function calls
        const toolStart = Date.now();
        const results = await this.executeFunctionCalls(gptResponse);
        toolTotal += Date.now() - toolStart;
        allFunctionResults.push(...results);

        // Add function call and results to conversation
        const assistantMessage = gptResponse.choices[0].message;
        this.addToConversationHistory('assistant', assistantMessage.content, assistantMessage.tool_calls);

        // Add function results to conversation
        for (const result of results) {
          this.addToConversationHistory('tool', JSON.stringify(result.result), null, result.function, result.tool_call_id);
        }

        // Continue conversation with updated context
        const openAIStart2 = Date.now();
        gptResponse = await this.callOpenAI(null, availableTools, serverInfo);
        openAITotal += Date.now() - openAIStart2;
        iterationCount++;
      }

      // Add final assistant response to history
      if (gptResponse.choices[0].message.content) {
        this.addToConversationHistory('assistant', gptResponse.choices[0].message.content);
      }

      const agentEnd = Date.now();
      console.log(`[Agent Timing] OpenAI total: ${openAITotal}ms, Tool total: ${toolTotal}ms, Agent total: ${agentEnd - agentStart}ms`);

      return {
        success: true,
        message: gptResponse.choices[0].message.content,
        response: gptResponse.choices[0].message.content, // For compatibility
        functionCalls: allFunctionResults,
        serverInfo: serverInfo,
        rawResponse: gptResponse,
        conversationLength: this.conversationHistory.length,
        timing: {
          openAI: openAITotal,
          tool: toolTotal,
          agent: agentEnd - agentStart
        }
      };

    } catch (error) {
      console.error('❌ Hospital AI processing failed:', error);
      return {
        success: false,
        error: error.message,
        message: `Failed to process request: ${error.message}`,
        response: `I encountered an error while processing your request: ${error.message}. Please try again.`
      };
    }
  }

  /**
   * Intelligent tool determination with AI assistance - Claude Desktop style
   */
  async determineRequiredToolsWithAI(userMessage, availableTools) {
    // Check conversation context for ongoing operations
    const contextualTools = this.analyzeConversationContext(userMessage);
    if (contextualTools.length > 0) {
      return contextualTools;
    }
    
    // Check for complex multi-step scenarios (EMERGENCY HANDLING)
    const emergencyScenario = this.detectEmergencyScenario(userMessage);
    if (emergencyScenario.length > 0) {
      return emergencyScenario;
    }
    
    // Fall back to existing logic
    return this.determineRequiredTools(userMessage, availableTools);
  }

  /**
   * Detect emergency or multi-step scenarios
   */
  detectEmergencyScenario(userMessage) {
    const message = userMessage.toLowerCase();
    const toolsNeeded = [];
    
    // Emergency patient scenario: register + allocate bed + assign doctor
    if (message.includes('emergency') && (message.includes('patient') || message.includes('register'))) {
      // Check if patient details are provided in structured format
      if (this.containsStructuredData(userMessage)) {
        const structuredTool = this.parseStructuredInput(userMessage);
        if (structuredTool && structuredTool.name === 'create_patient') {
          // Multi-step emergency process
          toolsNeeded.push(structuredTool); // Create patient first
          toolsNeeded.push({ name: 'list_beds', arguments: { status: 'available' } }); // Check available beds
          toolsNeeded.push({ name: 'list_staff', arguments: {} }); // List available doctors
          return toolsNeeded;
        }
      }
    }
    
    // Bed allocation with availability check
    if (message.includes('allocate') && message.includes('bed') && message.includes('availability')) {
      toolsNeeded.push({ name: 'list_beds', arguments: { status: 'available' } });
      return toolsNeeded;
    }
    
    // Multi-operation requests
    if (message.includes('register') && message.includes('allocate') && message.includes('bed')) {
      // User wants to register patient AND allocate bed
      if (this.containsStructuredData(userMessage)) {
        const structuredTool = this.parseStructuredInput(userMessage);
        if (structuredTool) {
          toolsNeeded.push(structuredTool);
          toolsNeeded.push({ name: 'list_beds', arguments: { status: 'available' } });
          return toolsNeeded;
        }
      }
    }
    
    return [];
  }

  /**
   * Analyze conversation context for ongoing operations
   */
  analyzeConversationContext(userMessage) {
    const recentHistory = this.conversationHistory.slice(-5);
    const toolsNeeded = [];
    
    // Look for incomplete operations in recent history
    for (const entry of recentHistory) {
      if (entry.role === 'assistant' && entry.content.includes('What should I call this department')) {
        // User is in the middle of creating a department
        if (userMessage.trim().length > 0) {
          return [{ name: 'create_department', arguments: { name: userMessage.trim() } }];
        }
      }
      // Add more contextual analysis here for other ongoing operations
    }
    
    return toolsNeeded;
  }

  /**
   * Handle incomplete requests intelligently
   */
  async handleIncompleteRequest(tool, _userMessage) {
    const requestType = tool.name;
    
    switch (requestType) {
      case '_ask_for_department_details':
        return "I'd be happy to create a new department! What should I call this department? For example: 'Cardiology', 'Emergency', 'Pediatrics', etc.";
        
      case '_ask_for_patient_details':
        return "To create a new patient, I need:\n\n" +
               "📝 **Required:** First Name, Last Name, Date of Birth (YYYY-MM-DD)\n" +
               "📋 **Optional:** Gender, Phone, Email, Address\n\n" +
               "**Example:** *Create patient John Doe born 1985-05-15*";
               
      // Add more intelligent prompts for other incomplete requests
      default:
        return "Please provide the required information for this operation.";
    }
  }

  /**
   * Resolve foreign keys by searching for IDs when users provide names
   */
  async resolveForeignKeys(tool) {
    const resolvedTool = { ...tool };
    const params = { ...tool.arguments };
    
    // Resolve department names to IDs
    if (params.department_name && !params.department_id) {
      try {
        const departments = await this.mcpClient.callTool('list_departments', {});
        const dept = departments.find(d => 
          d.name.toLowerCase().includes(params.department_name.toLowerCase())
        );
        if (dept) {
          params.department_id = dept.id;
          delete params.department_name;
        }
      } catch {
        console.warn('Could not resolve department name:', params.department_name);
      }
    }
    
    // Resolve patient names to IDs
    if (params.patient_name && !params.patient_id) {
      try {
        const patients = await this.mcpClient.callTool('search_patients', {
          first_name: params.patient_name.split(' ')[0],
          last_name: params.patient_name.split(' ')[1]
        });
        if (patients.length > 0) {
          params.patient_id = patients[0].id;
          delete params.patient_name;
        }
      } catch {
        console.warn('Could not resolve patient name:', params.patient_name);
      }
    }
    
    // Resolve doctor names to IDs
    if (params.doctor_name && !params.doctor_id) {
      try {
        const staff = await this.mcpClient.callTool('list_staff', {});
        const doctor = staff.find(s => 
          s.position.toLowerCase().includes('doctor') &&
          (s.first_name + ' ' + s.last_name).toLowerCase().includes(params.doctor_name.toLowerCase())
        );
        if (doctor) {
          params.doctor_id = doctor.id;
          delete params.doctor_name;
        }
      } catch {
        console.warn('Could not resolve doctor name:', params.doctor_name);
      }
    }
    
    resolvedTool.arguments = params;
    return resolvedTool;
  }

  /**
   * Generate response with conversation context
   */
  async generateResponseWithContext(userMessage, toolResults, availableTools) {
    if (!this.openaiApiKey) {
      return this.formatToolResults(userMessage, toolResults);
    }

    // Build conversation context for OpenAI
    const conversationContext = this.conversationHistory.slice(-6).map(entry => ({
      role: entry.role === 'assistant' ? 'assistant' : 'user',
      content: entry.content
    }));

    const systemPrompt = `You are an intelligent hospital management assistant with advanced conversation capabilities and memory.

🏥 **Hospital Management System - AI Assistant with Context**

**Current Conversation Context:**
Remember the recent conversation and provide contextually appropriate responses. Don't repeat information unnecessarily.

**Enhanced Capabilities:**
1. **Smart Parameter Collection**: Ask for missing details conversationally, one at a time
2. **Multi-Tool Operations**: Automatically resolve names to IDs when needed
3. **Conversation Memory**: Build upon previous exchanges
4. **Contextual Responses**: Tailor responses based on conversation flow

**Critical Behaviors:**

**INCOMPLETE REQUESTS:**
- For "create new department" → Ask: "What should I call this department?"
- Never create with placeholder names
- Collect required information conversationally

**FOREIGN KEY RESOLUTION:**
- When users mention names instead of IDs, automatically search for matches
- Explain what you're doing: "Let me find John Doe in our patient records..."
- If multiple matches found, ask for clarification

**CONVERSATION FLOW:**
- Remember what the user is trying to accomplish
- Build upon previous responses
- Don't ask for information already provided
- Confirm actions before executing

Available tools: ${availableTools.map(tool => tool.name).join(', ')}

Tool Results:
${toolResults.map(result => {
  if (result.error) {
    return `❌ ${result.tool}: ${result.error}`;
  } else {
    return `✅ ${result.tool}: Success`;
  }
}).join('\n')}

Respond naturally, conversationally, and contextually based on the conversation history and tool results.`;

    try {
      const messages = [
        { role: 'system', content: systemPrompt },
        ...conversationContext,
        { role: 'user', content: userMessage }
      ];

      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: messages,
          temperature: 0.7,
          max_tokens: 1500
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;

    } catch (error) {
      console.error('❌ Failed to generate contextual response:', error);
      return this.formatToolResults(userMessage, toolResults);
    }
  }

  /**
   * Determine which tools are needed based on user input
   */
  async determineRequiredTools(userMessage, _availableTools) {
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
    
    // Enhanced department creation - don't auto-create with insufficient data
    if (message.includes('create department') || message.includes('add department') || message.includes('new department')) {
      const deptParams = this.extractDepartmentParameters(userMessage);
      // Only create if we have a meaningful name (not just "new" or generic words)
      if (deptParams.name && deptParams.name.length > 3 && 
          !['new', 'department', 'create', 'add'].includes(deptParams.name.toLowerCase())) {
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
    
    // Get operations for specific records
    if (message.includes('get user') || message.includes('find user by id')) {
      const userId = this.extractId(userMessage, ['user', 'id']);
      if (userId) {
        toolsNeeded.push({ name: 'get_user_by_id', arguments: { user_id: userId } });
      }
    }
    
    if (message.includes('get patient') || message.includes('find patient by id')) {
      const patientId = this.extractId(userMessage, ['patient', 'id', 'pat']);
      if (patientId) {
        toolsNeeded.push({ name: 'get_patient_by_id', arguments: { patient_id: patientId } });
      }
    }
    
    if (message.includes('get staff') || message.includes('find staff by id')) {
      const staffId = this.extractId(userMessage, ['staff', 'employee', 'emp']);
      if (staffId) {
        toolsNeeded.push({ name: 'get_staff_by_id', arguments: { staff_id: staffId } });
      }
    }
    
    if (message.includes('get department') || message.includes('find department by id')) {
      const deptId = this.extractId(userMessage, ['department', 'dept']);
      if (deptId) {
        toolsNeeded.push({ name: 'get_department_by_id', arguments: { department_id: deptId } });
      }
    }
    
    if (message.includes('get equipment') || message.includes('find equipment by id')) {
      const equipId = this.extractId(userMessage, ['equipment', 'eq']);
      if (equipId) {
        toolsNeeded.push({ name: 'get_equipment_by_id', arguments: { equipment_id: equipId } });
      }
    }
    
    // Update operations
    if (message.includes('update user') || message.includes('edit user')) {
      const updateParams = this.extractUpdateUserParameters(userMessage);
      if (updateParams.user_id) {
        toolsNeeded.push({ name: 'update_user', arguments: updateParams });
      }
    }
    
    if (message.includes('update equipment status') || message.includes('equipment status')) {
      const statusParams = this.extractEquipmentStatusParameters(userMessage);
      if (statusParams.equipment_id && statusParams.status) {
        toolsNeeded.push({ name: 'update_equipment_status', arguments: statusParams });
      }
    }
    
    if (message.includes('update supply stock') || message.includes('stock update')) {
      const stockParams = this.extractSupplyStockParameters(userMessage);
      if (stockParams.supply_id && stockParams.quantity_change && stockParams.transaction_type) {
        toolsNeeded.push({ name: 'update_supply_stock', arguments: stockParams });
      }
    }
    
    // Assignment operations
    if (message.includes('assign bed') || message.includes('bed assignment')) {
      const assignParams = this.extractBedAssignmentParameters(userMessage);
      if (assignParams.bed_id && assignParams.patient_id) {
        toolsNeeded.push({ name: 'assign_bed_to_patient', arguments: assignParams });
      }
    }
    
    if (message.includes('discharge bed') || message.includes('bed discharge')) {
      const dischargeParams = this.extractBedDischargeParameters(userMessage);
      if (dischargeParams.bed_id) {
        toolsNeeded.push({ name: 'discharge_bed', arguments: dischargeParams });
      }
    }
    
    // Delete operations
    if (message.includes('delete user') || message.includes('remove user')) {
      const userId = this.extractId(userMessage, ['user', 'id']);
      if (userId) {
        toolsNeeded.push({ name: 'delete_user', arguments: { user_id: userId } });
      }
    }
    
    // Category creation operations
    if (message.includes('create equipment category') || message.includes('add equipment category')) {
      const categoryParams = this.extractCategoryParameters(userMessage, 'equipment');
      if (categoryParams.name) {
        toolsNeeded.push({ name: 'create_equipment_category', arguments: categoryParams });
      }
    }
    
    if (message.includes('create supply category') || message.includes('add supply category')) {
      const categoryParams = this.extractCategoryParameters(userMessage, 'supply');
      if (categoryParams.name) {
        toolsNeeded.push({ name: 'create_supply_category', arguments: categoryParams });
      }
    }
    
    // Legacy operations
    if (message.includes('create legacy user') || message.includes('add legacy user')) {
      const legacyParams = this.extractLegacyUserParameters(userMessage);
      if (legacyParams.name && legacyParams.email) {
        toolsNeeded.push({ name: 'create_legacy_user', arguments: legacyParams });
      }
    }
    
    if (message.includes('list legacy users') || message.includes('show legacy users')) {
      toolsNeeded.push({ name: 'list_legacy_users', arguments: {} });
    }
    
    console.log('🔧 Tools needed:', toolsNeeded);
    return toolsNeeded;
  }

  /**
   * Generate response using OpenAI with enhanced system prompt for intelligent conversation
   */
  async generateResponse(userMessage, toolResults, availableTools) {
    // If no OpenAI API key, provide simple formatted response
    if (!this.openaiApiKey) {
      return this.formatToolResults(userMessage, toolResults);
    }

    const systemPrompt = `You are an intelligent hospital management assistant with advanced conversation capabilities. You can perform complex multi-step operations and have memory of previous interactions.

🏥 **Hospital Management System - AI Assistant**

**Core Capabilities:**
1. **Intelligent Parameter Collection**: When users request operations without complete information, ask for missing details conversationally
2. **Multi-Tool Operations**: Automatically resolve foreign keys by searching for IDs when users provide names
3. **Conversation Memory**: Remember context and avoid asking for information already provided
4. **Smart Validation**: Validate data before operations and provide helpful feedback

**Advanced Behaviors:**

**1. INCOMPLETE CREATE REQUESTS:**
When users say "create new department" without details:
- ASK: "I'd be happy to create a new department! What should I call this department? For example: 'Cardiology', 'Emergency', 'Pediatrics', etc."
- NEVER create with placeholder names like "New" or "Unnamed"
- Collect required fields conversationally before proceeding

**2. FOREIGN KEY RESOLUTION:**
When operations require IDs but users provide names:
- AUTOMATICALLY search for IDs using available list/search tools
- Example: "Create appointment for John Doe with Dr. Smith in Cardiology"
  1. Search patients for "John Doe" to get patient_id
  2. Search staff for "Dr. Smith" to get doctor_id  
  3. Search departments for "Cardiology" to get department_id
  4. Then create appointment with resolved IDs

**3. CONVERSATION FLOW:**
- Remember what the user is trying to accomplish
- If missing information, ask ONE question at a time
- Provide examples of valid formats
- Confirm before executing operations

**4. ERROR HANDLING:**
- If foreign key lookups fail, suggest alternatives
- Provide helpful error messages with next steps
- Offer to list available options when searches fail

**Available Tools:**
${availableTools.map(tool => `- ${tool.name}: ${tool.description}`).join('\n')}

**Tool Execution Results:**
${toolResults.map(result => {
  if (result.error) {
    return `❌ ${result.tool}: Error - ${result.error}`;
  } else {
    return `✅ ${result.tool}: ${JSON.stringify(result.result, null, 2)}`;
  }
}).join('\n\n')}

**Response Guidelines:**
- Be conversational and helpful
- Ask clarifying questions when needed
- Explain what you're doing for multi-step operations
- Provide clear success/failure feedback
- Hide technical UUIDs from users
- Focus on user-friendly information
- Remember the conversation context

Respond naturally and helpfully based on the user's request and the tool results.`;

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
          } catch {
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
          'patient_id': 'patient_id',
          'username': 'username',
          'role': 'role',
          'password': 'password_hash',
          'equipment_id': 'equipment_id',
          'category_id': 'category_id',
          'item_code': 'item_code',
          'unit_of_measure': 'unit_of_measure'
        };
        
        const mappedField = fieldMappings[field] || field;
        params[mappedField] = value;
      }
    }
    
    // Determine operation type based on provided fields
    if (params.bed_number && params.room_id) {
      operationType = 'create_bed';
    } else if (params.username && params.email && params.role && params.first_name && params.last_name) {
      operationType = 'create_user';
      // Generate password hash if not provided (using a simple default)
      if (!params.password_hash) {
        params.password_hash = 'temp_password_hash'; // This should be handled properly in production
      }
    } else if (params.first_name && params.last_name && params.date_of_birth) {
      operationType = 'create_patient';
      // Generate patient number if not provided
      if (!params.patient_number) {
        params.patient_number = `PAT${String(Math.floor(Math.random() * 9000) + 1000)}`;
      }
    } else if (params.employee_id && params.department_id && params.position) {
      operationType = 'create_staff';
    } else if (params.name && !params.bed_number && !params.first_name && !params.username) {
      operationType = 'create_department';
    } else if (params.room_number && params.department_id) {
      operationType = 'create_room';
    } else if (params.patient_id && params.doctor_id && params.appointment_date) {
      operationType = 'create_appointment';
    } else if (params.equipment_id && params.name && params.category_id) {
      operationType = 'create_equipment';
    } else if (params.item_code && params.name && params.category_id && params.unit_of_measure) {
      operationType = 'create_supply';
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
    
    // Extract patient name or ID
    const patientMatch = message.match(/patient\s+(\w+)|for\s+([a-zA-Z\s]+)(?:\s+with|\s+in|$)/i);
    if (patientMatch) {
      const patientInfo = patientMatch[1] || patientMatch[2];
      if (patientInfo && patientInfo.trim()) {
        // If it looks like an ID (PAT123), treat as ID; otherwise treat as name
        if (/^PAT\d+$/i.test(patientInfo.trim())) {
          params.patient_id = patientInfo.trim();
        } else {
          params.patient = patientInfo.trim();
        }
      }
    }
    
    // Extract doctor name or ID
    const doctorMatch = message.match(/doctor\s+([a-zA-Z\s.]+)|with\s+([a-zA-Z\s.]+)(?:\s+in|\s+on|$)/i);
    if (doctorMatch) {
      const doctorInfo = doctorMatch[1] || doctorMatch[2];
      if (doctorInfo && doctorInfo.trim()) {
        // If it looks like an ID (DOC123), treat as ID; otherwise treat as name
        if (/^DOC\d+$/i.test(doctorInfo.trim()) || /^D\d+$/i.test(doctorInfo.trim())) {
          params.doctor_id = doctorInfo.trim();
        } else {
          params.doctor = doctorInfo.trim();
        }
      }
    }
    
    // Extract department name or ID
    const deptMatch = message.match(/in\s+([a-zA-Z\s]+)|department\s+([a-zA-Z\s]+)/i);
    if (deptMatch) {
      const deptInfo = deptMatch[1] || deptMatch[2];
      if (deptInfo && deptInfo.trim()) {
        // If it looks like an ID (DEPT123), treat as ID; otherwise treat as name
        if (/^DEPT\d+$/i.test(deptInfo.trim())) {
          params.department_id = deptInfo.trim();
        } else {
          params.department = deptInfo.trim();
        }
      }
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
   * Extract ID from message for various entity types
   */
  extractId(message, entityType) {
    const patterns = {
      'patient': [/patient\s+([A-Z0-9]+)/i, /pat([0-9]+)/i],
      'staff': [/staff\s+([A-Z0-9]+)/i, /emp([0-9]+)/i],
      'user': [/user\s+([A-Z0-9-]+)/i],
      'department': [/department\s+([A-Z0-9]+)/i, /dept\s+([A-Z0-9]+)/i],
      'doctor': [/doctor\s+([A-Z0-9]+)/i, /dr\s+([A-Z0-9]+)/i],
      'equipment': [/equipment\s+([A-Z0-9]+)/i, /eq([0-9]+)/i]
    };
    
    const entityPatterns = patterns[entityType] || [];
    for (const pattern of entityPatterns) {
      const match = message.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  }

  /**
   * Extract status from message
   */
  extractStatus(message) {
    const statusKeywords = ['available', 'occupied', 'maintenance', 'active', 'inactive', 'operational', 'broken'];
    for (const status of statusKeywords) {
      if (message.toLowerCase().includes(status)) {
        return status;
      }
    }
    return null;
  }

  /**
   * Extract date from message
   */
  extractDate(message) {
    const dateMatch = message.match(/(\d{4}-\d{2}-\d{2})/);
    return dateMatch ? dateMatch[1] : null;
  }

  /**
   * Extract bed assignment parameters
   */
  extractBedAssignmentParameters(message) {
    const params = {};
    params.bed_id = this.extractId(message, 'bed') || message.match(/bed\s+([A-Z0-9]+)/i)?.[1];
    params.patient_id = this.extractId(message, 'patient') || message.match(/patient\s+([A-Z0-9]+)/i)?.[1];
    params.admission_date = this.extractDate(message);
    return params;
  }

  /**
   * Extract discharge parameters
   */
  extractDischargeParameters(message) {
    const params = {};
    params.bed_id = this.extractId(message, 'bed') || message.match(/bed\s+([A-Z0-9]+)/i)?.[1];
    params.discharge_date = this.extractDate(message);
    return params;
  }

  /**
   * Extract equipment status update parameters
   */
  extractEquipmentStatusUpdateParameters(message) {
    const params = {};
    params.equipment_id = this.extractId(message, 'equipment');
    params.status = this.extractStatus(message);
    const notesMatch = message.match(/notes?\s*:?\s*([^,.\n]+)/i);
    if (notesMatch) {
      params.notes = notesMatch[1].trim();
    }
    return params;
  }

  /**
   * Extract category parameters (for equipment/supply categories)
   */
  extractCategoryParameters(message, type) {
    const params = {};
    const categoryMatch = message.match(new RegExp(`${type}\\s+category\\s+([a-zA-Z\\s]+)`, 'i'));
    if (categoryMatch) {
      params.name = categoryMatch[1].trim();
    }
    const descMatch = message.match(/description\s*:?\s*([^,.\n]+)/i);
    if (descMatch) {
      params.description = descMatch[1].trim();
    }
    return params;
  }

  /**
   * Extract supply stock update parameters
   */
  extractSupplyStockUpdateParameters(message) {
    const params = {};
    params.supply_id = this.extractId(message, 'supply') || message.match(/supply\s+([A-Z0-9]+)/i)?.[1];
    
    const quantityMatch = message.match(/quantity\s*:?\s*([+-]?\d+)/i) || message.match(/([+-]?\d+)\s*units?/i);
    if (quantityMatch) {
      params.quantity_change = parseInt(quantityMatch[1]);
    }
    
    const typeMatch = message.match(/type\s*:?\s*(purchase|usage|adjustment|return)/i);
    if (typeMatch) {
      params.transaction_type = typeMatch[1].toLowerCase();
    }
    
    const performedByMatch = message.match(/by\s+([A-Z0-9]+)/i);
    if (performedByMatch) {
      params.performed_by = performedByMatch[1];
    }
    
    return params;
  }

  /**
   * Extract user update parameters
   */
  extractUserUpdateParameters(message) {
    const params = {};
    params.user_id = this.extractId(message, 'user');
    
    const usernameMatch = message.match(/username\s*:?\s*([a-zA-Z0-9_]+)/i);
    if (usernameMatch) {
      params.username = usernameMatch[1];
    }
    
    const emailMatch = message.match(/email\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i);
    if (emailMatch) {
      params.email = emailMatch[1];
    }
    
    const roleMatch = message.match(/role\s*:?\s*([a-zA-Z]+)/i);
    if (roleMatch) {
      params.role = roleMatch[1];
    }
    
    const activeMatch = message.match(/(activate|deactivate|active|inactive)/i);
    if (activeMatch) {
      params.is_active = activeMatch[1].toLowerCase().includes('activ') && !activeMatch[1].toLowerCase().includes('deactiv');
    }
    
    return params;
  }

  /**
   * Extract legacy user parameters
   */
  extractLegacyUserParameters(message) {
    const params = {};
    
    const nameMatch = message.match(/name\s*:?\s*([a-zA-Z\s]+)/i);
    if (nameMatch) {
      params.name = nameMatch[1].trim();
    }
    
    const emailMatch = message.match(/email\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i);
    if (emailMatch) {
      params.email = emailMatch[1];
    }
    
    const addressMatch = message.match(/address\s*:?\s*([^,\n]+)/i);
    if (addressMatch) {
      params.address = addressMatch[1].trim();
    }
    
    const phoneMatch = message.match(/phone\s*:?\s*([\d\s\-()]+)/i);
    if (phoneMatch) {
      params.phone = phoneMatch[1].trim();
    }
    
    return params;
  }

  /**
   * Extract log interaction parameters
   */
  extractLogParameters(message) {
    const params = {};
    
    const agentMatch = message.match(/agent[_\s]type\s*:?\s*([a-zA-Z]+)/i);
    if (agentMatch) {
      params.agent_type = agentMatch[1];
    }
    
    const queryMatch = message.match(/query\s*:?\s*([^,\n]+)/i);
    if (queryMatch) {
      params.query = queryMatch[1].trim();
    }
    
    const responseMatch = message.match(/response\s*:?\s*([^,\n]+)/i);
    if (responseMatch) {
      params.response = responseMatch[1].trim();
    }
    
    return params;
  }

  /**
   * Extract parameters for user updates
   */
  extractUpdateUserParameters(message) {
    const params = {};
    
    // Extract user ID
    const userId = this.extractId(message, 'user');
    if (userId) {
      params.user_id = userId;
    }
    
    // Extract updateable fields
    const emailMatch = message.match(/email[:\s]+([^\s,]+)/i);
    if (emailMatch) {
      params.email = emailMatch[1];
    }
    
    const phoneMatch = message.match(/phone[:\s]+([^\s,]+)/i);
    if (phoneMatch) {
      params.phone = phoneMatch[1];
    }
    
    const roleMatch = message.match(/role[:\s]+(\w+)/i);
    if (roleMatch) {
      params.role = roleMatch[1];
    }
    
    if (message.toLowerCase().includes('active')) {
      params.is_active = true;
    } else if (message.toLowerCase().includes('inactive')) {
      params.is_active = false;
    }
    
    return params;
  }

  /**
   * Extract equipment status parameters
   */
  extractEquipmentStatusParameters(message) {
    const params = {};
    
    const equipId = this.extractId(message, 'equipment');
    if (equipId) {
      params.equipment_id = equipId;
    }
    
    if (message.toLowerCase().includes('operational')) {
      params.status = 'operational';
    } else if (message.toLowerCase().includes('maintenance')) {
      params.status = 'maintenance';
    } else if (message.toLowerCase().includes('broken') || message.toLowerCase().includes('out of order')) {
      params.status = 'broken';
    }
    
    const notesMatch = message.match(/notes?[:\s]+([^,]+)/i);
    if (notesMatch) {
      params.notes = notesMatch[1].trim();
    }
    
    return params;
  }

  /**
   * Extract supply stock update parameters
   */
  extractSupplyStockParameters(message) {
    const params = {};
    
    const supplyId = this.extractId(message, 'supply');
    if (supplyId) {
      params.supply_id = supplyId;
    }
    
    const quantityMatch = message.match(/(\+?-?\d+)\s*(?:units?|pieces?|items?)?/i);
    if (quantityMatch) {
      params.quantity_change = parseInt(quantityMatch[1]);
    }
    
    if (message.toLowerCase().includes('add') || message.toLowerCase().includes('restock')) {
      params.transaction_type = 'restock';
    } else if (message.toLowerCase().includes('use') || message.toLowerCase().includes('consume')) {
      params.transaction_type = 'usage';
    } else if (message.toLowerCase().includes('adjust')) {
      params.transaction_type = 'adjustment';
    }
    
    const performedByMatch = message.match(/by[:\s]+(\w+)/i);
    if (performedByMatch) {
      params.performed_by = performedByMatch[1];
    }
    
    return params;
  }

  /**
   * Add message to conversation history with memory management
   */
  addToConversationHistory(role, content, tool_calls = null, functionName = null, tool_call_id = null) {
    const message = { role, content };
    
    if (tool_calls) {
      message.tool_calls = tool_calls;
    }
    
    if (functionName) {
      message.name = functionName;
    }

    if (tool_call_id) {
      message.tool_call_id = tool_call_id;
    }
    
    this.conversationHistory.push(message);
    
    // Manage conversation memory to prevent token overflow
    if (this.conversationHistory.length > this.maxHistoryLength) {
      // Keep system message and recent conversations
      const systemMessages = this.conversationHistory.filter(msg => msg.role === 'system');
      const recentMessages = this.conversationHistory.slice(-this.maxHistoryLength + systemMessages.length);
      this.conversationHistory = [...systemMessages, ...recentMessages];
    }
  }

  /**
   * Call OpenAI with function calling and conversation history (Claude Desktop Style)
   */
  async callOpenAI(userMessage, functions, _serverInfo) {
    const systemPrompt = `You are Hospital AI, an advanced AI assistant specialized in comprehensive hospital management. You're connected to a real hospital management system through MCP (Model Context Protocol).

Today is: ${this.getTodayDate()}.

🏥 **Hospital System Context:**
- Server: Direct HTTP FastMCP Server
- Available Tools: ${functions.length} medical management tools
- Connection: Direct HTTP communication via MCP protocol

**CRITICAL: Parameter Requirements:**
NEVER call functions without required parameters. If a user requests an action but doesn't provide the necessary information:
1. Ask for the missing required information FIRST
2. Only call functions after you have ALL required parameters
3. For create_patient, you MUST have: first_name, last_name, date_of_birth
4. For create_user, you MUST have: username, email, password_hash, role, first_name, last_name
5. For create_appointment, you MUST have: patient_id, doctor_id (NOT staff_id), department_id, appointment_date

**CRITICAL: Foreign Key Resolution (Claude Desktop Style):**
When users provide human-readable names instead of IDs, always resolve them first:
1. For room_id: Ask "Which room?" → User says "Room 101" → Use search_rooms or list_rooms to find room_id
2. For department_id: Ask "Which department?" → User says "Emergency" → Use list_departments to find department_id  
3. For doctor_id: Ask "Which doctor?" → User says "Dr. Smith" → Use list_staff to find staff member who is a doctor
4. For patient_id: Ask "Which patient?" → User says "John Doe" → Use search_patients to find patient_id
5. For category_id: Ask "Which category?" → User says "Medical Equipment" → Use list categories to find category_id

**WORKFLOW: Always resolve foreign keys before create operations:**
- If user says "create bed in room 101" → FIRST find room_id for "room 101", THEN create bed
- If user says "create appointment with Dr. Smith" → FIRST find doctor_id for "Dr. Smith", THEN create appointment
- If user says "assign bed to John Doe" → FIRST find patient_id for "John Doe", THEN assign bed

**NEVER ask users for UUIDs directly - always use human names and resolve automatically**

**CRITICAL: Emergency Scenario Handling:**
When users mention "emergency patient" scenarios:
1. FIRST create the patient with provided details
2. THEN check available beds with list_beds(status="available")
3. If no beds are available, create a new emergency bed using create_bed
4. THEN assign the first truly available bed to the patient
5. THEN list available doctors/staff with list_staff()
6. THEN create an appointment with correct doctor_id (NOT staff_id)
7. Use simple appointment_date format like "2025-08-10 10:00" instead of "2025-08-10T10:00:00Z"
8. Provide comprehensive response with next steps for bed assignment and doctor allocation

📋 **Your Identity & Capabilities:**
You are Hospital AI - NOT Claude. Always introduce yourself as "Hospital AI".
You have access to a complete hospital management system with tools for:
- 👥 Patient management (create, search, update patient records)
- 🏢 Department operations (manage hospital departments)
- 👨‍⚕️ Staff management (doctors, nurses, administrators)
- 🛏️ Bed management (room assignments, occupancy)
- 🏥 Equipment tracking (medical devices, maintenance)
- 📦 Supply inventory (medications, consumables)
- 📅 Appointment scheduling
- 📊 Reporting and analytics

🔧 **Function Calling Instructions:**
- Always use the exact function names provided
- Use structured data from user when available
- For create operations, extract all provided parameters
- NEVER call create functions without required parameters - ask for missing information first
- CRITICAL: Always use exact parameter names as defined in schemas:
  * For appointments: use 'doctor_id' NOT 'staff_id', 'doctor', 'staff', or 'appointment_type'
  * For patients: use 'patient_number' only if provided, otherwise let it auto-generate
  * For equipment: use 'equipment_id' as specified
  * For search_patients: use specific field names (first_name, last_name, phone, email) NOT 'query'
- For emergency scenarios, execute multiple related functions in sequence
- Provide clear, helpful responses based on actual tool results
- If a parameter name doesn't exist in the schema, don't use it

**CRITICAL: Multi-Step Operations with Foreign Key Resolution:**
For complex requests that need foreign keys, follow this workflow:
1. If user says "create bed in room 101":
   → FIRST call list_rooms to find room_id for room "101"
   → THEN call create_bed with the found room_id
2. If user says "create appointment with Dr. Smith":
   → FIRST call list_staff to find doctor_id for "Dr. Smith"
   → THEN call create_appointment with the found doctor_id
3. If user says "assign bed to John Doe":
   → FIRST call search_patients with first_name="John", last_name="Doe"
   → THEN call assign_bed_to_patient with the found patient_id

**ALWAYS resolve human names to IDs before create operations - this is how Claude Desktop works!**

**Response Guidelines:**
- Be conversational and professional
- If user says "Add new patient" without details, ask for patient information first
- Explain what actions you're taking
- Provide clear success/failure feedback
- Hide technical UUIDs from users
- Focus on user-friendly information
- For emergency scenarios, be decisive and efficient

Use the available functions to help users with hospital management tasks.`;

    const messages = [{ role: 'system', content: systemPrompt }];
    
    // Add conversation history
    messages.push(...this.conversationHistory);
    
    // Add current user message if provided
    if (userMessage) {
      messages.push({ role: 'user', content: userMessage });
    }

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.openaiApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4-turbo-preview',
          messages: messages,
          tools: functions,
          tool_choice: 'auto',
          temperature: 0.7,
          max_tokens: 2000
        })
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      console.log('🎯 OpenAI Response:', data.choices[0].message);
      
      return data;

    } catch (error) {
      console.error('❌ OpenAI API call failed:', error);
      throw error;
    }
  }

  /**
   * Execute function calls from OpenAI response (Claude Desktop Style)
   */
  async executeFunctionCalls(gptResponse) {
    const results = [];
    const toolCalls = gptResponse.choices[0].message.tool_calls || [];

    for (const toolCall of toolCalls) {
      const functionName = toolCall.function.name;
      const functionArgs = JSON.parse(toolCall.function.arguments);

      console.log(`🔧 Executing function: ${functionName}`, functionArgs);

      try {
        // Call the actual MCP tool
        const result = await this.mcpClient.callTool(functionName, functionArgs);
        
        console.log(`✅ Function ${functionName} completed:`, result);

        results.push({
          function: functionName,
          arguments: functionArgs,
          result: result,
          tool_call_id: toolCall.id
        });

      } catch (error) {
        console.error(`❌ Function ${functionName} failed:`, error);
        
        results.push({
          function: functionName,
          arguments: functionArgs,
          error: error.message,
          tool_call_id: toolCall.id
        });
      }
    }

    return results;
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
