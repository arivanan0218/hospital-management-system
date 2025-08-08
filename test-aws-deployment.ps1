# Test AWS MCP Deployment
Write-Host "Testing AWS Deployment..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Frontend accessibility
Write-Host "1. Testing Frontend..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com" -TimeoutSec 10 -UseBasicParsing
    Write-Host "Frontend Status: $($frontendResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: MCP Diagnostics
Write-Host ""
Write-Host "2. Testing MCP Diagnostics..." -ForegroundColor Yellow
try {
    $mcpResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/diagnose" -TimeoutSec 15
    Write-Host "MCP Diagnostics retrieved successfully" -ForegroundColor Green
    Write-Host "MCP Server Info:" -ForegroundColor Cyan
    Write-Host "   - Running: $($mcpResponse.mcpServerRunning)"
    Write-Host "   - Environment: $($mcpResponse.environment.AWS_EXECUTION_ENV -or 'Local')"
    Write-Host "   - Python Version: $($mcpResponse.environment.pythonVersion -or 'Unknown')"
    Write-Host "   - Database URL: $(if($mcpResponse.environment.databaseUrl) {'Set'} else {'Not Set'})"
    Write-Host "   - UV Available: $($mcpResponse.environment.uvAvailable)"
} catch {
    Write-Host "MCP Diagnostics Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: MCP Status
Write-Host ""
Write-Host "3. Testing MCP Status..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status" -TimeoutSec 10
    Write-Host "MCP Status retrieved successfully" -ForegroundColor Green
    Write-Host "   - Connected: $($statusResponse.isConnected)"
    Write-Host "   - Tool Count: $($statusResponse.toolCount)"
    Write-Host "   - Server Running: $($statusResponse.mcpServerRunning)"
    
    $global:mcpConnected = $statusResponse.isConnected
    $global:toolCount = $statusResponse.toolCount
} catch {
    Write-Host "MCP Status Error: $($_.Exception.Message)" -ForegroundColor Red
    $global:mcpConnected = $false
    $global:toolCount = 0
}

# Test 4: MCP Start (if not running)
if (-not $global:mcpConnected -or $global:toolCount -eq 0) {
    Write-Host ""
    Write-Host "4. Testing MCP Start..." -ForegroundColor Yellow
    try {
        $startResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/start" -Method POST -TimeoutSec 30
        Write-Host "MCP Start request sent successfully" -ForegroundColor Green
        Write-Host "   - Success: $($startResponse.success)"
        Write-Host "   - Message: $($startResponse.message)"
        
        if ($startResponse.success) {
            Write-Host ""
            Write-Host "Waiting for MCP server to initialize..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            $finalStatusResponse = Invoke-RestMethod -Uri "http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com:3001/mcp/status" -TimeoutSec 10
            Write-Host ""
            Write-Host "Final MCP Status:" -ForegroundColor Cyan
            Write-Host "   - Connected: $($finalStatusResponse.isConnected)"
            Write-Host "   - Tool Count: $($finalStatusResponse.toolCount)"
            Write-Host "   - Server Running: $($finalStatusResponse.mcpServerRunning)"
            
            if ($finalStatusResponse.isConnected -and $finalStatusResponse.toolCount -gt 0) {
                Write-Host ""
                Write-Host "SUCCESS! MCP Server is fully operational with tools available!" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "MCP Server started but not fully connected. Check logs for database issues." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "MCP Start Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "MCP Server is already connected with $global:toolCount tools!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Test Complete!" -ForegroundColor Cyan
