# Create a new patient for assignment testing
$patientData = @{
    first_name = "Sarah"
    last_name = "Johnson"
    date_of_birth = "1992-08-15"
    age = 32
    gender = "Female"
    contact_number = "+971-555-9876"
    email = "sarah.johnson@email.com"
    emergency_contact = "John Johnson: +971-555-9877"
    medical_history = "Asthma, no other significant history"
    admission_reason = "Respiratory evaluation"
}

# Use the correct JSON-RPC 2.0 format for tools/call endpoint
$payload = @{
    jsonrpc = "2.0"
    id = 1
    method = "tools/call"
    params = @{
        name = "create_patient"
        arguments = $patientData
    }
} | ConvertTo-Json -Depth 4

Write-Host "=== CREATING NEW PATIENT: SARAH JOHNSON ===" -ForegroundColor Green
Write-Host "Payload: $payload" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/tools/call" -Method POST -Body $payload -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "`nResponse received:" -ForegroundColor Yellow
    $result | ConvertTo-Json -Depth 3 | Write-Host
    
    if ($result.result -and $result.result.success -eq $true) {
        $patientId = $result.result.data.id
        Write-Host ""
        Write-Host "Patient Sarah Johnson created successfully!" -ForegroundColor Green
        Write-Host "Patient ID: $patientId" -ForegroundColor Cyan
        Write-Host "Patient Name: Sarah Johnson" -ForegroundColor Cyan
        Write-Host "Email: sarah.johnson@email.com" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Ready for frontend assignment testing!" -ForegroundColor Magenta
        Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Test Commands:" -ForegroundColor White
        Write-Host "  1. find patient Sarah Johnson" -ForegroundColor Gray
        Write-Host "  2. assign bed 301A to patient Sarah Johnson" -ForegroundColor Gray
        Write-Host "  3. assign equipment X-Ray to patient Sarah Johnson" -ForegroundColor Gray
        Write-Host "  4. assign nurse Sarah to patient Sarah Johnson" -ForegroundColor Gray
        Write-Host "  5. assign supply bandages to patient Sarah Johnson" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "Failed to create patient" -ForegroundColor Red
        if ($result.error) {
            Write-Host "Error: $($result.error.message)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
}
