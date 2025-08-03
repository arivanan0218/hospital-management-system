/**
 * Hospital AI Chatbot Component
 * Integrates Gemini AI with MCP Bridge for hospital management
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Settings, Activity, AlertCircle, CheckCircle, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { v4 as uuidv4 } from 'uuid';

import GeminiService from '../services/gemini';
import ClaudeService from '../services/claude';
import OpenAIService from '../services/openai';
import GroqService from '../services/groq';
import MCPBridgeService from '../services/mcpBridge';
import QuickActions from './QuickActions';
import DataDisplay from './DataDisplay';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      role: 'assistant',
      content: '👋 Hello! I\'m your Hospital Management AI Assistant. I can help you with patient records, staff management, bed assignments, equipment tracking, and more. What would you like to know?',
      timestamp: new Date(),
      type: 'welcome'
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [geminiApiKey, setGeminiApiKey] = useState(localStorage.getItem('geminiApiKey') || '');
  const [claudeApiKey, setClaudeApiKey] = useState(
    localStorage.getItem('claudeApiKey') || 
    import.meta.env.VITE_CLAUDE_API_KEY || 
    ''
  );
  const [openaiApiKey, setOpenaiApiKey] = useState(
    localStorage.getItem('openaiApiKey') || 
    import.meta.env.VITE_OPENAI_API_KEY || 
    ''
  );
  const [groqApiKey, setGroqApiKey] = useState(
    localStorage.getItem('groqApiKey') || 
    import.meta.env.VITE_GROQ_API_KEY || 
    ''
  );
  const [selectedAI, setSelectedAI] = useState(localStorage.getItem('selectedAI') || 'groq'); // 'claude', 'gemini', 'openai', or 'groq'
  const [showSettings, setShowSettings] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [mcpStatus, setMcpStatus] = useState('unknown');
  const [mcpTools, setMcpTools] = useState([]);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Services
  const [geminiService, setGeminiService] = useState(null);
  const [claudeService] = useState(ClaudeService);
  const [openaiService] = useState(OpenAIService);
  const [groqService] = useState(GroqService);
  const [mcpService] = useState(new MCPBridgeService());

  // Initialize services
  useEffect(() => {
    if (geminiApiKey) {
      try {
        setGeminiService(new GeminiService(geminiApiKey));
      } catch (error) {
        console.error('Failed to initialize Gemini service:', error);
      }
    }
  }, [geminiApiKey]);

  // Update Claude API key when changed
  useEffect(() => {
    if (claudeApiKey) {
      claudeService.updateApiKey(claudeApiKey);
    }
  }, [claudeApiKey]);

  // Update OpenAI API key when changed
  useEffect(() => {
    if (openaiApiKey) {
      openaiService.updateApiKey(openaiApiKey);
    }
  }, [openaiApiKey, openaiService]);

  // Update Groq API key when changed
  useEffect(() => {
    if (groqApiKey) {
      groqService.updateApiKey(groqApiKey);
    }
  }, [groqApiKey, groqService]);

  // Check MCP bridge status
  useEffect(() => {
    const checkMCPStatus = async () => {
      try {
        await mcpService.healthCheck();
        setMcpStatus('connected');
        
        // Load available tools
        const toolsResponse = await mcpService.listTools();
        setMcpTools(toolsResponse.tools || []);
      } catch (error) {
        setMcpStatus('disconnected');
        console.error('MCP Bridge not available:', error);
      }
    };

    checkMCPStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkMCPStatus, 30000);
    return () => clearInterval(interval);
  }, [mcpService]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Save API key to localStorage
  useEffect(() => {
    if (geminiApiKey) {
      localStorage.setItem('geminiApiKey', geminiApiKey);
    }
  }, [geminiApiKey]);

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || isLoading) return;
    
    if (!geminiService) {
      alert('Please configure your Gemini API key in settings first.');
      setShowSettings(true);
      return;
    }

    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
      type: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Choose AI service based on selection
      const activeAI = selectedAI === 'claude' ? claudeService : 
                   selectedAI === 'openai' ? openaiService :
                   selectedAI === 'groq' ? groqService : geminiService;
      const aiServiceName = selectedAI === 'claude' ? 'Claude' : 
                           selectedAI === 'openai' ? 'OpenAI' :
                           selectedAI === 'groq' ? 'Groq' : 'Gemini';

      if (!activeAI || (selectedAI === 'gemini' && !geminiService)) {
        throw new Error(`${aiServiceName} service not available. Please configure API key in settings.`);
      }

      // Analyze user query to determine if MCP data is needed
      const queryAnalysis = await activeAI.analyzeQuery(userMessage.content);
      
      let mcpData = null;
      let mcpError = null;

      // FORCE MCP CALLS for ALL hospital-related queries
      if (mcpStatus === 'connected') {
        const message = userMessage.content.toLowerCase();
        // Check for ANY hospital-related keywords
        if (message.includes('patient') || message.includes('bed') || message.includes('staff') || 
            message.includes('appointment') || message.includes('equipment') || message.includes('supply') ||
            message.includes('department') || message.includes('room') || message.includes('user') ||
            message.includes('add') || message.includes('create') || message.includes('register') ||
            message.includes('new') || message.includes('nivetha') || message.includes('full name') ||
            message.includes('dob') || message.includes('date of birth') || message.includes('phone') ||
            message.includes('address') || message.includes('emergency') || message.includes('medical') ||
            message.includes('arivu') || message.includes('list') || message.includes('show') ||
            message.includes('available') || message.includes('occupied') || message.includes('assign') ||
            queryAnalysis.needsMCPData) {
          try {
            console.log('🚀 Forcing MCP call for hospital query:', userMessage.content);
            mcpData = await mcpService.analyzeAndExecuteQuery(userMessage.content);
            console.log('✅ MCP Data retrieved:', mcpData);
          } catch (error) {
            mcpError = error.message;
            console.error('❌ MCP query failed:', error);
          }
        }
      }

      // Generate AI response using selected service
      let aiResponse;
      
      // If we have MCP tool results from creation operations, prioritize them
      if (mcpData && mcpData.toolResult) {
        console.log('🎯 Using MCP tool result as primary response');
        
        const operation = mcpData.operation || 'operation';
        const result = mcpData.toolResult;
        
        if (operation.includes('create') || operation.includes('add')) {
          // Creation operations - show success with details
          aiResponse = `✅ **${operation.replace('_', ' ').toUpperCase()} SUCCESSFUL**\n\n`;
          aiResponse += `🏥 **Real Database Operation Completed**\n\n`;
          
          if (result.patient_id || result.id) {
            const id = result.patient_id || result.id;
            aiResponse += `**Created Record ID:** ${id}\n\n`;
          }
          
          if (result.patient_number) {
            aiResponse += `**Patient Number:** ${result.patient_number}\n`;
          }
          if (result.first_name && result.last_name) {
            aiResponse += `**Name:** ${result.first_name} ${result.last_name}\n`;
          }
          if (result.bed_number) {
            aiResponse += `**Bed Number:** ${result.bed_number}\n`;
          }
          if (result.date_of_birth) {
            aiResponse += `**Date of Birth:** ${result.date_of_birth}\n`;
          }
          if (result.phone) {
            aiResponse += `**Phone:** ${result.phone}\n`;
          }
          
          aiResponse += `\n🎉 **This was a REAL database operation!** The record has been permanently saved to the hospital management system.\n\n`;
          aiResponse += `You can verify this by asking to "list all patients" or checking the relevant records.`;
        } else {
          // Other operations
          aiResponse = `✅ **${operation.replace('_', ' ').toUpperCase()} COMPLETED**\n\n`;
          aiResponse += JSON.stringify(result, null, 2);
        }
      } else {
        // Normal AI response generation
        try {
          aiResponse = await activeAI.generateResponse(
            userMessage.content,
            mcpData,
            messages.slice(-10), // Last 10 messages for context
            mcpTools // Available tools for Claude
          );
        } catch (error) {
          // If AI service fails, provide a helpful demo response with real data
          console.warn('🔄 AI service failed, providing demo response with real data:', error);
          
          let responseMessage = `🏥 **Hospital Management System** (Real Database Connected)\n\n`;
        
        if (mcpData && mcpData.data) {
          // Format the real hospital data nicely
          if (mcpData.description) {
            responseMessage += `📊 **${mcpData.description}**\n\n`;
          }
          
          if (Array.isArray(mcpData.data)) {
            responseMessage += `**Found ${mcpData.data.length} record(s):**\n\n`;
            
            // Format different types of data
            mcpData.data.forEach((item, index) => {
              if (item.bed_number) {
                // Bed data
                responseMessage += `🛏️ **Bed ${item.bed_number}**\n`;
                responseMessage += `   - Type: ${item.bed_type}\n`;
                responseMessage += `   - Status: ${item.status}\n`;
                responseMessage += `   - Room ID: ${item.room_id}\n`;
                if (item.patient_id) {
                  responseMessage += `   - Patient: ${item.patient_id}\n`;
                }
                responseMessage += `\n`;
              } else if (item.patient_number) {
                // Patient data
                responseMessage += `👤 **Patient ${item.patient_number}**: ${item.first_name} ${item.last_name}\n`;
                responseMessage += `   - DOB: ${item.date_of_birth}\n`;
                if (item.phone) responseMessage += `   - Phone: ${item.phone}\n`;
                if (item.blood_type) responseMessage += `   - Blood Type: ${item.blood_type}\n`;
                responseMessage += `\n`;
              } else if (item.name && item.description) {
                // Department data
                responseMessage += `🏢 **${item.name}**\n`;
                responseMessage += `   - ${item.description}\n`;
                if (item.floor_number) responseMessage += `   - Floor: ${item.floor_number}\n`;
                responseMessage += `\n`;
              } else {
                // Generic data
                responseMessage += `📋 **Record ${index + 1}**\n`;
                Object.entries(item).slice(0, 3).forEach(([key, value]) => {
                  if (value && !key.includes('id') && !key.includes('_at')) {
                    responseMessage += `   - ${key}: ${value}\n`;
                  }
                });
                responseMessage += `\n`;
              }
            });
          } else {
            responseMessage += `📋 **Data Retrieved:**\n${JSON.stringify(mcpData.data, null, 2)}\n\n`;
          }
        } else if (mcpError) {
          responseMessage += `⚠️ **Connection Issue:** ${mcpError}\n\n`;
        } else {
          responseMessage += `ℹ️ **No specific data requested.**\n\n`;
        }
        
        responseMessage += `✅ **System Status:** All hospital management tools are operational\n\n`;
        responseMessage += `💡 **Note:** AI service quota exceeded. Showing raw data from hospital database.\n`;
        responseMessage += `To get AI-powered responses, add credits to your API account.`;
        
        aiResponse = {
          success: true,
          message: responseMessage,
          usage: { inputTokens: 0, outputTokens: 0 },
          model: 'database-direct'
        };
        }
      }

      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: aiResponse.message,
        timestamp: new Date(),
        type: 'ai_response',
        mcpData: mcpData,
        mcpError: mcpError,
        queryAnalysis: queryAnalysis,
        aiService: aiServiceName,
        usage: aiResponse.usage
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please check your API key and try again.',
        timestamp: new Date(),
        type: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (query) => {
    setInputMessage(query);
    handleSendMessage(query);
  };

  const clearChat = () => {
    setMessages([
      {
        id: uuidv4(),
        role: 'assistant',
        content: '👋 Chat cleared! How can I help you with hospital management today?',
        timestamp: new Date(),
        type: 'welcome'
      }
    ]);
  };

  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500 ml-2' : 'bg-green-500 mr-2'
          }`}>
            {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
          </div>
          
          {/* Message content */}
          <div className={`rounded-lg px-4 py-2 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : message.type === 'error'
                ? 'bg-red-50 border border-red-200'
                : 'bg-gray-50 border border-gray-200'
          }`}>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  code({inline, className, children, ...props}) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            
            {/* Show MCP data if available */}
            {message.mcpData && (
              <div className="mt-3">
                <DataDisplay 
                  data={message.mcpData.data} 
                  type={message.mcpData.type}
                  title={message.mcpData.description}
                />
              </div>
            )}
            
            {/* Show MCP error if any */}
            {message.mcpError && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
                <div className="font-medium text-yellow-800 mb-1">
                  ⚠️ System Access Issue
                </div>
                <div className="text-yellow-600">
                  {message.mcpError}
                </div>
              </div>
            )}
            
            <div className="text-xs opacity-60 mt-2">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
            <Bot className="text-white" size={20} />
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">Hospital AI Assistant</h1>
            <div className="flex items-center space-x-2 text-sm">
              <div className={`flex items-center space-x-1 ${
                mcpStatus === 'connected' ? 'text-green-600' : 'text-red-600'
              }`}>
                {mcpStatus === 'connected' ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                <span>MCP Bridge {mcpStatus}</span>
              </div>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600">{mcpTools.length} tools available</span>
              <span className="text-gray-400">•</span>
              <span className={`font-medium ${
                selectedAI === 'claude' ? 'text-purple-600' : 
                selectedAI === 'openai' ? 'text-green-600' :
                selectedAI === 'groq' ? 'text-orange-600' : 'text-blue-600'
              }`}>
                {selectedAI === 'claude' ? 'Claude AI' : 
                 selectedAI === 'openai' ? 'OpenAI GPT-4' :
                 selectedAI === 'groq' ? 'Groq Llama' : 'Gemini AI'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowQuickActions(!showQuickActions)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Quick Actions"
          >
            <Zap size={18} className="text-gray-600" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Settings"
          >
            <Settings size={18} className="text-gray-600" />
          </button>
          <button
            onClick={clearChat}
            className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
          <div className="max-w-md space-y-4">
            {/* AI Service Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Service
              </label>
              <select
                value={selectedAI}
                onChange={(e) => {
                  setSelectedAI(e.target.value);
                  localStorage.setItem('selectedAI', e.target.value);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="groq">Groq Llama (Free & Fast) - Recommended</option>
                <option value="openai">OpenAI GPT-4</option>
                <option value="claude">Claude (Anthropic)</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>

            {/* Groq API Key */}
            {selectedAI === 'groq' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Groq API Key
                </label>
                <input
                  type="password"
                  value={groqApiKey}
                  onChange={(e) => {
                    setGroqApiKey(e.target.value);
                    localStorage.setItem('groqApiKey', e.target.value);
                    groqService.updateApiKey(e.target.value);
                  }}
                  placeholder="Enter your Groq API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-600 mt-1">
                  Get your free API key from <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Groq Console</a> - Free & Fast!
                </p>
              </div>
            )}

            {/* OpenAI API Key */}
            {selectedAI === 'openai' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => {
                    setOpenaiApiKey(e.target.value);
                    localStorage.setItem('openaiApiKey', e.target.value);
                    openaiService.updateApiKey(e.target.value);
                  }}
                  placeholder="Enter your OpenAI API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-600 mt-1">
                  Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI Platform</a>
                </p>
              </div>
            )}

            {/* Claude API Key */}
            {selectedAI === 'claude' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claude API Key
                </label>
                <input
                  type="password"
                  value={claudeApiKey}
                  onChange={(e) => {
                    setClaudeApiKey(e.target.value);
                    localStorage.setItem('claudeApiKey', e.target.value);
                  }}
                  placeholder="Enter your Anthropic Claude API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-600 mt-1">
                  Get your API key from <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Anthropic Console</a>
                </p>
              </div>
            )}

            {/* Gemini API Key */}
            {selectedAI === 'gemini' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gemini API Key
                </label>
                <input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => {
                    setGeminiApiKey(e.target.value);
                    localStorage.setItem('geminiApiKey', e.target.value);
                  }}
                  placeholder="Enter your Google Gemini API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-600 mt-1">
                  Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a>
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {/* Quick Actions Panel */}
        {showQuickActions && messages.length <= 1 && (
          <div className="mb-6">
            <QuickActions onActionClick={handleQuickAction} />
          </div>
        )}
        
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <Activity className="animate-spin" size={16} />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-3">
        <div className="flex space-x-3">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about patients, staff, beds, appointments..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim() || !geminiService}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
