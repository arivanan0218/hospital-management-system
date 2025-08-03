import React, { useState } from 'react';
import UniversalMCPChatbot from './components/UniversalMCPChatbot';
import DirectMCPChatbot from './components/DirectMCPChatbot';
import './App.css';

function App() {
  const [chatbotMode, setChatbotMode] = useState('direct'); // 'universal' or 'direct'

  return (
    <div className="App">
      {/* Mode Selector */}
      <div className="fixed top-4 right-4 z-50">
        <div className="bg-white rounded-lg shadow-lg p-3 border">
          <div className="text-sm font-medium text-gray-700 mb-2">Chatbot Mode:</div>
          <div className="flex space-x-2">
            <button
              onClick={() => setChatbotMode('direct')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                chatbotMode === 'direct'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🚀 Direct MCP
            </button>
            <button
              onClick={() => setChatbotMode('universal')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                chatbotMode === 'universal'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🌐 Universal MCP
            </button>
          </div>
        </div>
      </div>

      {/* Render selected chatbot */}
      {chatbotMode === 'direct' ? <DirectMCPChatbot /> : <UniversalMCPChatbot />}
    </div>
  );
}

export default App;
