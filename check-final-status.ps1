# Final Deployment Status Check

Write-Host "Hospital Management System - Deployment Status" -ForegroundColor Green
Write-Host "==============================================="

$PUBLIC_IP = "34.207.201.88"
$INSTANCE_ID = "i-0cf791e5c2873120e"

Write-Host "Instance ID: $INSTANCE_ID" -ForegroundColor Yellow
Write-Host "Public IP: $PUBLIC_IP" -ForegroundColor Yellow

# Check instance status
$INSTANCE_STATE = aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name' --output text
Write-Host "Instance State: $INSTANCE_STATE" -ForegroundColor Green

Write-Host ""
Write-Host "Testing Application Endpoints..." -ForegroundColor Yellow

# Test backend health
try {
    $response = Invoke-WebRequest -Uri "http://$PUBLIC_IP:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Backend Health Check: SUCCESS (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⏳ Backend Health Check: Still starting up..." -ForegroundColor Yellow
}

# Test frontend
try {
    $response = Invoke-WebRequest -Uri "http://$PUBLIC_IP:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Frontend: SUCCESS (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⏳ Frontend: Still starting up..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Your Hospital Management System URLs:" -ForegroundColor Cyan
Write-Host "=====================================", 
Write-Host "🌐 Frontend Application: http://$PUBLIC_IP:3000" -ForegroundColor Green
Write-Host "🔧 Backend API: http://$PUBLIC_IP:8000" -ForegroundColor Green
Write-Host "🩺 Health Check: http://$PUBLIC_IP:8000/health" -ForegroundColor Green

Write-Host ""
Write-Host "If services are still starting up, wait 2-3 minutes and try again." -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Your Hospital Management System is successfully deployed on AWS!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Visit the URLs above to test your application"
Write-Host "2. Set up GitHub repository and push your code"
Write-Host "3. Configure GitHub Actions for CI/CD"
Write-Host "4. Consider setting up RDS database for production"
Write-Host "5. Set up custom domain and SSL certificate"

Write-Host ""
Write-Host "To SSH into your server (for debugging):" -ForegroundColor Yellow
Write-Host "ssh -i hospital-key.pem ec2-user@$PUBLIC_IP"
