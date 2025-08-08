# Simple MCP Test
Write-Host "Testing MCP Server Status..." -ForegroundColor Cyan

try {
    Write-Host "Checking MCP server status..." -ForegroundColor Yellow
    $statusResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status" -TimeoutSec 10
    Write-Host "Connected: $($statusResponse.isConnected)" -ForegroundColor $(if($statusResponse.isConnected) {'Green'} else {'Red'})
    Write-Host "Tool Count: $($statusResponse.toolCount)" -ForegroundColor $(if($statusResponse.toolCount -gt 0) {'Green'} else {'Red'})
    Write-Host "Server Running: $($statusResponse.mcpServerRunning)" -ForegroundColor $(if($statusResponse.mcpServerRunning) {'Green'} else {'Red'})
} catch {
    Write-Host "Error getting status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTrying to start MCP server..." -ForegroundColor Yellow
try {
    $startResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/start" -Method POST -TimeoutSec 30
    Write-Host "Start Success: $($startResponse.success)" -ForegroundColor $(if($startResponse.success) {'Green'} else {'Red'})
    Write-Host "Message: $($startResponse.message)" -ForegroundColor Cyan
} catch {
    Write-Host "Error starting: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nFinal status check..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $finalResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status" -TimeoutSec 10
    Write-Host "Final Connected: $($finalResponse.isConnected)" -ForegroundColor $(if($finalResponse.isConnected) {'Green'} else {'Red'})
    Write-Host "Final Tool Count: $($finalResponse.toolCount)" -ForegroundColor $(if($finalResponse.toolCount -gt 0) {'Green'} else {'Red'})
} catch {
    Write-Host "Error getting final status: $($_.Exception.Message)" -ForegroundColor Red
}
