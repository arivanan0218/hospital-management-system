/**
 * Gemini AI Service - Handles communication with Google's Gemini API
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

class GeminiService {
  constructor(apiKey) {
    if (!apiKey) {
      throw new Error('Gemini API key is required');
    }
    
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    
    // System prompt for hospital management context
    this.systemPrompt = `You are a helpful AI assistant for a Hospital Management System. You can help users with:

1. Patient management (creating, listing, finding patients)
2. Staff management (listing staff, departments)
3. Bed management (finding available beds, assignments)
4. Equipment tracking
5. Supply inventory management
6. Appointment scheduling
7. General hospital operations

You have access to a hospital management system through an MCP (Model Context Protocol) bridge. When users ask questions about hospital data or want to perform operations, you can:

- Query the system for real-time data
- Help interpret results
- Suggest appropriate actions
- Provide context and explanations

Always be helpful, professional, and focused on healthcare operations. If you need to access hospital data, mention that you're checking the system and provide clear, organized results.

Guidelines:
- Be concise but thorough
- Use medical terminology appropriately
- Prioritize patient safety and privacy
- Suggest best practices for hospital operations
- When showing data, format it clearly and highlight important information`;
  }

  async generateResponse(userMessage, mcpData = null, conversationHistory = []) {
    try {
      // Build the conversation context
      let prompt = this.systemPrompt + '\n\n';
      
      // Add conversation history for context
      if (conversationHistory.length > 0) {
        prompt += 'Previous conversation:\n';
        conversationHistory.slice(-6).forEach(msg => { // Last 6 messages for context
          prompt += `${msg.role}: ${msg.content}\n`;
        });
        prompt += '\n';
      }
      
      // Add MCP data if available
      if (mcpData) {
        prompt += `Current hospital system data:\n`;
        prompt += `Type: ${mcpData.type}\n`;
        prompt += `Description: ${mcpData.description}\n`;
        prompt += `Data: ${JSON.stringify(mcpData.data, null, 2)}\n\n`;
      }
      
      // Add current user message
      prompt += `User: ${userMessage}\n`;
      prompt += `Assistant: `;
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      return {
        success: true,
        message: text,
        usage: response.usage || null
      };
      
    } catch (error) {
      console.error('Gemini API error:', error);
      return {
        success: false,
        error: error.message,
        message: 'I apologize, but I encountered an error while processing your request. Please try again.'
      };
    }
  }

  async analyzeQuery(userMessage) {
    try {
      const analysisPrompt = `Analyze this user query for a hospital management system and determine what kind of data or action they might need:

User Query: "${userMessage}"

Determine:
1. Intent (query_data, create_record, update_record, general_question)
2. Entity Type (patient, staff, bed, department, appointment, equipment, supply, or general)
3. Specific Action (list, find, create, update, delete, assign, discharge)
4. Keywords to match

Respond in JSON format:
{
  "intent": "query_data|create_record|update_record|general_question",
  "entityType": "patient|staff|bed|department|appointment|equipment|supply|general",
  "action": "list|find|create|update|delete|assign|discharge|help",
  "keywords": ["keyword1", "keyword2"],
  "needsMCPData": true|false,
  "suggestedMCPQuery": "suggested query for MCP system if needed"
}`;

      const result = await this.model.generateContent(analysisPrompt);
      const response = await result.response;
      const text = response.text();
      
      try {
        // Extract JSON from the response
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      } catch (parseError) {
        console.warn('Failed to parse query analysis:', parseError);
      }
      
      // Fallback analysis
      return {
        intent: 'general_question',
        entityType: 'general',
        action: 'help',
        keywords: userMessage.toLowerCase().split(' '),
        needsMCPData: false,
        suggestedMCPQuery: null
      };
      
    } catch (error) {
      console.error('Query analysis error:', error);
      return {
        intent: 'general_question',
        entityType: 'general',
        action: 'help',
        keywords: [],
        needsMCPData: false,
        suggestedMCPQuery: null
      };
    }
  }

  async generateDataSummary(data, dataType) {
    try {
      const summaryPrompt = `Summarize this hospital ${dataType} data in a clear, professional manner:

Data: ${JSON.stringify(data, null, 2)}

Provide:
1. A brief overview
2. Key statistics or counts
3. Any important observations
4. Formatted display of the most relevant information

Keep it concise but informative, suitable for hospital staff.`;

      const result = await this.model.generateContent(summaryPrompt);
      const response = await result.response;
      return response.text();
      
    } catch (error) {
      console.error('Data summary error:', error);
      return `Retrieved ${dataType} data. Please see the details below.`;
    }
  }
}

export default GeminiService;
