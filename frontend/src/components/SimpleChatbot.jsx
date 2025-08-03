import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import MCPClient from '../services/mcpClient';

const SimpleChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      role: 'assistant',
      content: '🏥 **Hospital Management System**\n\nI\'m connected directly to the hospital MCP server. I can help you with:\n\n• **Create patients** - "Create patient with full name: John Doe, date of birth: 1990-01-15"\n• **List patients** - "List all patients"\n• **Create departments** - "Create department: Cardiology"\n• **Create rooms** - "Create room: 301, department: Cardiology"\n• **Create beds** - "Create bed: B301A, room: 301"\n• **List beds, staff, departments**\n\nAll operations are **real database transactions**!',
      timestamp: new Date(),
      type: 'assistant'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mcpClient] = useState(new MCPClient());
  const [isConnected, setIsConnected] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Connect to MCP server on component mount
  useEffect(() => {
    const connectToMCP = async () => {
      console.log('🚀 Connecting to MCP server...');
      const connected = await mcpClient.connect();
      setIsConnected(connected);
      
      if (connected) {
        const welcomeMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: '✅ **Connected to Hospital MCP Server**\n\nReady to process real hospital operations!',
          timestamp: new Date(),
          type: 'system'
        };
        setMessages(prev => [...prev, welcomeMessage]);
      } else {
        const errorMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: '❌ **Failed to connect to MCP server**\n\nPlease ensure the MCP bridge is running on port 8080.',
          timestamp: new Date(),
          type: 'error'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    };

    connectToMCP();

    // Cleanup on unmount
    return () => {
      mcpClient.disconnect();
    };
  }, [mcpClient]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || isLoading) return;

    if (!isConnected) {
      alert('MCP server not connected. Please check the server status.');
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
      console.log('📨 Sending message to MCP server:', textToSend);
      
      // Execute query using MCP client
      const mcpResult = await mcpClient.executeQuery(textToSend);
      
      let responseContent;
      
      if (mcpResult.success) {
        // Format successful operation response
        responseContent = `✅ **${mcpResult.operation?.toUpperCase().replace('_', ' ')} SUCCESSFUL**\n\n`;
        responseContent += `🏥 **Real Database Operation Completed**\n\n`;
        
        if (mcpResult.result) {
          const result = mcpResult.result;
          
          // Handle different result types
          if (result.data) {
            // Single record creation
            const record = result.data;
            responseContent += `**Record Details:**\n`;
            
            if (record.patient_number) responseContent += `• Patient Number: ${record.patient_number}\n`;
            if (record.first_name && record.last_name) responseContent += `• Name: ${record.first_name} ${record.last_name}\n`;
            if (record.date_of_birth) responseContent += `• Date of Birth: ${record.date_of_birth}\n`;
            if (record.phone) responseContent += `• Phone: ${record.phone}\n`;
            if (record.email) responseContent += `• Email: ${record.email}\n`;
            if (record.address) responseContent += `• Address: ${record.address}\n`;
            if (record.id) responseContent += `• Database ID: ${record.id}\n`;
            if (record.bed_number) responseContent += `• Bed Number: ${record.bed_number}\n`;
            if (record.room_number) responseContent += `• Room Number: ${record.room_number}\n`;
            if (record.name) responseContent += `• Name: ${record.name}\n`;
            
            responseContent += `\n✅ **Record saved to database at:** ${record.created_at || 'just now'}\n`;
          } else if (result.patients) {
            // Patient list
            responseContent += `**Found ${result.patients.length} patients:**\n\n`;
            result.patients.slice(0, 10).forEach((patient, index) => {
              responseContent += `${index + 1}. **${patient.first_name} ${patient.last_name}** (${patient.patient_number})\n`;
              responseContent += `   📅 DOB: ${patient.date_of_birth} | 📞 ${patient.phone || 'No phone'}\n`;
              if (patient.email) responseContent += `   📧 ${patient.email}\n`;
              responseContent += `\n`;
            });
            if (result.patients.length > 10) {
              responseContent += `... and ${result.patients.length - 10} more patients\n`;
            }
          } else if (result.departments) {
            // Department list
            responseContent += `**Found ${result.departments.length} departments:**\n\n`;
            result.departments.forEach((dept, index) => {
              responseContent += `${index + 1}. **${dept.name}**\n`;
              if (dept.description) responseContent += `   📝 ${dept.description}\n`;
              if (dept.floor_number) responseContent += `   🏢 Floor: ${dept.floor_number}\n`;
              responseContent += `\n`;
            });
          } else if (result.beds) {
            // Bed list
            responseContent += `**Found bed information:**\n\n`;
            const bedGroups = {};
            result.beds.forEach(bed => {
              const status = bed.status || 'unknown';
              if (!bedGroups[status]) bedGroups[status] = [];
              bedGroups[status].push(bed);
            });
            
            Object.keys(bedGroups).forEach(status => {
              responseContent += `**${status.toUpperCase()} BEDS (${bedGroups[status].length}):**\n`;
              bedGroups[status].slice(0, 5).forEach(bed => {
                responseContent += `• ${bed.bed_number} (Room: ${bed.room_number || 'N/A'})\n`;
              });
              if (bedGroups[status].length > 5) {
                responseContent += `  ... and ${bedGroups[status].length - 5} more\n`;
              }
              responseContent += `\n`;
            });
          } else if (result.rooms) {
            // Room list
            responseContent += `**Found ${result.rooms.length} rooms:**\n\n`;
            result.rooms.forEach((room, index) => {
              responseContent += `${index + 1}. **Room ${room.room_number}**\n`;
              if (room.room_type) responseContent += `   🏠 Type: ${room.room_type}\n`;
              if (room.capacity) responseContent += `   👥 Capacity: ${room.capacity}\n`;
              responseContent += `\n`;
            });
          } else if (result.staff) {
            // Staff list
            responseContent += `**Found staff information:**\n\n`;
            result.staff.slice(0, 10).forEach((staff, index) => {
              responseContent += `${index + 1}. **${staff.user?.first_name || 'N/A'} ${staff.user?.last_name || ''}**\n`;
              if (staff.position) responseContent += `   💼 Position: ${staff.position}\n`;
              if (staff.department_name) responseContent += `   🏢 Department: ${staff.department_name}\n`;
              responseContent += `\n`;
            });
          } else {
            // Generic result
            responseContent += `**Operation Result:**\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\`\n`;
          }
        }
        
        responseContent += `\n🎉 **This was a real database operation!** All changes have been permanently saved.`;
      } else {
        // Handle errors
        responseContent = `❌ **Operation Failed**\n\n`;
        responseContent += `**Error:** ${mcpResult.message || mcpResult.error || 'Unknown error'}\n\n`;
        responseContent += `Please check your input and try again. For patient creation, ensure you provide:\n`;
        responseContent += `• Full name\n• Date of birth (YYYY-MM-DD format)\n• Other optional details`;
      }

      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        type: mcpResult.success ? 'success' : 'error'
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('💥 Error in message handling:', error);
      
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: `❌ **System Error**\n\n${error.message}\n\nPlease check the MCP server connection and try again.`,
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

  const quickActions = [
    { label: '👥 List Patients', action: 'List all patients' },
    { label: '🏨 List Departments', action: 'List all departments' },
    { label: '🛏️ List Beds', action: 'List all beds' },
    { label: '👨‍⚕️ List Staff', action: 'List all staff' },
    { label: '🏠 List Rooms', action: 'List all rooms' }
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

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Hospital Management System</h1>
            <p className="text-sm text-gray-600">Direct MCP Connection</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium text-gray-700">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white border-b border-gray-200 p-3">
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleSendMessage(action.action)}
              disabled={isLoading || !isConnected}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-3xl ${message.role === 'user' ? 'ml-auto' : 'mr-auto'}`}
          >
            <div
              className={`p-4 rounded-lg border ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white border-blue-500'
                  : getMessageStyle(message.type)
              }`}
            >
              <div className="prose prose-sm max-w-none">
                {message.content.split('\n').map((line, index) => (
                  <div key={index}>
                    {line.startsWith('**') && line.endsWith('**') ? (
                      <strong>{line.slice(2, -2)}</strong>
                    ) : line.startsWith('• ') ? (
                      <div className="ml-4">• {line.slice(2)}</div>
                    ) : line.startsWith('✅') || line.startsWith('❌') || line.startsWith('🏥') ? (
                      <div className="font-medium">{line}</div>
                    ) : (
                      <div>{line || <br />}</div>
                    )}
                  </div>
                ))}
              </div>
              <div className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="max-w-3xl mr-auto">
            <div className="p-4 rounded-lg border border-gray-200 bg-white">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-gray-600">Processing MCP request...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type your hospital management request..." : "Connecting to MCP server..."}
            disabled={isLoading || !isConnected}
            className="flex-1 resize-none p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            rows="2"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim() || !isConnected}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Example: "Create patient with full name: John Smith, date of birth: 1985-03-15, phone: 555-0123"
        </div>
      </div>
    </div>
  );
};

export default SimpleChatbot;
