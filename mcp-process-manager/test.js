/**
 * Test script for MCP Process Manager
 */

const BASE_URL = 'http://localhost:3001';

async function testProcessManager() {
  console.log('🧪 Testing MCP Process Manager...');
  
  try {
    // Test 1: Check status
    console.log('\n1. Testing status endpoint...');
    const statusResponse = await fetch(`${BASE_URL}/mcp/status`);
    const statusData = await statusResponse.json();
    console.log('✅ Status:', statusData);
    
    // Test 2: Start MCP server
    console.log('\n2. Testing MCP server start...');
    const startResponse = await fetch(`${BASE_URL}/mcp/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        command: 'python',
        args: ['-m', 'backend_python.comprehensive_server'],
        env: {
          'PYTHONPATH': 'c:\\Users\\Arivanan\\hospital-management-system\\backend-python'
        }
      })
    });
    
    const startData = await startResponse.json();
    console.log('📊 Start result:', startData);
    
    if (startData.success) {
      console.log('✅ MCP server started successfully!');
      
      // Wait a moment for initialization
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Test 3: Get tools
      console.log('\n3. Testing tools endpoint...');
      const toolsResponse = await fetch(`${BASE_URL}/mcp/tools`);
      const toolsData = await toolsResponse.json();
      console.log('🔧 Tools:', toolsData);
      
      // Test 4: Call a tool
      if (toolsData.success && toolsData.tools.length > 0) {
        console.log('\n4. Testing tool call...');
        const callResponse = await fetch(`${BASE_URL}/mcp/call`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            toolName: 'list_patients',
            args: {}
          })
        });
        
        const callData = await callResponse.json();
        console.log('📞 Tool call result:', callData);
      }
      
      // Test 5: Stop server
      console.log('\n5. Testing stop endpoint...');
      const stopResponse = await fetch(`${BASE_URL}/mcp/stop`, {
        method: 'POST'
      });
      const stopData = await stopResponse.json();
      console.log('🛑 Stop result:', stopData);
      
    } else {
      console.error('❌ Failed to start MCP server:', startData.error);
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Run in browser console or Node.js
if (typeof window !== 'undefined') {
  // Browser environment
  window.testProcessManager = testProcessManager;
  console.log('Run testProcessManager() in the console to test');
} else {
  // Node.js environment
  testProcessManager();
}
