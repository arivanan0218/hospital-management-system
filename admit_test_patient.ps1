# Admit a test patient for assignment testing
$patientData = @{
    name = "Ahmed Hassan"
    age = 28
    gender = "Male"
    contact_number = "+971-555-0123"
    email = "ahmed.hassan@email.com"
    emergency_contact = "Fatima Hassan: +971-555-0124"
    medical_history = "No significant medical history"
    admission_reason = "Chest pain evaluation"
    assigned_doctor = "Dr. Smith"
}

$payload = @{
    name = "create_patient"
    arguments = $patientData
} | ConvertTo-Json -Depth 3

Write-Host "=== ADMITTING PATIENT AHMED HASSAN ===" -ForegroundColor Green

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/tools/call" -Method POST -Body $payload -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "Response received:" -ForegroundColor Yellow
    $result | ConvertTo-Json -Depth 3 | Write-Host
    
    if ($result.result.success -eq $true) {
        $patientId = $result.result.data.id
        Write-Host ""
        Write-Host "Patient Ahmed Hassan admitted successfully!" -ForegroundColor Green
        Write-Host "Patient ID: $patientId" -ForegroundColor Cyan
        Write-Host "Patient Name: Ahmed Hassan" -ForegroundColor Cyan
        Write-Host "Email: ahmed.hassan@email.com" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Ready for frontend assignment testing!" -ForegroundColor Magenta
        Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Yellow
    } else {
        Write-Host "Failed to admit patient" -ForegroundColor Red
        Write-Host "Error details: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
