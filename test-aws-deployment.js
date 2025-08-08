// Test AWS MCP Deployment
const fetch = require('node-fetch');

async function testAWSDeployment() {
    console.log('🧪 Testing AWS Deployment...\n');
    
    // Test 1: Frontend accessibility
    try {
        console.log('1️⃣ Testing Frontend...');
        const frontendResponse = await fetch('http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com', {
            timeout: 10000
        });
        console.log(`✅ Frontend Status: ${frontendResponse.status}`);
    } catch (error) {
        console.log(`❌ Frontend Error: ${error.message}`);
    }
    
    // Test 2: MCP Diagnostics
    try {
        console.log('\n2️⃣ Testing MCP Diagnostics...');
        const mcpResponse = await fetch('http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/diagnose', {
            timeout: 15000
        });
        const mcpData = await mcpResponse.json();
        console.log(`✅ MCP Diagnostics Status: ${mcpResponse.status}`);
        console.log('📊 MCP Server Info:');
        console.log(`   - Running: ${mcpData.mcpServerRunning}`);
        console.log(`   - Environment: ${mcpData.environment?.AWS_EXECUTION_ENV || 'Local'}`);
        console.log(`   - Python Version: ${mcpData.environment?.pythonVersion || 'Unknown'}`);
        console.log(`   - Database URL: ${mcpData.environment?.databaseUrl ? 'Set' : 'Not Set'}`);
        console.log(`   - UV Available: ${mcpData.environment?.uvAvailable}`);
    } catch (error) {
        console.log(`❌ MCP Diagnostics Error: ${error.message}`);
    }
    
    // Test 3: MCP Status
    try {
        console.log('\n3️⃣ Testing MCP Status...');
        const statusResponse = await fetch('http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status', {
            timeout: 10000
        });
        const statusData = await statusResponse.json();
        console.log(`✅ MCP Status: ${statusResponse.status}`);
        console.log(`   - Connected: ${statusData.isConnected}`);
        console.log(`   - Tool Count: ${statusData.toolCount}`);
        console.log(`   - Server Running: ${statusData.mcpServerRunning}`);
    } catch (error) {
        console.log(`❌ MCP Status Error: ${error.message}`);
    }
    
    // Test 4: MCP Start (if not running)
    try {
        console.log('\n4️⃣ Testing MCP Start...');
        const startResponse = await fetch('http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/start', {
            method: 'POST',
            timeout: 30000
        });
        const startData = await startResponse.json();
        console.log(`✅ MCP Start Status: ${startResponse.status}`);
        console.log(`   - Success: ${startData.success}`);
        console.log(`   - Message: ${startData.message}`);
        
        if (startData.success) {
            // Wait a moment and test status again
            console.log('\n⏳ Waiting for MCP server to initialize...');
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            const finalStatusResponse = await fetch('http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status', {
                timeout: 10000
            });
            const finalStatusData = await finalStatusResponse.json();
            console.log('\n🔄 Final MCP Status:');
            console.log(`   - Connected: ${finalStatusData.isConnected}`);
            console.log(`   - Tool Count: ${finalStatusData.toolCount}`);
            console.log(`   - Server Running: ${finalStatusData.mcpServerRunning}`);
            
            if (finalStatusData.isConnected && finalStatusData.toolCount > 0) {
                console.log('\n🎉 SUCCESS! MCP Server is fully operational with tools available!');
            } else {
                console.log('\n⚠️ MCP Server started but not fully connected. Check logs for database issues.');
            }
        }
    } catch (error) {
        console.log(`❌ MCP Start Error: ${error.message}`);
    }
    
    console.log('\n📋 Test Complete!');
}

// Run the test
testAWSDeployment().catch(console.error);
