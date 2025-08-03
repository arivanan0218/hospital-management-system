import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import AIMCPService from '../services/aiMcpService';

const ClaudeDesktopChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      role: 'assistant',
      content: '🤖 **AI Hospital Assistant**\n\nI\'m connected to your hospital MCP server with AI intelligence! Just talk to me naturally:\n\n• "Create a patient named John Smith born on 1985-03-15"\n• "Show me all patients"\n• "Add a new cardiology department"\n• "List all available beds"\n• "Create room 301 in cardiology"\n\nI understand natural language and will call the right database operations for you! 🏥',
      timestamp: new Date(),
      type: 'assistant'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiService] = useState(new AIMCPService());
  const [isConnected, setIsConnected] = useState(false);
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_OPENAI_API_KEY || '');
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-connect on component mount if API key is available
  useEffect(() => {
    const autoConnect = async () => {
      const envApiKey = import.meta.env.VITE_OPENAI_API_KEY;
      if (envApiKey) {
        console.log('🔑 Found OpenAI API key in environment, auto-connecting...');
        setApiKey(envApiKey);
        
        // Connect directly with the env API key
        try {
          setIsLoading(true);
          const connected = await aiService.initialize(envApiKey);
          
          if (connected) {
            setIsConnected(true);
            setShowApiKeyInput(false);
            
            const welcomeMessage = {
              id: uuidv4(),
              role: 'assistant',
              content: '✅ **Auto-Connected to AI Hospital System**\n\n🧠 OpenAI GPT-4 is ready\n🏥 MCP Hospital Server connected\n🔑 Using API key from environment\n\nYou can now speak naturally and I\'ll handle the database operations!',
              timestamp: new Date(),
              type: 'system'
            };
            setMessages(prev => [...prev, welcomeMessage]);
          }
        } catch (error) {
          console.error('Auto-connection failed:', error);
          setShowApiKeyInput(true);
        } finally {
          setIsLoading(false);
        }
      } else {
        setShowApiKeyInput(true);
      }
    };
    
    autoConnect();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Connect to AI service with API key
  const connectWithApiKey = async (providedApiKey = null) => {
    const keyToUse = providedApiKey || apiKey.trim();
    if (!keyToUse) {
      alert('Please enter your OpenAI API key');
      return;
    }

    try {
      setIsLoading(true);
      const connected = await aiService.initialize(keyToUse);
      
      if (connected) {
        setIsConnected(true);
        setShowApiKeyInput(false);
        
        const welcomeMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: '✅ **Connected to AI Hospital System**\n\n🧠 OpenAI GPT-4 is now analyzing your requests\n🏥 MCP Hospital Server is ready\n\nYou can now speak naturally and I\'ll handle the database operations!',
          timestamp: new Date(),
          type: 'system'
        };
        setMessages(prev => [...prev, welcomeMessage]);
      }
    } catch (error) {
      console.error('Connection failed:', error);
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: `❌ **Connection Failed**\n\n${error.message}\n\nPlease check:\n• Your OpenAI API key is valid\n• MCP server is running on port 8080\n• You have sufficient OpenAI credits`,
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || isLoading) return;

    if (!isConnected) {
      alert('Please connect with your OpenAI API key first');
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
      console.log('🤖 Sending to AI service:', textToSend);
      
      // Process with AI
      const aiResult = await aiService.processRequest(textToSend);
      
      let responseContent;
      
      if (aiResult.success) {
        // Start with AI response, handle null/empty responses
        const aiMessage = aiResult.message || "I've processed your request successfully.";
        responseContent = aiMessage + '\n\n';
        
        // Add function call results
        if (aiResult.functionCalls && aiResult.functionCalls.length > 0) {
          responseContent += '🔧 **Database Operations Performed:**\n\n';
          
          aiResult.functionCalls.forEach((call, index) => {
            if (call.success) {
              responseContent += `${index + 1}. ✅ **${call.function.toUpperCase().replace('_', ' ')}**\n`;
              
              if (call.result?.data) {
                const record = call.result.data;
                responseContent += '   📋 **Record Details:**\n';
                
                if (record.patient_number) responseContent += `   • Patient #: ${record.patient_number}\n`;
                if (record.first_name && record.last_name) responseContent += `   • Name: ${record.first_name} ${record.last_name}\n`;
                if (record.date_of_birth) responseContent += `   • DOB: ${record.date_of_birth}\n`;
                if (record.phone) responseContent += `   • Phone: ${record.phone}\n`;
                if (record.email) responseContent += `   • Email: ${record.email}\n`;
                if (record.name) responseContent += `   • Name: ${record.name}\n`;
                if (record.room_number) responseContent += `   • Room: ${record.room_number}\n`;
                if (record.bed_number) responseContent += `   • Bed: ${record.bed_number}\n`;
                if (record.id) responseContent += `   • Database ID: ${record.id}\n`;
                
                responseContent += `   ⏰ Created: ${record.created_at || 'just now'}\n`;
              } else if (call.result?.patients) {
                responseContent += `   📊 **Found ${call.result.patients.length} patients:**\n\n`;
                call.result.patients.slice(0, 10).forEach((patient, index) => {
                  responseContent += `   ${index + 1}. **${patient.first_name} ${patient.last_name}** (${patient.patient_number})\n`;
                  responseContent += `      📅 DOB: ${patient.date_of_birth} | 📞 ${patient.phone || 'No phone'}\n`;
                  if (patient.email) responseContent += `      📧 ${patient.email}\n`;
                  if (patient.address) responseContent += `      🏠 ${patient.address}\n`;
                  responseContent += `\n`;
                });
                if (call.result.patients.length > 10) {
                  responseContent += `   ... and ${call.result.patients.length - 10} more patients\n`;
                }
              } else if (call.result?.departments) {
                responseContent += `   📊 **Found ${call.result.departments.length} departments:**\n\n`;
                call.result.departments.forEach((dept, index) => {
                  responseContent += `   ${index + 1}. **${dept.name}**\n`;
                  if (dept.description) responseContent += `      📝 ${dept.description}\n`;
                  if (dept.floor_number) responseContent += `      🏢 Floor: ${dept.floor_number}\n`;
                  if (dept.phone) responseContent += `      📞 ${dept.phone}\n`;
                  responseContent += `\n`;
                });
              } else if (call.result?.beds) {
                responseContent += `   📊 **Found bed information:**\n\n`;
                const bedGroups = {};
                call.result.beds.forEach(bed => {
                  const status = bed.status || 'unknown';
                  if (!bedGroups[status]) bedGroups[status] = [];
                  bedGroups[status].push(bed);
                });
                
                Object.keys(bedGroups).forEach(status => {
                  responseContent += `   **${status.toUpperCase()} BEDS (${bedGroups[status].length}):**\n`;
                  bedGroups[status].slice(0, 5).forEach(bed => {
                    responseContent += `   • ${bed.bed_number} (Room: ${bed.room_number || 'N/A'})\n`;
                  });
                  if (bedGroups[status].length > 5) {
                    responseContent += `     ... and ${bedGroups[status].length - 5} more\n`;
                  }
                  responseContent += `\n`;
                });
              } else if (call.result?.rooms) {
                responseContent += `   📊 **Found ${call.result.rooms.length} rooms:**\n\n`;
                call.result.rooms.forEach((room, index) => {
                  responseContent += `   ${index + 1}. **Room ${room.room_number}**\n`;
                  if (room.room_type) responseContent += `      🏠 Type: ${room.room_type}\n`;
                  if (room.capacity) responseContent += `      👥 Capacity: ${room.capacity}\n`;
                  if (room.floor_number) responseContent += `      🏢 Floor: ${room.floor_number}\n`;
                  responseContent += `\n`;
                });
              } else if (call.result?.staff) {
                responseContent += `   📊 **Found staff information:**\n\n`;
                call.result.staff.slice(0, 10).forEach((staff, index) => {
                  responseContent += `   ${index + 1}. **${staff.user?.first_name || 'N/A'} ${staff.user?.last_name || ''}**\n`;
                  if (staff.position) responseContent += `      💼 Position: ${staff.position}\n`;
                  if (staff.department_name) responseContent += `      🏢 Department: ${staff.department_name}\n`;
                  responseContent += `\n`;
                });
              } else {
                // Show generic info or error details
                if (call.error) {
                  responseContent += `   ❌ Error: ${call.error}\n`;
                } else {
                  responseContent += `   📊 Found ${call.function.replace('list_', '').replace('_', ' ')} information\n`;
                }
              }
              
              responseContent += '\n';
            } else {
              responseContent += `${index + 1}. ❌ **${call.function.toUpperCase().replace('_', ' ')} FAILED**\n`;
              responseContent += `   Error: ${call.error}\n\n`;
            }
          });
          
          responseContent += '🎉 **All operations were real database transactions!**';
        }
      } else {
        responseContent = `❌ **AI Processing Failed**\n\n${aiResult.message || aiResult.error}`;
      }

      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        type: aiResult.success ? 'success' : 'error'
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('💥 Error in AI processing:', error);
      
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: `❌ **System Error**\n\n${error.message}\n\nPlease check your OpenAI API key and MCP server connection.`,
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

  const handleApiKeySubmit = (e) => {
    if (e.key === 'Enter') {
      connectWithApiKey();
    }
  };

  const quickActions = [
    { label: '👥 List all patients', action: 'Show me all patients in the hospital' },
    { label: '🏨 List departments', action: 'What departments do we have?' },
    { label: '🛏️ Show beds', action: 'Show me all beds and their status' },
    { label: '👨‍⚕️ List staff', action: 'List all hospital staff' },
    { label: '🏠 Show rooms', action: 'What rooms are available?' }
  ];

  const getMessageStyle = (type) => {
    switch (type) {
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      case 'system':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  if (showApiKeyInput) {
    return (
      <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50 p-6">
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg border w-full max-w-md">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">🤖 AI Hospital Assistant</h2>
              <p className="text-gray-600">Connect with Claude Desktop-like experience</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  onKeyPress={handleApiKeySubmit}
                  placeholder="sk-..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <button
                onClick={connectWithApiKey}
                disabled={isLoading || !apiKey.trim()}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Connecting...
                  </>
                ) : (
                  'Connect to Hospital AI'
                )}
              </button>
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">🔒 Privacy & Security</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• API key is stored only in browser memory</li>
                <li>• No API key is saved or transmitted to our servers</li>
                <li>• Direct connection to OpenAI and your MCP server</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">🤖 AI Hospital Assistant</h1>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'AI Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-1">Natural language → AI → Hospital database operations</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`border rounded-lg p-4 ${getMessageStyle(message.type)} ${
              message.role === 'user' ? 'ml-12' : 'mr-12'
            }`}
          >
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg">
                {message.role === 'user' ? '👤' : '🤖'}
              </span>
              <span className="font-medium text-sm text-gray-600">
                {message.role === 'user' ? 'You' : 'AI Assistant'}
              </span>
              <span className="text-xs text-gray-400">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className="prose prose-sm max-w-none">
              {message.content.split('\n').map((line, index) => (
                <div key={index} className={line.trim() === '' ? 'mb-2' : ''}>
                  {line.includes('**') ? (
                    <div dangerouslySetInnerHTML={{
                      __html: line
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/• /g, '• ')
                    }} />
                  ) : (
                    <div>{line}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="border rounded-lg p-4 mr-12 border-blue-200 bg-blue-50">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-blue-800">AI is analyzing your request...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex flex-wrap gap-2 mb-3">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleSendMessage(action.action)}
              disabled={isLoading || !isConnected}
              className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full border text-gray-700 disabled:opacity-50"
            >
              {action.label}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Speak naturally: 'Create a patient named John Smith...' or 'Show me all departments'"
            disabled={isLoading || !isConnected}
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim() || !isConnected}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '⏳' : '🚀'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClaudeDesktopChatbot;
