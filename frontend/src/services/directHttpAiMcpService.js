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
    this.openaiApiKey = import.meta.env.VITE_OPENAI_API_KEY; // Get from environment
    this.isInitialized = false;
    this.conversationHistory = []; // Add conversation memory
    this.maxHistoryLength = 6; // Keep last 6 messages to manage token usage better
    this.verboseMode = true; // Toggle for response style
    this.previousQuestions = []; // Track user's previous questions for duplicate detection
  }

  /**
   * Calculate Levenshtein distance for fuzzy matching
   */
  calculateLevenshteinDistance(str1, str2) {
    const matrix = [];
    
    // Initialize matrix
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    // Fill matrix
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // substitution
            matrix[i][j - 1] + 1,     // insertion
            matrix[i - 1][j] + 1      // deletion
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  }

  /**
   * Calculate similarity percentage between two strings
   */
  calculateSimilarity(str1, str2) {
    const distance = this.calculateLevenshteinDistance(str1.toLowerCase(), str2.toLowerCase());
    const maxLength = Math.max(str1.length, str2.length);
    return ((maxLength - distance) / maxLength) * 100;
  }

  /**
   * Find similar patient names using fuzzy matching
   */
  async findSimilarPatientNames(searchName, threshold = 70) {
    try {
      // First get all patients
      const allPatientsResult = await this.mcpClient.callTool('list_patients', {});
      
      if (!allPatientsResult.content || !Array.isArray(allPatientsResult.content)) {
        return [];
      }

      const patients = allPatientsResult.content;
      const matches = [];

      // Check each patient for similar names
      for (const patient of patients) {
        const fullName = `${patient.first_name} ${patient.last_name}`.trim();
        const firstNameSimilarity = this.calculateSimilarity(searchName, patient.first_name);
        const lastNameSimilarity = this.calculateSimilarity(searchName, patient.last_name);
        const fullNameSimilarity = this.calculateSimilarity(searchName, fullName);

        // Check if any name component has similarity above threshold
        const maxSimilarity = Math.max(firstNameSimilarity, lastNameSimilarity, fullNameSimilarity);
        
        if (maxSimilarity >= threshold) {
          matches.push({
            patient,
            similarity: maxSimilarity,
            matchType: maxSimilarity === firstNameSimilarity ? 'first_name' : 
                      maxSimilarity === lastNameSimilarity ? 'last_name' : 'full_name'
          });
        }
      }

      // Sort by similarity (highest first)
      matches.sort((a, b) => b.similarity - a.similarity);
      
      return matches;
    } catch (error) {
      console.error('Error finding similar patient names:', error);
      return [];
    }
  }

  /**
   * Find similar doctor/staff names using fuzzy matching
   */
  async findSimilarDoctorNames(searchName, threshold = 70) {
    try {
      // First get all staff
      const allStaffResult = await this.mcpClient.callTool('list_staff', {});
      
      if (!allStaffResult.content || !Array.isArray(allStaffResult.content)) {
        return [];
      }

      const staff = allStaffResult.content;
      const matches = [];

      // Check each staff member for similar names (doctors and all staff)
      for (const member of staff) {
        const fullName = `${member.first_name} ${member.last_name}`.trim();
        const firstNameSimilarity = this.calculateSimilarity(searchName, member.first_name);
        const lastNameSimilarity = this.calculateSimilarity(searchName, member.last_name);
        const fullNameSimilarity = this.calculateSimilarity(searchName, fullName);

        // Check if any name component has similarity above threshold
        const maxSimilarity = Math.max(firstNameSimilarity, lastNameSimilarity, fullNameSimilarity);
        
        if (maxSimilarity >= threshold) {
          matches.push({
            staff: member,
            similarity: maxSimilarity,
            matchType: maxSimilarity === firstNameSimilarity ? 'first_name' : 
                      maxSimilarity === lastNameSimilarity ? 'last_name' : 'full_name'
          });
        }
      }

      // Sort by similarity (highest first)
      matches.sort((a, b) => b.similarity - a.similarity);
      
      return matches;
    } catch (error) {
      console.error('Error finding similar doctor/staff names:', error);
      return [];
    }
  }

  /**
   * Find similar department names using fuzzy matching
   */
  async findSimilarDepartmentNames(searchName, threshold = 70) {
    try {
      // First get all departments
      const allDepartmentsResult = await this.mcpClient.callTool('list_departments', {});
      
      if (!allDepartmentsResult.content || !Array.isArray(allDepartmentsResult.content)) {
        return [];
      }

      const departments = allDepartmentsResult.content;
      const matches = [];

      // Check each department for similar names
      for (const dept of departments) {
        const nameSimilarity = this.calculateSimilarity(searchName, dept.name);
        const descriptionSimilarity = dept.description ? 
          this.calculateSimilarity(searchName, dept.description) : 0;

        // Check if name or description has similarity above threshold
        const maxSimilarity = Math.max(nameSimilarity, descriptionSimilarity);
        
        if (maxSimilarity >= threshold) {
          matches.push({
            department: dept,
            similarity: maxSimilarity,
            matchType: maxSimilarity === nameSimilarity ? 'name' : 'description'
          });
        }
      }

      // Sort by similarity (highest first)
      matches.sort((a, b) => b.similarity - a.similarity);
      
      return matches;
    } catch (error) {
      console.error('Error finding similar department names:', error);
      return [];
    }
  }

  // Helper function to generate Google Meet-style links
  generateMeetingLink() {
    // Generate a simple Google Meet-style room code
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    const generateSegment = (length) => {
      let result = '';
      for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    };
    
    const segment1 = generateSegment(3);
    const segment2 = generateSegment(4);
    const segment3 = generateSegment(3);
    
    return `https://meet.google.com/${segment1}-${segment2}-${segment3}`;
  }

  /**
   * Initialize the service
   */
  async initialize() {
    console.log('🚀 Initializing Direct HTTP AI-MCP Service (Claude Desktop Style)...');
    
    if (!this.openaiApiKey) {
      console.error('❌ OpenAI API key not configured in environment variables');
      return false;
    }

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
   * Validate conversation history for proper tool call/response structure
   */
  validateConversationStructure() {
    const pendingToolCalls = new Set();
    
    for (const message of this.conversationHistory) {
      if (message.role === 'assistant' && message.tool_calls) {
        // Add all tool call IDs to pending set
        for (const toolCall of message.tool_calls) {
          pendingToolCalls.add(toolCall.id);
        }
      } else if (message.role === 'tool' && message.tool_call_id) {
        // Remove responded tool call ID
        pendingToolCalls.delete(message.tool_call_id);
      }
    }
    
    if (pendingToolCalls.size > 0) {
      console.warn(`⚠️ Found ${pendingToolCalls.size} unresolved tool calls:`, Array.from(pendingToolCalls));
      return false;
    }
    
    return true;
  }

  /**
   * Clear conversation history (useful for fresh context)
   */
  clearConversationHistory() {
    this.conversationHistory = [];
    console.log('🧹 Conversation history cleared');
  }

  /**
   * Check if service is connected
   */
  isConnected() {
    return this.isInitialized && this.mcpClient.isConnectedToServer();
  }

  /**
   * Call MCP tool directly without AI processing (for form submissions)
   */
  async callToolDirectly(toolName, arguments_obj) {
    if (!this.isInitialized) {
      throw new Error('Service not initialized');
    }

    try {
      console.log(`🔧 Direct tool call: ${toolName}`, arguments_obj);
      
      const result = await this.mcpClient.callTool(toolName, arguments_obj);
      console.log(`✅ Direct tool result:`, result);
      
      // Handle the response from the MCP client
      // The response format is: { jsonrpc: "2.0", id: X, result: { content: [{ type: "text", text: "JSON_STRING" }] } }
      if (result && result.result && result.result.content && Array.isArray(result.result.content) && result.result.content[0]?.text) {
        try {
          const parsedResult = JSON.parse(result.result.content[0].text);
          console.log(`✅ Parsed result:`, parsedResult);
          return parsedResult;
        } catch (parseError) {
          console.error(`❌ Failed to parse result JSON:`, parseError);
          // If parsing fails, return a structured error
          return {
            success: false,
            message: `Failed to parse response: ${result.result.content[0].text}`
          };
        }
      }
      
      // Fallback - if response format is unexpected
      console.warn(`⚠️ Unexpected response format:`, result);
      return {
        success: false,
        message: 'Unexpected response format from server',
        raw_response: result
      };
    } catch (error) {
      console.error(`❌ Direct tool call failed for ${toolName}:`, error);
      return {
        success: false,
        message: error.message || 'Unknown error occurred'
      };
    }
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
    
    // Safe date logging
    let currentDate;
    try {
      currentDate = this.getTodayDate();
    } catch (error) {
      console.warn('Error getting date for logging:', error);
      // Dynamic fallback - always gets current date
      currentDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    }
    console.log(`[Agent] Today is: ${currentDate}`);

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
  async handleIncompleteRequest(tool) {
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
    
    // Resolve department names to IDs with fuzzy matching
    if (params.department_name && !params.department_id) {
      try {
        const departments = await this.mcpClient.callTool('list_departments', {});
        const dept = departments.find(d => 
          d.name.toLowerCase().includes(params.department_name.toLowerCase())
        );
        
        if (dept) {
          params.department_id = dept.id;
          delete params.department_name;
        } else {
          // If exact search fails, try fuzzy matching
          console.log(`🔍 Exact search for department "${params.department_name}" failed, trying fuzzy matching...`);
          const similarMatches = await this.findSimilarDepartmentNames(params.department_name, 70);
          
          if (similarMatches.length > 0) {
            const bestMatch = similarMatches[0];
            console.log(`🎯 Found similar department: ${bestMatch.department.name} (${bestMatch.similarity.toFixed(1)}% match)`);
            params.department_id = bestMatch.department.id;
            params._fuzzy_match_info = {
              original_search: params.department_name,
              matched_name: bestMatch.department.name,
              similarity: bestMatch.similarity
            };
            delete params.department_name;
          }
        }
      } catch (error) {
        console.warn('Could not resolve department name:', params.department_name, error);
      }
    }
    
    // Resolve patient names to IDs with fuzzy matching
    if ((params.patient_name || (params.first_name && params.last_name)) && !params.patient_id) {
      try {
        let searchName = params.patient_name;
        let searchParams = {};
        
        if (params.first_name && params.last_name) {
          searchName = `${params.first_name} ${params.last_name}`;
          searchParams = {
            first_name: params.first_name,
            last_name: params.last_name
          };
        } else if (params.patient_name) {
          const nameParts = params.patient_name.split(' ');
          searchParams = {
            first_name: nameParts[0],
            last_name: nameParts[1]
          };
        }
        
        // First try exact search
        const patients = await this.mcpClient.callTool('search_patients', searchParams);
        
        if (patients.length > 0) {
          params.patient_id = patients[0].id;
          delete params.patient_name;
          delete params.first_name;
          delete params.last_name;
        } else {
          // If exact search fails, try fuzzy matching
          console.log(`🔍 Exact search for "${searchName}" failed, trying fuzzy matching...`);
          const similarMatches = await this.findSimilarPatientNames(searchName, 70);
          
          if (similarMatches.length > 0) {
            const bestMatch = similarMatches[0];
            console.log(`🎯 Found similar patient: ${bestMatch.patient.first_name} ${bestMatch.patient.last_name} (${bestMatch.similarity.toFixed(1)}% match)`);
            params.patient_id = bestMatch.patient.id;
            params._fuzzy_match_info = {
              original_search: searchName,
              matched_name: `${bestMatch.patient.first_name} ${bestMatch.patient.last_name}`,
              similarity: bestMatch.similarity
            };
            delete params.patient_name;
            delete params.first_name;
            delete params.last_name;
          }
        }
      } catch (error) {
        console.warn('Could not resolve patient name:', params.patient_name || `${params.first_name} ${params.last_name}`, error);
      }
    }
    
    // Resolve doctor names to IDs with fuzzy matching
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
        } else {
          // If exact search fails, try fuzzy matching for doctors
          console.log(`🔍 Exact search for doctor "${params.doctor_name}" failed, trying fuzzy matching...`);
          const similarMatches = await this.findSimilarDoctorNames(params.doctor_name, 70);
          
          // Filter to only doctors
          const doctorMatches = similarMatches.filter(match => 
            match.staff.position.toLowerCase().includes('doctor')
          );
          
          if (doctorMatches.length > 0) {
            const bestMatch = doctorMatches[0];
            console.log(`🎯 Found similar doctor: ${bestMatch.staff.first_name} ${bestMatch.staff.last_name} (${bestMatch.similarity.toFixed(1)}% match)`);
            params.doctor_id = bestMatch.staff.id;
            params._fuzzy_match_info = {
              original_search: params.doctor_name,
              matched_name: `${bestMatch.staff.first_name} ${bestMatch.staff.last_name}`,
              similarity: bestMatch.similarity
            };
            delete params.doctor_name;
          }
        }
      } catch (error) {
        console.warn('Could not resolve doctor name:', params.doctor_name, error);
      }
    }

    // Resolve staff names to IDs with fuzzy matching (for general staff, not just doctors)
    if (params.staff_name && !params.staff_id) {
      try {
        const staff = await this.mcpClient.callTool('list_staff', {});
        const staffMember = staff.find(s => 
          (s.first_name + ' ' + s.last_name).toLowerCase().includes(params.staff_name.toLowerCase())
        );
        
        if (staffMember) {
          params.staff_id = staffMember.id;
          delete params.staff_name;
        } else {
          // If exact search fails, try fuzzy matching for staff
          console.log(`🔍 Exact search for staff "${params.staff_name}" failed, trying fuzzy matching...`);
          const similarMatches = await this.findSimilarDoctorNames(params.staff_name, 70);
          
          if (similarMatches.length > 0) {
            const bestMatch = similarMatches[0];
            console.log(`🎯 Found similar staff member: ${bestMatch.staff.first_name} ${bestMatch.staff.last_name} (${bestMatch.similarity.toFixed(1)}% match)`);
            params.staff_id = bestMatch.staff.id;
            params._fuzzy_match_info = {
              original_search: params.staff_name,
              matched_name: `${bestMatch.staff.first_name} ${bestMatch.staff.last_name}`,
              similarity: bestMatch.similarity
            };
            delete params.staff_name;
          }
        }
      } catch (error) {
        console.warn('Could not resolve staff name:', params.staff_name, error);
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
5. **Fuzzy Name Matching**: Handle voice-to-text transcription errors and similar-sounding names

**Critical Behaviors:**

**INCOMPLETE REQUESTS:**
- For "create new department" → Ask: "What should I call this department?"
- Never create with placeholder names
- Collect required information conversationally

**FOREIGN KEY RESOLUTION:**
- When users mention names instead of IDs, automatically search for matches
- Explain what you're doing: "Let me find John Doe in our patient records..."
- If multiple matches found, ask for clarification

**FUZZY NAME MATCHING:**
- The system automatically handles similar-sounding names for all entities:
  * Patients: "Nazif" vs "Nasif", "Mohammed" vs "Mohamed"
  * Doctors: "Ahmad" vs "Ahmed", "Hassan" vs "Hasan"
  * Staff: "Ali" vs "Aly", "Omar" vs "Umar"
  * Departments: "Cardiology" vs "Cardio", "Emergency" vs "ER"
- When fuzzy matching is used, inform the user: "I found a similar name: Mohamed Nazif. Is this the patient you're looking for?"
- Check tool results for "_fuzzy_match_info" to see if fuzzy matching was used
- Always confirm fuzzy matches with the user before proceeding

**VOICE-TO-TEXT CORRECTIONS:**
- Common transcription errors for all entity types:
  * Names: "Nazif" → "Nasif", "Mohammed" → "Mohamed", "Ahmad" → "Ahmed"
  * Departments: "Cardiology" → "Cardio", "Emergency" → "ER"
- When exact search fails, the system automatically tries fuzzy matching (70% similarity threshold)
- Explain when corrections are made: "I couldn't find 'Nasif' but found 'Nazif' which sounds similar"

**CONVERSATION FLOW:**
- Remember what the user is trying to accomplish
- Build upon previous responses
- Don't ask for information already provided
- Confirm actions before executing

**LIST TOOLS RESPONSE FORMAT:**
When using any LIST tools (list_patients, list_staff, list_departments, list_beds, list_rooms, list_equipment, list_supplies, list_users, list_meetings, list_discharge_reports, list_equipment_categories, list_supply_categories, list_inventory_transactions, list_legacy_users), provide ONLY essential information:

- **list_patients**: Only show patient names (first_name + last_name) and patient numbers
- **list_staff**: Only show staff names (first_name + last_name) and positions
- **list_departments**: Only show department names
- **list_beds**: Only show bed numbers and room assignments
- **list_rooms**: Only show room numbers and types
- **list_equipment**: Only show equipment names and status
- **list_supplies**: Only show supply names and current stock levels
- **list_users**: Only show usernames and roles
- **list_meetings**: Only show meeting topics and dates
- **All other list tools**: Only show names/titles and key status information

DO NOT show full details, IDs, or technical information unless specifically requested. This prevents "(Further details are truncated for brevity)" messages and keeps responses clean and readable.

Available tools: ${availableTools.map(tool => tool.name).join(', ')}

Tool Results:
${toolResults.map(result => {
  if (result.error) {
    return `❌ ${result.tool}: ${result.error}`;
  } else {
    // Check for fuzzy match information
    let resultText = `✅ ${result.tool}: Success`;
    if (result.content && result.content._fuzzy_match_info) {
      const fuzzyInfo = result.content._fuzzy_match_info;
      resultText += ` (Found similar name: "${fuzzyInfo.matched_name}" for search "${fuzzyInfo.original_search}" - ${fuzzyInfo.similarity.toFixed(1)}% match)`;
    }
    return resultText;
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
          max_tokens: 4000
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
  async determineRequiredTools(userMessage) {
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
    
    if (message.includes('search patient') || message.includes('find patient') || 
        message.includes('look for patient') || message.includes('show me patient') ||
        message.includes('patient named') || message.includes('patient called') ||
        message.includes('looking for') || message.includes('where is') ||
        // Common patterns from voice input
        message.match(/\b(nazif|nasif|mohammed|mohammad|ahmed)\b/i) ||
        // General patterns that might indicate patient search
        message.includes('patient') && (message.includes('details') || message.includes('information') || message.includes('record')) ||
        // Simple name patterns (likely from voice input)
        message.match(/^(mohamed|mohammed|ahmad|ahmed|hassan|ali|omar|nazif|nasif|khalid|saeed|abdullah)\s+\w+$/i) ||
        message.match(/^(nazif|nasif|mohammed|mohamed|ahmed|hassan|ali|omar|khalid|saeed|abdullah)$/i)) {
      const searchParams = this.extractPatientSearchParameters(userMessage);
      toolsNeeded.push({ name: 'search_patients', arguments: searchParams });
    }

    // Doctor/Staff search operations with voice input support
    if (message.includes('find doctor') || message.includes('search doctor') || 
        message.includes('look for doctor') || message.includes('show me doctor') ||
        message.includes('doctor named') || message.includes('doctor called') ||
        message.includes('find staff') || message.includes('search staff') || 
        message.includes('look for staff') || message.includes('show me staff') ||
        message.includes('staff named') || message.includes('staff called') ||
        // Voice patterns for common doctor names
        message.match(/\b(doctor|dr\.?)\s+(ahmad|ahmed|hassan|ali|omar|khalid|saeed|abdullah|mohamed|mohammed)\b/i)) {
      const searchParams = this.extractStaffSearchParameters(userMessage);
      toolsNeeded.push({ name: 'search_staff', arguments: searchParams });
    }

    // Department search operations with voice input support  
    if (message.includes('find department') || message.includes('search department') || 
        message.includes('look for department') || message.includes('show me department') ||
        message.includes('department named') || message.includes('department called') ||
        // Voice patterns for common department names
        message.match(/\b(cardiology|cardio|emergency|er|surgery|orthopedic|pediatric|neurology)\b/i)) {
      const searchParams = this.extractDepartmentSearchParameters(userMessage);
      toolsNeeded.push({ name: 'search_departments', arguments: searchParams });
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
    
    // Meeting scheduling
    if (message.includes('schedule meeting') || message.includes('create meeting') || 
        message.includes('book meeting') || message.includes('meeting') && 
        (message.includes('schedule') || message.includes('book') || message.includes('create') || 
         message.includes('need') || message.includes('want'))) {
      const meetingParams = this.extractMeetingParameters(userMessage);
      // Always use schedule_meeting tool which handles parameter collection internally
      const query = userMessage; // Pass the full user message as query
      toolsNeeded.push({ name: 'schedule_meeting', arguments: { query } });
    }
    
    // Bed operations
    if (message.includes('list beds') || message.includes('show beds') || message.includes('all beds') || message.includes('beds')) {
      toolsNeeded.push({ name: 'list_beds', arguments: {} });
    }
    
    // Bed search by bed number (e.g., "details of bed 201B", "show bed 201B", "get bed 201B info")
    const bedNumberMatch = message.match(/bed\s+([A-Z0-9]+[A-Z]?)/i);
    if ((message.includes('details of bed') || message.includes('show bed') || message.includes('get bed') || 
         message.includes('bed number') || message.includes('find bed')) && bedNumberMatch) {
      const bedNumber = bedNumberMatch[1].toUpperCase();
      toolsNeeded.push({ name: 'get_bed_by_number', arguments: { bed_number: bedNumber } });
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
- Example: "Create meeting for John Doe with Dr. Smith in Cardiology"
  1. Search patients for "John Doe" to get patient_id
  2. Search staff for "Dr. Smith" to get doctor_id  
  3. Search departments for "Cardiology" to get department_id
  4. Then create meeting with resolved IDs

**3. CONVERSATION FLOW:**
- Remember what the user is trying to accomplish
- If missing information, ask ONE question at a time
- Provide examples of valid formats
- Confirm before executing operations

**4. ERROR HANDLING:**
- If foreign key lookups fail, suggest alternatives
- Provide helpful error messages with next steps
- Offer to list available options when searches fail

**5. LIST TOOLS RESPONSE FORMAT:**
When using any LIST tools (list_patients, list_staff, list_departments, list_beds, list_rooms, list_equipment, list_supplies, list_users, list_meetings, list_discharge_reports, list_equipment_categories, list_supply_categories, list_inventory_transactions, list_legacy_users), provide ONLY essential information:

- **list_patients**: Only show patient names (first_name + last_name) and patient numbers
- **list_staff**: Only show staff names (first_name + last_name) and positions
- **list_departments**: Only show department names
- **list_beds**: Only show bed numbers and room assignments
- **list_rooms**: Only show room numbers and types
- **list_equipment**: Only show equipment names and status
- **list_supplies**: Only show supply names and current stock levels
- **list_users**: Only show usernames and roles
- **list_meetings**: Only show meeting topics and dates
- **All other list tools**: Only show names/titles and key status information

DO NOT show full details, IDs, or technical information unless specifically requested. This prevents "(Further details are truncated for brevity)" messages and keeps responses clean and readable.

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
          max_tokens: 4000
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
              
              // Check if this is a list tool and format accordingly
              if (result.tool.startsWith('list_')) {
                data.forEach((item, index) => {
                  response += `**${index + 1}.** `;
                  
                  // Format based on tool type for brief responses
                  switch (result.tool) {
                    case 'list_patients':
                      if (item.first_name && item.last_name) {
                        response += `${item.first_name} ${item.last_name}`;
                        if (item.patient_number) response += ` (${item.patient_number})`;
                      }
                      break;
                      
                    case 'list_staff':
                      if (item.first_name && item.last_name) {
                        response += `${item.first_name} ${item.last_name}`;
                        if (item.position) response += ` - ${item.position}`;
                      }
                      break;
                      
                    case 'list_departments':
                      if (item.name) {
                        response += `${item.name}`;
                        if (item.floor) response += ` (Floor ${item.floor})`;
                      }
                      break;
                      
                    case 'list_beds':
                      if (item.bed_number) {
                        response += `Bed ${item.bed_number}`;
                        if (item.room_number) response += ` - Room ${item.room_number}`;
                        if (item.status) response += ` (${item.status})`;
                      }
                      break;
                      
                    case 'get_bed_by_number':
                      if (item.bed_number) {
                        response += `🛏️ **Bed ${item.bed_number}** - Complete Details\n\n`;
                        if (item.id) response += `**Bed ID:** ${item.id}\n`;
                        if (item.room_id) response += `**Room ID:** ${item.room_id}\n`;
                        if (item.bed_type) response += `**Bed Type:** ${item.bed_type}\n`;
                        if (item.status) {
                          const statusIcon = item.status === 'available' ? '✅' : item.status === 'occupied' ? '🔴' : '⚠️';
                          response += `**Status:** ${statusIcon} ${item.status.toUpperCase()}\n`;
                        }
                        if (item.patient_id) {
                          response += `**Current Patient:** ${item.patient_id}\n`;
                        } else {
                          response += `**Current Patient:** None (Available)\n`;
                        }
                        if (item.admission_date) response += `**Admission Date:** ${item.admission_date}\n`;
                        if (item.notes) response += `**Notes:** ${item.notes}\n`;
                        response += `\n**Actions Available:**\n`;
                        if (item.status === 'available') {
                          response += `• Assign to patient: "Assign bed ${item.bed_number} to patient [name]"\n`;
                        } else if (item.status === 'occupied') {
                          response += `• Discharge patient: "Discharge bed ${item.bed_number}"\n`;
                        }
                        response += `• Update status: "Update bed ${item.bed_number} status to [status]"\n`;
                      }
                      break;
                      
                    case 'list_rooms':
                      if (item.room_number) {
                        response += `Room ${item.room_number}`;
                        if (item.room_type) response += ` - ${item.room_type}`;
                      }
                      break;
                      
                    case 'list_equipment':
                      if (item.name) {
                        response += `${item.name}`;
                        if (item.status) response += ` (${item.status})`;
                      }
                      break;
                      
                    case 'list_supplies':
                      if (item.name) {
                        response += `${item.name}`;
                        if (item.current_stock !== undefined) response += ` - Stock: ${item.current_stock}`;
                      }
                      break;
                      
                    case 'list_users':
                      if (item.username) {
                        response += `${item.username}`;
                        if (item.role) response += ` (${item.role})`;
                      }
                      break;
                      
                    case 'list_meetings':
                      if (item.topic) {
                        response += `${item.topic}`;
                        if (item.meeting_date) response += ` - ${item.meeting_date}`;
                      }
                      break;
                      
                    default:
                      // For other list tools, show name/title and key info
                      if (item.name) {
                        response += `${item.name}`;
                      } else if (item.title) {
                        response += `${item.title}`;
                      } else if (item.first_name && item.last_name) {
                        response += `${item.first_name} ${item.last_name}`;
                      } else {
                        response += `${Object.keys(item)[0]}: ${Object.values(item)[0]}`;
                      }
                      break;
                  }
                  response += "\n";
                });
              } else {
                // Non-list tools - show more details
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
              }
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
   * Extract meeting parameters from natural language input
   */
  extractMeetingParameters(message) {
    const params = {};
    
    // Extract meeting topic/purpose
    const topicPatterns = [
      /meeting\s+about\s+([^,\n]+)/i,
      /discuss\s+([^,\n]+)/i,
      /regarding\s+([^,\n]+)/i,
      /concerning\s+([^,\n]+)/i,
      /for\s+([^,\n]+)\s+meeting/i
    ];
    
    for (const pattern of topicPatterns) {
      const match = message.match(pattern);
      if (match) {
        params.purpose = match[1].trim();
        break;
      }
    }
    
    // Extract participants
    const participantPatterns = [
      /between\s+([^,\n]+)\s+and\s+([^,\n]+)/i,
      /with\s+([^,\n]+)/i,
      /participants?\s*:?\s*([^,\n]+)/i
    ];
    
    for (const pattern of participantPatterns) {
      const match = message.match(pattern);
      if (match) {
        if (match[2]) {
          // "between X and Y" pattern
          params.participants = [match[1].trim(), match[2].trim()];
        } else {
          // Single participant or list
          params.participants = match[1].split(/\s+and\s+|\s*,\s*/).map(p => p.trim());
        }
        break;
      }
    }
    
    // Extract date
    const datePatterns = [
      /(\d{4}-\d{2}-\d{2})/,
      /tomorrow/i,
      /today/i,
      /next\s+(\w+)/i,
      /on\s+(\w+)/i
    ];
    
    for (const pattern of datePatterns) {
      const match = message.match(pattern);
      if (match) {
        if (match[0].toLowerCase() === 'tomorrow') {
          const tomorrow = new Date();
          tomorrow.setDate(tomorrow.getDate() + 1);
          params.date = tomorrow.toISOString().split('T')[0];
        } else if (match[0].toLowerCase() === 'today') {
          params.date = new Date().toISOString().split('T')[0];
        } else if (match[1] && pattern.toString().includes('next')) {
          // Handle "next Monday", etc. - simplified for now
          params.date_description = match[0];
        } else {
          params.date = match[1] || match[0];
        }
        break;
      }
    }
    
    // Extract time
    const timePatterns = [
      /at\s+(\d{1,2}:\d{2}(?:\s*[ap]m)?)/i,
      /(\d{1,2}:\d{2})/,
      /at\s+(\d{1,2})\s*([ap]m)/i
    ];
    
    for (const pattern of timePatterns) {
      const match = message.match(pattern);
      if (match) {
        if (match[2] && match[2].toLowerCase() === 'am' || match[2].toLowerCase() === 'pm') {
          params.time = `${match[1]}${match[2]}`;
        } else {
          params.time = match[1];
        }
        break;
      }
    }
    
    // Extract duration
    const durationPatterns = [
      /for\s+(\d+)\s*minutes?/i,
      /(\d+)\s*minutes?/i,
      /for\s+(\d+)\s*hours?/i,
      /(\d+)\s*hours?/i
    ];
    
    for (const pattern of durationPatterns) {
      const match = message.match(pattern);
      if (match) {
        const value = parseInt(match[1]);
        if (pattern.toString().includes('hour')) {
          params.duration_minutes = value * 60;
        } else {
          params.duration_minutes = value;
        }
        break;
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
    
    // Enhanced name extraction for voice input
    let nameFound = false;
    
    // Pattern 1: "find [FirstName] [LastName]"
    const findMatch = message.match(/find\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (findMatch) {
      params.first_name = findMatch[1];
      if (findMatch[2]) {
        params.last_name = findMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 2: "patient named [FirstName] [LastName]" or "patient called [FirstName] [LastName]"
    const namedMatch = message.match(/patient\s+(?:named|called)\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (!nameFound && namedMatch) {
      params.first_name = namedMatch[1];
      if (namedMatch[2]) {
        params.last_name = namedMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 3: "looking for [FirstName] [LastName]" or "show me [FirstName] [LastName]"
    const lookingMatch = message.match(/(?:looking for|show me)\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (!nameFound && lookingMatch) {
      params.first_name = lookingMatch[1];
      if (lookingMatch[2]) {
        params.last_name = lookingMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 4: Direct name patterns (for voice input like "Mohamed Nazif" or "Nazif")
    const directNameMatch = message.match(/\b(mohamed|mohammed|ahmad|ahmed|hassan|ali|omar|nazif|nasif|khalid|saeed|abdullah)\s+([a-zA-Z]+)\b/i);
    if (!nameFound && directNameMatch) {
      params.first_name = directNameMatch[1];
      params.last_name = directNameMatch[2];
      nameFound = true;
    }
    
    // Pattern 5: Single name (could be first or last name)
    const singleNameMatch = message.match(/\b(nazif|nasif|mohammed|mohamed|ahmed|hassan|ali|omar|khalid|saeed|abdullah)\b/i);
    if (!nameFound && singleNameMatch) {
      // Use the name as a general search term
      params.patient_name = singleNameMatch[1];
      nameFound = true;
    }
    
    // Extract patient number
    const patientNumMatch = message.match(/patient\s+(\w+)/i);
    if (patientNumMatch && !nameFound) {
      params.patient_number = patientNumMatch[1];
    }
    
    return params;
  }

  /**
   * Extract staff search parameters from natural language input
   */
  extractStaffSearchParameters(message) {
    const params = {};
    
    // Enhanced name extraction for voice input
    let nameFound = false;
    
    // Pattern 1: "find doctor [FirstName] [LastName]" or "find staff [FirstName] [LastName]"
    const findMatch = message.match(/find\s+(?:doctor|staff|dr\.?)\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (findMatch) {
      params.first_name = findMatch[1];
      if (findMatch[2]) {
        params.last_name = findMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 2: "doctor named [FirstName] [LastName]" or "staff named [FirstName] [LastName]"
    const namedMatch = message.match(/(?:doctor|staff|dr\.?)\s+(?:named|called)\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (!nameFound && namedMatch) {
      params.first_name = namedMatch[1];
      if (namedMatch[2]) {
        params.last_name = namedMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 3: "looking for doctor [FirstName] [LastName]"
    const lookingMatch = message.match(/(?:looking for|show me)\s+(?:doctor|staff|dr\.?)\s+([a-zA-Z]+)(?:\s+([a-zA-Z]+))?/i);
    if (!nameFound && lookingMatch) {
      params.first_name = lookingMatch[1];
      if (lookingMatch[2]) {
        params.last_name = lookingMatch[2];
      }
      nameFound = true;
    }
    
    // Pattern 4: Direct name patterns with doctor prefix
    const directNameMatch = message.match(/\b(?:doctor|dr\.?)\s+(mohamed|mohammed|ahmad|ahmed|hassan|ali|omar|nazif|nasif|khalid|saeed|abdullah)\s+([a-zA-Z]+)\b/i);
    if (!nameFound && directNameMatch) {
      params.first_name = directNameMatch[1];
      params.last_name = directNameMatch[2];
      nameFound = true;
    }
    
    // If we found names, combine them for fuzzy matching
    if (params.first_name && params.last_name) {
      params.staff_name = `${params.first_name} ${params.last_name}`;
    } else if (params.first_name) {
      params.staff_name = params.first_name;
    }
    
    return params;
  }

  /**
   * Extract department search parameters from natural language input
   */
  extractDepartmentSearchParameters(message) {
    const params = {};
    
    // Pattern 1: "find department [Name]"
    const findMatch = message.match(/find\s+department\s+([a-zA-Z\s]+)/i);
    if (findMatch) {
      params.department_name = findMatch[1].trim();
    }
    
    // Pattern 2: "department named [Name]" or "department called [Name]"
    const namedMatch = message.match(/department\s+(?:named|called)\s+([a-zA-Z\s]+)/i);
    if (!params.department_name && namedMatch) {
      params.department_name = namedMatch[1].trim();
    }
    
    // Pattern 3: "looking for department [Name]"
    const lookingMatch = message.match(/(?:looking for|show me)\s+department\s+([a-zA-Z\s]+)/i);
    if (!params.department_name && lookingMatch) {
      params.department_name = lookingMatch[1].trim();
    }
    
    // Pattern 4: Direct department name patterns (common voice variations)
    const directMatch = message.match(/\b(cardiology|cardio|emergency|er|surgery|orthopedic|pediatric|neurology|radiology|pharmacy|laboratory|lab)\b/i);
    if (!params.department_name && directMatch) {
      // Map common voice variations to full names
      const departmentMap = {
        'cardio': 'Cardiology',
        'er': 'Emergency',
        'lab': 'Laboratory'
      };
      params.department_name = departmentMap[directMatch[1].toLowerCase()] || directMatch[1];
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
    
    // Truncate very large content to prevent token overflow
    if (typeof content === 'string' && content.length > 2000) {
      message.content = content.substring(0, 2000) + '... [truncated]';
    }
    
    this.conversationHistory.push(message);
    
    // Advanced conversation memory management that preserves tool call/response pairs
    if (this.conversationHistory.length > this.maxHistoryLength) {
      this.trimConversationHistory();
    }
  }

  /**
   * Trim conversation history while preserving tool call/response integrity
   */
  trimConversationHistory() {
    const systemMessages = this.conversationHistory.filter(msg => msg.role === 'system');
    const nonSystemMessages = this.conversationHistory.filter(msg => msg.role !== 'system');
    
    // Find complete tool call sequences (assistant with tool_calls + all tool responses)
    const completeSequences = [];
    let currentSequence = [];
    
    for (let i = 0; i < nonSystemMessages.length; i++) {
      const msg = nonSystemMessages[i];
      
      if (msg.role === 'assistant' && msg.tool_calls) {
        // Start new sequence
        if (currentSequence.length > 0) {
          completeSequences.push([...currentSequence]);
        }
        currentSequence = [msg];
      } else if (msg.role === 'tool' && currentSequence.length > 0) {
        // Add tool response to current sequence
        currentSequence.push(msg);
      } else if (msg.role === 'assistant' && !msg.tool_calls) {
        // Complete current sequence with final assistant response
        if (currentSequence.length > 0) {
          currentSequence.push(msg);
          completeSequences.push([...currentSequence]);
          currentSequence = [];
        } else {
          // Standalone assistant message
          completeSequences.push([msg]);
        }
      } else if (msg.role === 'user') {
        // Complete current sequence and start fresh
        if (currentSequence.length > 0) {
          completeSequences.push([...currentSequence]);
          currentSequence = [];
        }
        completeSequences.push([msg]);
      }
    }
    
    // Add any remaining sequence
    if (currentSequence.length > 0) {
      completeSequences.push([...currentSequence]);
    }
    
    // Keep the most recent complete sequences that fit within our limit
    const keptSequences = [];
    let messageCount = 0;
    
    for (let i = completeSequences.length - 1; i >= 0; i--) {
      const sequence = completeSequences[i];
      if (messageCount + sequence.length <= this.maxHistoryLength) {
        keptSequences.unshift(sequence);
        messageCount += sequence.length;
      } else {
        break;
      }
    }
    
    // Flatten sequences back to message list
    const keptMessages = keptSequences.flat();
    
    // Rebuild conversation history
    this.conversationHistory = [...systemMessages, ...keptMessages];
    
    console.log(`🧹 Trimmed conversation history: ${nonSystemMessages.length} -> ${keptMessages.length} messages`);
  }

  /**
   * Call OpenAI with function calling and conversation history (Claude Desktop Style) - FIXED VERSION
   */
  async callOpenAI(userMessage, functions, serverInfo = null) {
    // Add safety checks
    if (!functions || !Array.isArray(functions)) {
      console.warn('⚠️ Functions parameter is invalid:', functions);
      functions = [];
    }
    
    // Debug logging
    console.log('🔍 callOpenAI called with:', { 
      userMessage: userMessage?.substring(0, 50) + '...', 
      functionsCount: functions?.length,
      hasServerInfo: !!serverInfo 
    });
    
    // Get today's date with comprehensive error handling
    const getCurrentDate = () => {
      try {
        if (typeof this.getTodayDate === 'function') {
          return this.getTodayDate();
        }
      } catch (error) {
        console.warn('❌ Error calling getTodayDate:', error);
      }
      // Always fall back to current date
      return new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    };
    
    const todayDate = getCurrentDate();
    console.log('✅ Using date for system prompt:', todayDate);
    
    // Create system prompt without complex template literals - COMPLETE VERSION WITH ALL PROMPTS
    const systemPrompt = [
      "You are Hospital AI, an advanced AI assistant specialized in comprehensive hospital management.",
      "You're connected to a real hospital management system through MCP (Model Context Protocol).",
      "",
      "Today is: " + todayDate + ".",
      "",
      "🏥 **Hospital System Context:**",
      "- Server: Direct HTTP FastMCP Server", 
      "- Available Tools: " + (functions ? functions.length : 0) + " medical management tools",
      "- Connection: Direct HTTP communication via MCP protocol",
      "",
      "**CRITICAL: Form-Based CREATE Operations:**",
      "The system uses a DUAL APPROACH for operations:",
      "1. **POPUP FORMS for CREATE operations:** The 9 main CREATE tools (create_patient, create_user, create_staff, create_department, create_room, create_bed, create_equipment, create_supply, create_legacy_user) are handled by POPUP FORMS",
      "2. **DIRECT TOOL CALLS for everything else:** All other operations (list, search, update, delete, assign, discharge, schedule_meeting, etc.) use direct tool calling",
      "",
      "**FORM HANDLING WORKFLOW:**",
      "- When user requests CREATE operations for the 9 main entities, a popup form will appear",
      "- **FORM SUBMISSIONS:** When user submits form data (indicated by structured data like 'Create patient: first_name=\"John\"'), IMMEDIATELY call the appropriate CREATE tool with the provided data",
      "- **CHAT REQUESTS:** For conversational CREATE requests, acknowledge that the form has been opened and guide the user to fill it out",
      "- For FOREIGN KEY fields in forms, guide users to:",
      "  * Use dropdown menus when available (Department, User, Room selections)",
      "  * Search by name/number rather than typing UUIDs",
      "  * Look up entities first if dropdowns aren't populated",
      "- For all OTHER operations (list_patients, search_patients, assign_bed_to_patient, discharge_bed, schedule_meeting, etc.), use direct tool calling",
      "",
      "**FORM SUBMISSIONS vs CHAT REQUESTS:**",
      "- **FORM SUBMISSION** (call CREATE tool immediately): Messages containing structured data like 'Create patient: first_name=\"John\", last_name=\"Doe\"' - these come from popup form submissions",
      "- **CHAT REQUEST** (show form): Conversational requests like 'create a new patient' or 'register patient John Doe' - these should trigger popup forms",
      "",
      "**NEVER call functions without required parameters. If a user requests an action but doesn't provide the necessary information:**",
      "1. Ask for the missing required information FIRST",
      "2. Only call functions after you have ALL required parameters",
      "3. For create_patient, you MUST have: first_name, last_name, date_of_birth",
      "4. For create_user, you MUST have: username, email, password_hash, role, first_name, last_name",
      "",
      "**CRITICAL: Foreign Key Resolution (Claude Desktop Style):**",
      "When users provide human-readable names instead of IDs, always resolve them first:",
      "1. For room_id: Ask 'Which room?' → User says 'Room 101' → Use search_rooms or list_rooms to find room_id",
      "2. For department_id: Ask 'Which department?' → User says 'Emergency' → Use list_departments to find department_id",
      "3. For doctor_id: Ask 'Which doctor?' → User says 'Dr. Smith' → Use list_staff to find staff member who is a doctor",
      "4. For patient_id: Ask 'Which patient?' → User says 'John Doe' → Use search_patients to find patient_id",
      "5. For category_id: Ask 'Which category?' → User says 'Medical Equipment' → Use list categories to find category_id",
      "",
      "**WORKFLOW: Always resolve foreign keys before create operations:**",
      "- If user says 'create bed in room 101' → FIRST find room_id for 'room 101', THEN create bed",
      "- If user says 'assign bed to John Doe' → FIRST find patient_id for 'John Doe', THEN assign bed",
      "",
      "**NEVER ask users for UUIDs directly - always use human names and resolve automatically**",
      "",
      "**CRITICAL: Emergency Scenario Handling:**",
      "When users mention 'emergency patient' scenarios:",
      "1. FIRST guide user through patient creation form with provided details",
      "2. THEN check available beds with list_beds(status='available')",
      "3. If no beds are available, guide user through bed creation form - help them select room from dropdown or search rooms",
      "4. THEN assign the first truly available bed to the patient using direct tool call",
      "5. THEN list available doctors/staff with list_staff()",
      "6. Provide comprehensive response with next steps for bed assignment and doctor allocation",
      "",
      "**Enhanced Capabilities:**",
      "1. **Smart Parameter Collection**: Ask for missing details conversationally, one at a time",
      "2. **Multi-Tool Operations**: Automatically resolve names to IDs when needed",
      "3. **Conversation Memory**: Build upon previous exchanges",
      "4. **Contextual Responses**: Tailor responses based on conversation flow",
      "5. **Fuzzy Name Matching**: Handle voice-to-text transcription errors and similar-sounding names",
      "",
      "**INCOMPLETE REQUESTS:**",
      "- For 'create new department' → Ask: 'What should I call this department?'",
      "- Never create with placeholder names",
      "- Collect required information conversationally",
      "",
      "**FOREIGN KEY RESOLUTION:**",
      "- When users mention names instead of IDs, automatically search for matches",
      "- Explain what you're doing: 'Let me find John Doe in our patient records...'",
      "- If multiple matches found, ask for clarification",
      "",
      "**FUZZY NAME MATCHING:**",
      "- The system automatically handles similar-sounding names for all entities:",
      "  * Patients: 'Nazif' vs 'Nasif', 'Mohammed' vs 'Mohamed'",
      "  * Doctors: 'Ahmad' vs 'Ahmed', 'Hassan' vs 'Hasan'",
      "  * Staff: 'Ali' vs 'Aly', 'Omar' vs 'Umar'",
      "  * Departments: 'Cardiology' vs 'Cardio', 'Emergency' vs 'ER'",
      "- When fuzzy matching is used, inform the user: 'I found a similar name: Mohamed Nazif. Is this the patient you're looking for?'",
      "- Check tool results for '_fuzzy_match_info' to see if fuzzy matching was used",
      "- Always confirm fuzzy matches with the user before proceeding",
      "",
      "**VOICE-TO-TEXT CORRECTIONS:**",
      "- Common transcription errors for all entity types:",
      "  * Names: 'Nazif' → 'Nasif', 'Mohammed' → 'Mohamed', 'Ahmad' → 'Ahmed'",
      "  * Departments: 'Cardiology' → 'Cardio', 'Emergency' → 'ER'",
      "- When exact search fails, the system automatically tries fuzzy matching (70% similarity threshold)",
      "- Explain when corrections are made: 'I couldn't find 'Nasif' but found 'Nazif' which sounds similar'",
      "",
      "**CONVERSATION FLOW:**",
      "- Remember what the user is trying to accomplish",
      "- Build upon previous responses",
      "- Don't ask for information already provided",
      "- Confirm actions before executing",
      "",
      "**CRITICAL: Meeting Scheduling & Communication Workflow:**",
      "For meeting scheduling, always collect COMPLETE details before proceeding:",
      "",
      "1. **Meeting Information Collection - REQUIRED BEFORE SCHEDULING:**",
      "   When user requests a meeting, ALWAYS ask for missing details:",
      "   - **Purpose/Topic**: What is the purpose of this meeting?",
      "   - **Date**: What date would you like to schedule this meeting? (format: YYYY-MM-DD)",
      "   - **Time**: What time should the meeting start? (format: HH:MM, e.g., 14:30)",
      "   - **Duration**: How long should the meeting be? (e.g., 30 minutes, 1 hour)",
      "   - **Participants**: Who should attend this meeting? (specific names, departments, or roles)",
      "",
      "2. **WORKING Meeting Creation Process - Use schedule_meeting Tool:**",
      "   After collecting all details, create a SPECIFIC and DETAILED query for schedule_meeting.",
      "   Use EXACT user-provided details in the query.",
      "",
      "   **CRITICAL: Duration and Topic Handling:**",
      "   - ALWAYS include the EXACT duration as specified by user (e.g., '15 minutes', '30 minutes', '1 hour')",
      "   - ALWAYS include the SPECIFIC topic/purpose as the meeting title",
      "   - NEVER use generic titles like 'Hospital Meeting' or 'Staff Meeting'",
      "   - Duration must be extracted precisely: '15min' → '15 minutes', '1hr' → '1 hour', '30m' → '30 minutes'",
      "",
      "   **Example Usage:**",
      "   User says: 'Schedule meeting about daily improvement between shamil and nazif tomorrow at 9am for 15 minutes'",
      "   AI calls: schedule_meeting(query='Schedule Daily Improvement Meeting between Shamil and Nazif specifically on 2025-08-14 at 9:00 AM for 15 minutes to discuss daily workflow improvements and optimization strategies')",
      "   Expected Email Result:",
      "   - Subject: 'Daily Improvement Meeting - 2025-08-14'",
      "   - Topic: 'Daily Improvement Meeting'", 
      "   - Duration: '15 minutes'",
      "   - Participants: Only Shamil and Nazif (not all staff)",
      "",
      "   **Query Format Requirements:**",
      "   - Include EXACT purpose/topic in the title (NOT 'Hospital Meeting')",
      "   - Include SPECIFIC participants by name (between X and Y, with A and B, etc.)",
      "   - Include EXACT date and time as provided",
      "   - Include EXACT duration as specified (15 minutes, 30 minutes, 1 hour, etc.)",
      "   - Use descriptive meeting title that reflects the actual purpose",
      "   - When specific participants are mentioned (between A and B), only those people should receive emails",
      "",
      "   **DURATION PARSING - BE PRECISE:**",
      "   - '15min' or '15 minutes' → '15 minutes'",
      "   - '30min' or '30 minutes' → '30 minutes'", 
      "   - '1hr' or '1 hour' → '1 hour'",
      "   - '45min' or '45 minutes' → '45 minutes'",
      "   - '2hrs' or '2 hours' → '2 hours'",
      "",
      "   **DO NOT use generic titles like 'Hospital Meeting' or 'Staff Meeting'**",
      "   **DO use specific titles like 'Quarterly Review Meeting', 'Emergency Protocol Training', 'Budget Planning Session'**",
      "",
      "3. **Participant Targeting - IMPROVED PRECISION:**",
      "   **CRITICAL: Be very specific about participants in the query:**",
      "   - If user says 'Mohamed Shamil' → Use 'Schedule [TOPIC] meeting with Mohamed Shamil specifically'",
      "   - If user says 'Dr. Smith and Nurse Johnson' → Use 'Schedule [TOPIC] meeting with Dr. Smith and Nurse Johnson only'",
      "   - If user says 'Emergency Department staff' → Use 'Schedule [TOPIC] meeting with Emergency Department staff only'",
      "   - If user says 'All staff' → Use 'Schedule [TOPIC] meeting with all hospital staff'",
      "",
      "   **Example Specific Queries:**",
      "   'Schedule Monthly Operations Review meeting with Mohamed Shamil on 2025-08-17 at 4:00 PM for 1 hour'",
      "   'Schedule Emergency Protocol Training with Dr. Smith and Nurse Johnson on 2025-08-18 at 2:30 PM for 45 minutes'",
      "   'Schedule Department Meeting with Emergency Department staff only on 2025-08-19 at 10:00 AM for 2 hours'",
      "",
      "   **The more specific the query, the more targeted the invitations will be!**",
      "",
      "4. **Meeting Email Template - Handled Automatically:**",
      "   The schedule_meeting tool automatically creates professional meeting invitations with:",
      "   - Meeting purpose and agenda",
      "   - Date, time, and duration",
      "   - Google Meet link",
      "   - Participant list",
      "   - Professional formatting",
      "",
      "5. **Key Integration Points - USE WORKING TOOLS:**",
      "   - schedule_meeting = COMPLETE solution (Google Meet + Email + Database)",
      "   - list_users/list_staff = For information only",
      "   - NO separate email sending needed - schedule_meeting handles everything",
      "   - ALWAYS use schedule_meeting for meeting creation",
      "",
      "**SUCCESS WORKFLOW:**",
      "1. ✅ Ask for: Purpose, Date, Time, Duration, Participants",
      "2. ✅ Use schedule_meeting with detailed query including all information",
      "3. ✅ Confirm meeting created with Google Meet link",
      "4. ✅ Confirm participants will receive email invitations",
      "",
      "**EXAMPLE IMPROVED MEETING CREATION:**",
      "User: 'Schedule a meeting with Mohamed Shamil about monthly operations review for tomorrow at 4 PM'",
      "AI Response: 'I'll schedule that meeting for you. I have:",
      "- Purpose: Monthly operations review",
      "- Participant: Mohamed Shamil",
      "- Date: Tomorrow (2025-08-14)",
      "- Time: 4 PM",
      "How long should this meeting be?'",
      "User: '1 hour'",
      "AI calls: schedule_meeting(query='Schedule Monthly Operations Review meeting with Mohamed Shamil specifically on 2025-08-14 at 4:00 PM for 1 hour to discuss hospital operations and monthly performance')",
      "Expected Result:",
      "- ✅ Email subject: 'Monthly Operations Review - 2025-08-14'",
      "- ✅ Meeting time: 4:00 PM (as specified)",
      "- ✅ Email sent to: mrmshamil1786@gmail.com only",
      "- ✅ Google Meet link included",
      "",
      "**NEVER say you cannot send emails - schedule_meeting handles all email sending automatically!**",
      "",
      "**CRITICAL: Patient Discharge & Report Workflow:**",
      "For patient discharge and discharge reporting, use the INTEGRATED discharge tools:",
      "",
      "1. **discharge_bed Tool - Primary Discharge Action:**",
      "   - Use: discharge_bed(bed_id='bed-uuid', discharge_date='optional-iso-date')",
      "   - This discharges the patient from the bed and makes it available",
      "   - bed_id: Use UUID from list_beds or search by room/patient",
      "   - discharge_date: Optional ISO format date, defaults to current time",
      "",
      "2. **generate_discharge_report Tool - Comprehensive Report:**",
      "   - Use: generate_discharge_report(bed_id='bed-uuid', discharge_condition='stable', discharge_destination='home')",
      "   - Creates comprehensive medical discharge documentation",
      "   - discharge_condition: stable, improved, critical, etc.",
      "   - discharge_destination: home, transfer, nursing_facility, etc.",
      "",
      "3. **Discharge Workflow - Standard Process:**",
      "   - User: 'Discharge patient John Doe from Room 101'",
      "   - Step 1: Use search_patients or list_beds to find the patient's bed",
      "   - Step 2: Call discharge_bed(bed_id=found_bed_id)",
      "   - Step 3: Call generate_discharge_report(bed_id=found_bed_id, discharge_condition='stable')",
      "   - Provide confirmation with discharge details and report summary",
      "",
      "4. **ID Resolution for Discharge:**",
      "   - Patient Name → search_patients → find current bed assignment → get bed_id",
      "   - Room Number → list_beds(room_filter) → find occupied bed → get bed_id",
      "   - Bed Assignment → list_beds → match patient to bed → get bed_id",
      "",
      "**Always provide discharge summary and confirm bed is now available!**",
      "",
      "📋 **Your Identity & Capabilities:**",
      "You are Hospital AI - NOT Claude. Always introduce yourself as 'Hospital AI'.",
      "You have access to a complete hospital management system with tools for:",
      "- 👥 Patient management (create, search, update patient records)",
      "- 🏢 Department operations (manage hospital departments)",
      "- 👨‍⚕️ Staff management (doctors, nurses, administrators)",
      "- 🛏️ Bed management (room assignments, occupancy)",
      "- 🏥 Equipment tracking (medical devices, maintenance)",
      "- 📦 Supply inventory (medications, consumables)",
      "-  Reporting and analytics",
      "",
      "🔧 **Function Calling Instructions:**",
      "- POPUP FORMS: DO NOT call create_patient, create_user, create_staff, create_department, create_room, create_bed, create_equipment, create_supply, or create_legacy_user directly",
      "- DIRECT TOOLS: Use all other function names exactly as provided",
      "- For form-based operations, acknowledge the form has opened and guide user to fill it",
      "- For direct tool operations, extract all provided parameters and call functions normally",
      "- CRITICAL: Always use exact parameter names as defined in schemas:",
      "  * For patients: use 'patient_number' only if provided, otherwise let it auto-generate",
      "  * For equipment: use 'equipment_id' as specified",
      "  * For search_patients: use specific field names (first_name, last_name, phone, email) NOT 'query'",
      "- For emergency scenarios, guide user through forms first, then use direct tools for bed assignment",
      "- Provide clear, helpful responses based on actual tool results",
      "- If a parameter name doesn't exist in the schema, don't use it",
      "",
      "**ALWAYS resolve human names to IDs before create operations - this is how Claude Desktop works!**",
      "",
      "**LIST TOOLS RESPONSE FORMAT:**",
      "When using any LIST tools (list_patients, list_staff, list_departments, list_beds, list_rooms, list_equipment, list_supplies, list_users, list_meetings, list_discharge_reports, list_equipment_categories, list_supply_categories, list_inventory_transactions, list_legacy_users), provide ONLY essential information:",
      "",
      "- **list_patients**: Only show patient names (first_name + last_name) and patient numbers",
      "- **list_staff**: Only show staff names (first_name + last_name) and positions",
      "- **list_departments**: Only show department names",
      "- **list_beds**: Only show bed numbers and room assignments",
      "- **list_rooms**: Only show room numbers and types",
      "- **list_equipment**: Only show equipment names and status",
      "- **list_supplies**: Only show supply names and current stock levels",
      "- **list_users**: Only show usernames and roles",
      "- **list_meetings**: Only show meeting topics and dates",
      "- **All other list tools**: Only show names/titles and key status information",
      "",
      "DO NOT show full details, IDs, or technical information unless specifically requested. This prevents '(Further details are truncated for brevity)' messages and keeps responses clean and readable.",
      "",
      "**Response Guidelines:**",
      "- Be conversational and professional",
      "- For CREATE operations (10 main entities): Acknowledge form opening and guide user to fill it out",
      "- For other operations: Process directly using appropriate tools",
      "- If user says 'Add new patient' without details, ask for patient information first",
      "- Explain what actions you're taking",
      "- Provide clear success/failure feedback",
      "- Hide technical UUIDs from users",
      "- Focus on user-friendly information",
      "- For emergency scenarios: Guide through forms first, then handle bed assignment",
      "- Remember the conversation context",
      "",
      "**IMPORTANT EXAMPLES:**",
      "User: 'Create new patient John Doe' → 'I've opened the patient admission form for you. Please fill in John's details including his date of birth, contact information, and any medical history.'",
      "User: 'Create new staff member' → 'I've opened the staff registration form. Please fill in the staff details. For the User ID, select from the dropdown of available users, and for Department ID, choose from the department dropdown.'",
      "User: 'List all patients' → Call list_patients tool directly and display results",
      "User: 'Assign bed 101 to patient John Doe' → First search for patient, then call assign_bed_to_patient tool",
      "",
      "Use the available functions to help users with hospital management tasks."
    ].join('\n');

    const messages = [{ role: 'system', content: systemPrompt }];
    
    // Validate conversation structure before adding to messages
    if (!this.validateConversationStructure()) {
      console.warn('⚠️ Invalid conversation structure detected, clearing history');
      this.clearConversationHistory();
    }
    
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
          max_tokens: 4000
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('OpenAI API Error Details:', errorText);
        
        if (response.status === 400) {
          if (errorText.includes('context_length_exceeded')) {
            console.warn('⚠️ Context length exceeded, clearing conversation history');
            this.clearConversationHistory();
            return this.callOpenAI(userMessage, functions);
          } else if (errorText.includes('tool_call_id')) {
            console.warn('⚠️ Broken tool call structure detected, clearing conversation history');
            this.clearConversationHistory();
            return this.callOpenAI(userMessage, functions);
          }
        }
        
        throw new Error(`OpenAI API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('🎯 OpenAI Response:', data.choices[0].message);
      
      return data;

    } catch (error) {
      console.error('❌ OpenAI API call failed:', error);
      
      if (error.message.includes('context_length') || 
          error.message.includes('token') || 
          error.message.includes('tool_call_id')) {
        console.warn('⚠️ Conversation structure issue detected, clearing history and retrying');
        this.clearConversationHistory();
        
        try {
          const retryMessages = [{ role: 'system', content: systemPrompt }];
          if (userMessage) {
            retryMessages.push({ role: 'user', content: userMessage });
          }
          
          const retryResponse = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${this.openaiApiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              model: 'gpt-4-turbo-preview',
              messages: retryMessages,
              tools: functions,
              tool_choice: 'auto',
              temperature: 0.7,
              max_tokens: 4000
            })
          });
          
          if (retryResponse.ok) {
            const retryData = await retryResponse.json();
            console.log('✅ Retry successful:', retryData.choices[0].message);
            return retryData;
          }
        } catch (retryError) {
          console.error('❌ Retry also failed:', retryError);
        }
      }
      
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
