// Quick test for Claude API connection
// Note: Make sure to set your API key in the .env file as VITE_CLAUDE_API_KEY
// For testing, replace "your_api_key_here" with your actual API key temporarily
const CLAUDE_API_KEY = "your_api_key_here";

async function testClaudeAPI() {
    try {
        console.log('🧪 Testing Claude API connection...');
        
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 100,
                messages: [{
                    role: 'user',
                    content: 'Hello, are you working?'
                }]
            })
        });

        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error:', errorText);
            return false;
        }

        const data = await response.json();
        console.log('✅ Claude API working! Response:', data);
        return true;

    } catch (error) {
        console.error('❌ Network Error:', error);
        return false;
    }
}

// Run test
testClaudeAPI().then(success => {
    console.log(success ? '✅ Claude API is working!' : '❌ Claude API test failed');
});
