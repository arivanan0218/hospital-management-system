class OpenAIService {
  constructor() {
    // Try to load API key from environment first, then fallback to manual setting
    this.apiKey = import.meta.env.VITE_OPENAI_API_KEY || localStorage.getItem('openaiApiKey') || '';
    this.baseUrl = 'https://api.openai.com/v1/chat/completions';
    this.model = 'gpt-4o'; // Latest GPT-4 model
    this.maxTokens = 4096;
    
    console.log('🔑 OpenAI Service Debug:', {
      envApiKey: import.meta.env.VITE_OPENAI_API_KEY ? 'Present (env)' : 'Missing (env)',
      localStorageKey: localStorage.getItem('openaiApiKey') ? 'Present (localStorage)' : 'Missing (localStorage)',
      finalApiKey: this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing'
    });
    
    if (!this.apiKey) {
      console.warn('OpenAI API key not found. Please set VITE_OPENAI_API_KEY in your .env file or configure it in the UI settings');
    }
  }

  // Method to update API key dynamically
  updateApiKey(newApiKey) {
    this.apiKey = newApiKey;
    console.log('🔄 OpenAI API key updated:', this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing');
  }

  get systemPrompt() {
    return `You are an intelligent AI assistant for a Hospital Management System. You have access to real-time hospital data through integrated tools and can help with:

🏥 **Core Capabilities:**
- Patient management and records
- Bed allocation and availability
- Staff scheduling and information
- Equipment tracking and maintenance
- Supply inventory management
- Appointment scheduling
- Department operations

📊 **Data Integration:**
- You receive REAL hospital data from the MCP bridge
- Always use actual data when available
- Format responses clearly with tables, lists, and highlights
- Be specific and accurate with medical information

🔧 **Tool Usage:**
- When user asks about patients, staff, beds, etc., I provide REAL data
- Use the hospital management tools to fetch current information
- Present data in a user-friendly format

🩺 **Medical Context:**
- Maintain patient confidentiality and privacy
- Provide helpful medical administrative assistance
- Suggest best practices for hospital operations
- When showing data, format it clearly and highlight important information

Always respond with actual data from the hospital system when available, not generic responses.`;
  }

  async generateResponse(userMessage, mcpData = null, conversationHistory = [], availableTools = []) {
    try {
      console.log('🤖 OpenAI Service Debug:', {
        apiKey: this.apiKey ? 'Present (length: ' + this.apiKey.length + ')' : 'Missing',
        userMessage: userMessage.substring(0, 50) + '...',
        hasMcpData: !!mcpData,
        toolCount: availableTools.length
      });

      if (!this.apiKey) {
        throw new Error('OpenAI API key not configured');
      }

      // Build messages for OpenAI's format
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
      
      if (mcpData) {
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

      // Add available tools information
      if (availableTools.length > 0) {
        currentContent += `\n\n**Available Hospital Tools:** ${availableTools.length} tools available including patient management, bed allocation, staff scheduling, equipment tracking, and more.`;
      }

      messages.push({
        role: 'user',
        content: currentContent
      });

      // Instead of calling OpenAI API directly, route through MCP bridge
      const mcpBridgeUrl = import.meta.env.VITE_MCP_BRIDGE_URL || 'http://localhost:8080';
      
      const requestBody = {
        model: this.model,
        max_tokens: this.maxTokens,
        messages: messages,
        api_key: this.apiKey  // Pass API key to bridge
      };

      console.log('🔄 Calling OpenAI via MCP Bridge:', {
        url: `${mcpBridgeUrl}/openai`,
        messageCount: messages.length,
        hasMcpData: !!mcpData,
        toolCount: availableTools.length
      });

      const response = await fetch(`${mcpBridgeUrl}/openai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`MCP Bridge OpenAI API error: ${response.status} ${response.statusText} - ${errorData.error || 'Unknown error'}`);
      }

      const data = await response.json();
      
      if (!data.choices || !data.choices[0] || !data.choices[0].message) {
        throw new Error('Invalid response format from OpenAI API via MCP Bridge');
      }

      return {
        success: true,
        message: data.choices[0].message.content,
        usage: {
          inputTokens: data.usage?.prompt_tokens || 0,
          outputTokens: data.usage?.completion_tokens || 0
        },
        model: data.model
      };

    } catch (error) {
      console.error('❌ OpenAI API error:', error);
      return {
        success: false,
        error: error.message,
        message: `I apologize, but I encountered an error while processing your request: ${error.message}`
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

export default new OpenAIService();
