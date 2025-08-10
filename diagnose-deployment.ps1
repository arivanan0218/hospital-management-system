# Deployment Diagnosis Script

Write-Host "=== Hospital Management System Deployment Diagnosis ===" -ForegroundColor Green
Write-Host ""

$PUBLIC_IP = "34.207.201.88"
$INSTANCE_ID = "i-0cf791e5c2873120e"

# 1. Check instance status
Write-Host "1. Instance Status:" -ForegroundColor Yellow
$instance_state = aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name' --output text
Write-Host "   Instance State: $instance_state" -ForegroundColor Green

# 2. Check basic connectivity
Write-Host ""
Write-Host "2. Network Connectivity:" -ForegroundColor Yellow
$ssh_test = Test-NetConnection -ComputerName $PUBLIC_IP -Port 22 -InformationLevel Quiet
if($ssh_test) {
    Write-Host "   ✅ SSH (Port 22): Reachable" -ForegroundColor Green
} else {
    Write-Host "   ❌ SSH (Port 22): Not reachable" -ForegroundColor Red
}

# 3. Check application ports
Write-Host ""
Write-Host "3. Application Ports:" -ForegroundColor Yellow

$backend_test = Test-NetConnection -ComputerName $PUBLIC_IP -Port 8000 -InformationLevel Quiet
if($backend_test) {
    Write-Host "   ✅ Backend (Port 8000): Open" -ForegroundColor Green
} else {
    Write-Host "   ❌ Backend (Port 8000): Closed or not responding" -ForegroundColor Red
}

$frontend_test = Test-NetConnection -ComputerName $PUBLIC_IP -Port 3000 -InformationLevel Quiet
if($frontend_test) {
    Write-Host "   ✅ Frontend (Port 3000): Open" -ForegroundColor Green
} else {
    Write-Host "   ❌ Frontend (Port 3000): Closed or not responding" -ForegroundColor Red
}

# 4. Test HTTP endpoints
Write-Host ""
Write-Host "4. HTTP Endpoints:" -ForegroundColor Yellow

try {
    $health_response = Invoke-WebRequest -Uri "http://$PUBLIC_IP:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Backend Health: SUCCESS (Status: $($health_response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend Health: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $frontend_response = Invoke-WebRequest -Uri "http://$PUBLIC_IP:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Frontend: SUCCESS (Status: $($frontend_response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Deployment timing
Write-Host ""
Write-Host "5. Deployment Information:" -ForegroundColor Yellow
$launch_time = aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].LaunchTime' --output text
Write-Host "   Instance launched: $launch_time"
$current_time = Get-Date
$launch_datetime = [DateTime]::Parse($launch_time)
$minutes_running = [math]::Round(($current_time - $launch_datetime).TotalMinutes, 1)
Write-Host "   Running for: $minutes_running minutes"

Write-Host ""
Write-Host "=== Diagnosis Summary ===" -ForegroundColor Cyan

if ($minutes_running -lt 5) {
    Write-Host "⏳ CONTAINERS LIKELY STILL STARTING" -ForegroundColor Yellow
    Write-Host "   Docker containers typically take 3-5 minutes to download and start."
    Write-Host "   Please wait a few more minutes and run this script again."
} elseif (-not $backend_test -or -not $frontend_test) {
    Write-Host "🔧 TROUBLESHOOTING NEEDED" -ForegroundColor Red
    Write-Host "   Containers may have failed to start. Debugging steps:"
    Write-Host "   1. SSH into the instance: ssh -i hospital-key.pem ec2-user@$PUBLIC_IP"
    Write-Host "   2. Check Docker status: sudo systemctl status docker"
    Write-Host "   3. Check containers: docker ps -a"
    Write-Host "   4. Check logs: docker logs hospital-backend && docker logs hospital-frontend"
} else {
    Write-Host "✅ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
    Write-Host "   Your Hospital Management System is running properly!"
}

Write-Host ""
Write-Host "Your Application URLs:" -ForegroundColor Green
Write-Host "- Frontend: http://$PUBLIC_IP:3000"
Write-Host "- Backend: http://$PUBLIC_IP:8000"
Write-Host "- Health Check: http://$PUBLIC_IP:8000/health"
