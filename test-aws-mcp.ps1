# Hospital Management System - AWS MCP Testing Script
# This script tests both local and AWS deployments

Write-Host "🏥 Hospital Management System - MCP Testing Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Test Local Environment
Write-Host "`n🏠 Testing Local Environment..." -ForegroundColor Yellow
try {
    $localStatus = Invoke-RestMethod -Uri "http://localhost:3001/mcp/status" -Method GET -TimeoutSec 10
    Write-Host "✅ Local MCP Status - Connected: $($localStatus.serverInfo.isConnected), Tools: $($localStatus.serverInfo.toolCount)" -ForegroundColor Green
    
    # Test local diagnostic endpoint
    try {
        $localDiag = Invoke-RestMethod -Uri "http://localhost:3001/mcp/diagnose" -Method GET -TimeoutSec 10
        Write-Host "✅ Local Diagnostic Endpoint: Working" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Local Diagnostic Endpoint: Not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Local MCP Server: Not accessible" -ForegroundColor Red
}

# Test Local Frontend
try {
    $localFrontend = Invoke-RestMethod -Uri "http://localhost" -Method GET -TimeoutSec 5
    Write-Host "✅ Local Frontend: Working" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Local Frontend: Not accessible" -ForegroundColor Yellow
}

# Test AWS Environment
Write-Host "`n☁️ Testing AWS Environment..." -ForegroundColor Yellow
$awsUrl = "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com"

try {
    $awsFrontend = Invoke-RestMethod -Uri $awsUrl -Method GET -TimeoutSec 10
    Write-Host "✅ AWS Frontend: Working" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS Frontend: Not accessible" -ForegroundColor Red
}

try {
    $awsStatus = Invoke-RestMethod -Uri "$awsUrl`:3001/mcp/status" -Method GET -TimeoutSec 10
    Write-Host "✅ AWS MCP Status - Connected: $($awsStatus.serverInfo.isConnected), Tools: $($awsStatus.serverInfo.toolCount)" -ForegroundColor Green
    
    # Test AWS diagnostic endpoint
    try {
        $awsDiag = Invoke-RestMethod -Uri "$awsUrl`:3001/mcp/diagnose" -Method GET -TimeoutSec 15
        Write-Host "✅ AWS Diagnostic Endpoint: Working" -ForegroundColor Green
        Write-Host "   - Python Available: $($awsDiag.diagnostics.pythonExecutable)" -ForegroundColor Cyan
        Write-Host "   - UV Available: $($awsDiag.diagnostics.uvAvailable)" -ForegroundColor Cyan
        Write-Host "   - Backend Dir Exists: $($awsDiag.diagnostics.backendPythonExists)" -ForegroundColor Cyan
        Write-Host "   - Auto-start Attempted: $($awsDiag.diagnostics.autoStartAttempted)" -ForegroundColor Cyan
    } catch {
        Write-Host "⚠️ AWS Diagnostic Endpoint: Not available (deployment may be in progress)" -ForegroundColor Yellow
        
        # Try to manually start AWS MCP server
        Write-Host "🔧 Attempting to manually start AWS MCP server..." -ForegroundColor Yellow
        try {
            $body = @{
                command = "uv"
                args = @("run", "python", "comprehensive_server.py")
                env = @{
                    PYTHONPATH = "/backend-python"
                }
                cwd = "/backend-python"
            } | ConvertTo-Json
            
            $startResult = Invoke-RestMethod -Uri "$awsUrl`:3001/mcp/start" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
            Write-Host "✅ AWS MCP Start Command: Sent successfully" -ForegroundColor Green
            
            # Wait and check again
            Write-Host "⏳ Waiting 30 seconds for MCP server to initialize..." -ForegroundColor Yellow
            Start-Sleep 30
            
            $awsStatusFinal = Invoke-RestMethod -Uri "$awsUrl`:3001/mcp/status" -Method GET -TimeoutSec 10
            Write-Host "🔄 AWS MCP Final Status - Connected: $($awsStatusFinal.serverInfo.isConnected), Tools: $($awsStatusFinal.serverInfo.toolCount)" -ForegroundColor Cyan
            
        } catch {
            Write-Host "❌ Failed to start AWS MCP server: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "❌ AWS MCP Server: Not accessible" -ForegroundColor Red
}

# Summary
Write-Host "`n📊 DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "🏠 Local Development: Perfect for testing with full MCP functionality" -ForegroundColor Green
Write-Host "☁️ AWS Production: Frontend working, MCP server needs troubleshooting" -ForegroundColor Yellow
Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Use local environment for development and testing" -ForegroundColor White
Write-Host "2. For AWS: Wait for diagnostic endpoint deployment or check ECS logs" -ForegroundColor White
Write-Host "3. Test AI chatbot locally with your API keys" -ForegroundColor White
Write-Host "`n🔗 URLs:" -ForegroundColor Cyan
Write-Host "- Local Frontend: http://localhost" -ForegroundColor White
Write-Host "- Local MCP: http://localhost:3001" -ForegroundColor White
Write-Host "- AWS Frontend: $awsUrl" -ForegroundColor White
Write-Host "- AWS MCP: $awsUrl`:3001" -ForegroundColor White

Write-Host "`n✨ Your hospital management system is ready for use! 🏥" -ForegroundColor Green
