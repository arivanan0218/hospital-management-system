import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import UniversalAIMCPService from '../services/universalAiMcpService';

const UniversalMCPChatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      role: 'assistant',
      content: '🤖 **Universal MCP Assistant**\n\nI\'m a Claude Desktop-like assistant that can connect to any MCP server! \n\n**Features:**\n• 🧠 OpenAI GPT-4 powered natural language understanding\n• 🔗 Connect to any MCP server\n• 🛠️ Automatically discover available tools\n• 💬 Natural conversation interface\n\n**Setup:**\n1. Enter your OpenAI API key\n2. Configure your MCP server URL\n3. Start chatting naturally!\n\nI\'ll understand your requests and call the right MCP tools for you! 🚀',
      timestamp: new Date(),
      type: 'assistant'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiService] = useState(new UniversalAIMCPService());
  const [isConnected, setIsConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(true);
  
  // Configuration state
  const [config, setConfig] = useState({
    openaiApiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
    mcpServerUrl: 'http://localhost:8080',
    mcpServerHeaders: '{}'
  });
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-connect if config is available
  useEffect(() => {
    if (config.openaiApiKey && config.mcpServerUrl && !showSetup) {
      connectToServices();
    }
  }, [config.openaiApiKey, config.mcpServerUrl, showSetup]); // eslint-disable-line react-hooks/exhaustive-deps

  const connectToServices = async () => {
    if (!config.openaiApiKey.trim() || !config.mcpServerUrl.trim()) {
      alert('Please provide both OpenAI API key and MCP server URL');
      return;
    }

    try {
      setIsLoading(true);
      
      // Parse headers
      let headers = {};
      try {
        if (config.mcpServerHeaders.trim()) {
          headers = JSON.parse(config.mcpServerHeaders);
        }
      } catch (parseError) {
        console.warn('Invalid headers JSON, using empty headers:', parseError);
      }

      const mcpServerConfig = {
        url: config.mcpServerUrl.trim(),
        headers: headers
      };

      const connected = await aiService.initialize(config.openaiApiKey.trim(), mcpServerConfig);
      
      if (connected) {
        setIsConnected(true);
        setShowSetup(false);
        
        const serverInfo = aiService.getServerInfo();
        const welcomeMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: `✅ **Connected Successfully!**\n\n🧠 **AI:** OpenAI GPT-4 ready\n🔗 **MCP Server:** ${serverInfo.url}\n🛠️ **Available Tools:** ${serverInfo.toolCount}\n\n**Discovered Tools:**\n${serverInfo.tools.map(tool => `• ${tool}`).join('\n')}\n\nYou can now chat naturally and I'll call the appropriate MCP tools for you! 🎉`,
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
        content: `❌ **Connection Failed**\n\n**Error:** ${error.message}\n\n**Please check:**\n• OpenAI API key is valid\n• MCP server is running and accessible\n• MCP server URL is correct\n• Server headers are valid JSON`,
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
      alert('Please connect to MCP server first');
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
      
      const aiResult = await aiService.processRequest(textToSend);
      
      let responseContent;
      
      if (aiResult.success) {
        const aiMessage = aiResult.message || "I've processed your request.";
        responseContent = aiMessage + '\n\n';
        
        if (aiResult.functionCalls && aiResult.functionCalls.length > 0) {
          responseContent += '🔧 **MCP Operations Performed:**\n\n';
          
          aiResult.functionCalls.forEach((call, index) => {
            if (call.success) {
              responseContent += `${index + 1}. ✅ **${call.function.toUpperCase()}**\n`;
              
              // Display result based on structure
              if (call.result) {
                if (call.result.result) {
                  responseContent += formatMCPResult(call.result.result);
                } else if (call.result.data) {
                  responseContent += formatMCPResult(call.result.data);
                } else {
                  responseContent += `   📊 **Result:** \`\`\`json\n${JSON.stringify(call.result, null, 2)}\n\`\`\`\n`;
                }
              }
              
              responseContent += '\n';
            } else {
              responseContent += `${index + 1}. ❌ **${call.function.toUpperCase()} FAILED**\n`;
              responseContent += `   **Error:** ${call.error}\n\n`;
            }
          });
          
          responseContent += '🎉 **All operations completed via MCP server!**';
        }
      } else {
        responseContent = `❌ **Processing Failed**\n\n${aiResult.message || aiResult.error}`;
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
        content: `❌ **System Error**\n\n${error.message}\n\nPlease check your connections and try again.`,
        timestamp: new Date(),
        type: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Format MCP results intelligently
  const formatMCPResult = (result) => {
    if (typeof result === 'string') {
      return `   📝 **Result:** ${result}\n`;
    }
    
    if (Array.isArray(result)) {
      return `   📊 **Found ${result.length} items**\n   ${result.slice(0, 5).map((item, i) => `${i+1}. ${typeof item === 'object' ? JSON.stringify(item) : item}`).join('\n   ')}${result.length > 5 ? '\n   ... and more' : ''}\n`;
    }
    
    if (typeof result === 'object' && result !== null) {
      let formatted = '   📋 **Details:**\n';
      Object.keys(result).slice(0, 10).forEach(key => {
        const value = result[key];
        if (typeof value === 'object') {
          formatted += `   • ${key}: ${JSON.stringify(value)}\n`;
        } else {
          formatted += `   • ${key}: ${value}\n`;
        }
      });
      return formatted;
    }
    
    return `   📊 **Result:** ${result}\n`;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleConfigSubmit = () => {
    connectToServices();
  };

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

  if (showSetup) {
    return (
      <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50 p-6">
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-lg border w-full max-w-2xl">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">🤖 Universal MCP Assistant</h2>
              <p className="text-gray-600">Connect to any MCP server with Claude Desktop-like experience</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key *
                </label>
                <input
                  type="password"
                  value={config.openaiApiKey}
                  onChange={(e) => setConfig(prev => ({...prev, openaiApiKey: e.target.value}))}
                  placeholder="sk-..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  MCP Server URL *
                </label>
                <input
                  type="url"
                  value={config.mcpServerUrl}
                  onChange={(e) => setConfig(prev => ({...prev, mcpServerUrl: e.target.value}))}
                  placeholder="http://localhost:8080"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Server Headers (JSON, optional)
                </label>
                <textarea
                  value={config.mcpServerHeaders}
                  onChange={(e) => setConfig(prev => ({...prev, mcpServerHeaders: e.target.value}))}
                  placeholder='{"Authorization": "Bearer token", "Custom-Header": "value"}'
                  rows="3"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <button
                onClick={handleConfigSubmit}
                disabled={isLoading || !config.openaiApiKey.trim() || !config.mcpServerUrl.trim()}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Connecting...
                  </>
                ) : (
                  'Connect to MCP Server'
                )}
              </button>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-800 mb-2">💡 Examples of MCP Servers</h3>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• Hospital Management: http://localhost:8080</li>
                  <li>• File System: http://localhost:3000</li>
                  <li>• Database: http://localhost:5000</li>
                  <li>• Custom MCP Server: http://your-server.com</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">🔒 Privacy & Security</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Credentials stored only in browser memory</li>
                <li>• Direct connection to your MCP server</li>
                <li>• No data sent to third parties</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-800">🤖 Universal MCP Assistant</h1>
            <p className="text-sm text-gray-600">Connected to: {aiService.getServerInfo()?.url}</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button
              onClick={() => setShowSetup(true)}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded border"
            >
              ⚙️ Settings
            </button>
          </div>
        </div>
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
                  ) : line.includes('```') ? (
                    <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                      {line.replace(/```\w*\n?|```/g, '')}
                    </pre>
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
              <span className="text-blue-800">AI is processing your request...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Chat naturally with your MCP server..."
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

export default UniversalMCPChatbot;
