# Comprehensive Assignment Testing and Database Verification Script
# Patient: Sarah Johnson (7a1810c4-ecb9-4302-9c3c-489598486798)

Write-Host "===============================================" -ForegroundColor Blue
Write-Host "ASSIGNMENT TESTING & DATABASE VERIFICATION" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Blue

$patientId = "7a1810c4-ecb9-4302-9c3c-489598486798"
$patientName = "Sarah Johnson"

# Function to call backend tool
function Invoke-BackendTool {
    param(
        [string]$toolName,
        [hashtable]$arguments = @{}
    )
    
    $payload = @{
        jsonrpc = "2.0"
        id = 1
        method = "tools/call"
        params = @{
            name = $toolName
            arguments = $arguments
        }
    } | ConvertTo-Json -Depth 4

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/tools/call" -Method POST -Body $payload -ContentType "application/json"
        $result = $response.Content | ConvertFrom-Json
        return $result
    } catch {
        Write-Host "Error calling $toolName`: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Test 1: Find Patient
Write-Host "`n1. FINDING PATIENT..." -ForegroundColor Yellow
$findResult = Invoke-BackendTool -toolName "search_patients" -arguments @{ query = $patientName }
if ($findResult -and $findResult.result.content[0].text -like "*success*") {
    Write-Host "✅ Patient found successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Patient not found" -ForegroundColor Red
}

# Test 2: Bed Assignment
Write-Host "`n2. TESTING BED ASSIGNMENT..." -ForegroundColor Yellow
$bedResult = Invoke-BackendTool -toolName "assign_bed_to_patient" -arguments @{
    patient_id = $patientId
    bed_number = "301A"
    assignment_date = "2025-08-26"
}

if ($bedResult -and $bedResult.result.content[0].text -like "*success*") {
    Write-Host "✅ Bed assignment successful" -ForegroundColor Green
} else {
    Write-Host "❌ Bed assignment failed" -ForegroundColor Red
    if ($bedResult) {
        Write-Host "Response: $($bedResult.result.content[0].text)" -ForegroundColor Gray
    }
}

# Test 3: Equipment Assignment
Write-Host "`n3. TESTING EQUIPMENT ASSIGNMENT..." -ForegroundColor Yellow
$equipmentResult = Invoke-BackendTool -toolName "add_equipment_usage_simple" -arguments @{
    patient_id = $patientId
    equipment_name = "X-Ray"
    staff_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}

if ($equipmentResult -and $equipmentResult.result.content[0].text -like "*success*") {
    Write-Host "✅ Equipment assignment successful" -ForegroundColor Green
} else {
    Write-Host "❌ Equipment assignment failed" -ForegroundColor Red
    if ($equipmentResult) {
        Write-Host "Response: $($equipmentResult.result.content[0].text)" -ForegroundColor Gray
    }
}

# Test 4: Staff Assignment
Write-Host "`n4. TESTING STAFF ASSIGNMENT..." -ForegroundColor Yellow
$staffResult = Invoke-BackendTool -toolName "assign_staff_to_patient_simple" -arguments @{
    patient_id = $patientId
    staff_employee_id = "EMP001"
    assignment_date = "2025-08-26"
    role = "Nurse"
}

if ($staffResult -and $staffResult.result.content[0].text -like "*success*") {
    Write-Host "✅ Staff assignment successful" -ForegroundColor Green
} else {
    Write-Host "❌ Staff assignment failed" -ForegroundColor Red
    if ($staffResult) {
        Write-Host "Response: $($staffResult.result.content[0].text)" -ForegroundColor Gray
    }
}

# Test 5: Supply Assignment
Write-Host "`n5. TESTING SUPPLY ASSIGNMENT..." -ForegroundColor Yellow
$supplyResult = Invoke-BackendTool -toolName "update_supply_stock" -arguments @{
    supply_id = "1"
    quantity_change = -1
    transaction_type = "ALLOCATION"
    performed_by = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    notes = "Allocated to patient Sarah Johnson"
}

if ($supplyResult -and $supplyResult.result.content[0].text -like "*success*") {
    Write-Host "✅ Supply assignment successful" -ForegroundColor Green
} else {
    Write-Host "❌ Supply assignment failed" -ForegroundColor Red
    if ($supplyResult) {
        Write-Host "Response: $($supplyResult.result.content[0].text)" -ForegroundColor Gray
    }
}

Write-Host "`n===============================================" -ForegroundColor Blue
Write-Host "DATABASE VERIFICATION" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Blue

# Now verify in database
Write-Host "`nVerifying assignments in database..." -ForegroundColor Cyan
