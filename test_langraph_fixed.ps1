# LangChain/LangGraph Integration Test Execution Script
# This script starts the server and runs comprehensive tests

Write-Host "🚀 Starting LangChain/LangGraph Integration Testing" -ForegroundColor Green
Write-Host "============================================================"

# Ensure we're in the correct directory
Set-Location "e:\Rise Ai\hospital-management-system"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "⚠️ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Install/update dependencies
Write-Host "📦 Installing/updating dependencies..." -ForegroundColor Cyan
Set-Location "backend-python"
pip install -e .

# Check if server is already running
Write-Host "🔍 Checking if server is running..." -ForegroundColor Cyan
$serverAlreadyRunning = $false
try {
    Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop | Out-Null
    Write-Host "✅ Server is already running" -ForegroundColor Green
    $serverAlreadyRunning = $true
} catch {
    Write-Host "ℹ️ Server not running, will start it" -ForegroundColor Yellow
    $serverAlreadyRunning = $false
}

# Start server if not running
$serverJob = $null
if (-not $serverAlreadyRunning) {
    Write-Host "🚀 Starting Multi-Agent Server..." -ForegroundColor Cyan
    
    # Start server in background
    $serverJob = Start-Job -ScriptBlock {
        Set-Location "e:\Rise Ai\hospital-management-system\backend-python"
        & "..\venv\Scripts\python.exe" multi_agent_server.py
    }
    
    Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check if server started successfully
    $attempts = 0
    $maxAttempts = 12
    $serverReady = $false
    
    while ($attempts -lt $maxAttempts -and -not $serverReady) {
        $attempts++
        try {
            Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop | Out-Null
            $serverReady = $true
            Write-Host "✅ Server is ready!" -ForegroundColor Green
        } catch {
            Write-Host "⏳ Attempt $attempts/$maxAttempts - Waiting for server..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
    
    if (-not $serverReady) {
        Write-Host "❌ Failed to start server after $maxAttempts attempts" -ForegroundColor Red
        if ($serverJob) {
            Stop-Job $serverJob
            Remove-Job $serverJob
        }
        exit 1
    }
}

# Run the integration tests
Write-Host ""
Write-Host "🧪 Running LangChain/LangGraph Integration Tests..." -ForegroundColor Cyan
Write-Host "============================================================"

$testExitCode = 0
try {
    python test_langraph_integration.py
    $testExitCode = $LASTEXITCODE
} catch {
    Write-Host "❌ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    $testExitCode = 1
}

# Clean up if we started the server
if (-not $serverAlreadyRunning -and $serverJob) {
    Write-Host ""
    Write-Host "🧹 Cleaning up server process..." -ForegroundColor Cyan
    Stop-Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job $serverJob -ErrorAction SilentlyContinue
}

# Display results
Write-Host ""
Write-Host "============================================================"
if ($testExitCode -eq 0) {
    Write-Host "🎉 LangChain/LangGraph Integration Tests PASSED!" -ForegroundColor Green
    Write-Host "✅ Your enhanced hospital management system is ready!" -ForegroundColor Green
} else {
    Write-Host "❌ LangChain/LangGraph Integration Tests FAILED!" -ForegroundColor Red
    Write-Host "ℹ️ Check the test results for details" -ForegroundColor Yellow
}

# Show next steps
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review test results in: langraph_integration_test_results.json"
Write-Host "2. If tests passed, your LangChain/LangGraph integration is ready!"
Write-Host "3. Start using enhanced AI workflows in your hospital system"
Write-Host "4. Monitor the system logs for any issues"

# Check if results file exists and show summary
if (Test-Path "langraph_integration_test_results.json") {
    Write-Host ""
    Write-Host "📊 Test Results Summary:" -ForegroundColor Cyan
    try {
        $results = Get-Content "langraph_integration_test_results.json" | ConvertFrom-Json
        Write-Host "Total Tests: $($results.total_tests)"
        Write-Host "Passed Tests: $($results.passed_tests)"
        $successRate = [math]::Round($results.success_rate * 100, 1)
        Write-Host "Success Rate: $successRate%"
        
        if ($results.summary.langraph_integration) {
            Write-Host "✅ LangGraph Workflows: Working" -ForegroundColor Green
        } else {
            Write-Host "❌ LangGraph Workflows: Issues" -ForegroundColor Red
        }
        
        if ($results.summary.enhanced_ai_available) {
            Write-Host "✅ Enhanced AI Features: Available" -ForegroundColor Green
        } else {
            Write-Host "❌ Enhanced AI Features: Not available" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "⚠️ Could not parse test results file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🏥 Your Hospital Management System with LangChain/LangGraph is ready!" -ForegroundColor Green

exit $testExitCode
