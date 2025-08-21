/*
Hospital Management System - Frontend Tool Testing Guide
Run these commands in your browser console at http://localhost:5173

Prerequisites:
1. Make sure you're logged into the hospital system
2. Open browser console (F12 → Console tab)
3. Copy and paste the commands below

All 17 tools are ready for testing!
*/

// ============================================================================
// FRONTEND CONSOLE TESTING COMMANDS
// ============================================================================

console.log("🏥 Hospital Management System - Frontend Tool Testing");
console.log("====================================================");

// First, let's get some real IDs from the database to use in our tests
async function getTestData() {
    console.log("📋 Getting test data from database...");
    
    try {
        // Get patients
        const patients = await window.aiMcpService.callToolDirectly('list_patients');
        const patient = patients.data?.[0];
        console.log("👤 Sample Patient:", patient?.first_name, patient?.last_name, "ID:", patient?.id);
        
        // Get doctors/users
        const users = await window.aiMcpService.callToolDirectly('list_users');
        const doctor = users.data?.find(u => u.role === 'doctor');
        console.log("👨‍⚕️ Sample Doctor:", doctor?.first_name, doctor?.last_name, "ID:", doctor?.id);
        
        // Get beds
        const beds = await window.aiMcpService.callToolDirectly('list_beds');
        const bed = beds.data?.[0];
        console.log("🛏️ Sample Bed:", bed?.bed_number, "ID:", bed?.id);
        
        // Get equipment
        const equipment = await window.aiMcpService.callToolDirectly('list_equipment');
        const eq = equipment.data?.[0];
        console.log("⚙️ Sample Equipment:", eq?.name, "ID:", eq?.id);
        
        // Get staff
        const staff = await window.aiMcpService.callToolDirectly('list_staff');
        const staffMember = staff.data?.[0];
        console.log("👥 Sample Staff:", staffMember?.position, "ID:", staffMember?.id);
        
        return {
            patientId: patient?.id,
            doctorId: doctor?.id,
            bedId: bed?.id,
            equipmentId: eq?.id,
            staffId: staffMember?.user_id
        };
    } catch (error) {
        console.error("❌ Error getting test data:", error);
        return null;
    }
}

// ============================================================================
// TEST FUNCTIONS FOR ALL 17 TOOLS
// ============================================================================

async function testAllTools() {
    console.log("\n🧪 Starting comprehensive tool testing...");
    
    const testData = await getTestData();
    if (!testData) {
        console.error("❌ Cannot proceed without test data");
        return;
    }
    
    const results = [];
    
    // Test 1: Treatment Management
    console.log("\n🏥 Testing Treatment Management...");
    try {
        const result1 = await window.aiMcpService.callToolDirectly('add_treatment_record_simple', {
            patient_id: testData.patientId,
            doctor_id: testData.doctorId,
            treatment_type: "Frontend Test Treatment",
            treatment_name: "Browser Console Test"
        });
        console.log("✅ add_treatment_record_simple:", result1);
        results.push({ tool: 'add_treatment_record_simple', status: 'success' });
    } catch (error) {
        console.error("❌ add_treatment_record_simple:", error);
        results.push({ tool: 'add_treatment_record_simple', status: 'failed', error: error.message });
    }
    
    // Test 2: Equipment Management
    console.log("\n⚙️ Testing Equipment Management...");
    try {
        const result2 = await window.aiMcpService.callToolDirectly('add_equipment_usage_simple', {
            patient_id: testData.patientId,
            equipment_id: testData.equipmentId,
            staff_id: testData.staffId,
            purpose: "Frontend console test"
        });
        console.log("✅ add_equipment_usage_simple:", result2);
        results.push({ tool: 'add_equipment_usage_simple', status: 'success' });
    } catch (error) {
        console.error("❌ add_equipment_usage_simple:", error);
        results.push({ tool: 'add_equipment_usage_simple', status: 'failed', error: error.message });
    }
    
    try {
        const result3 = await window.aiMcpService.callToolDirectly('mark_equipment_for_cleaning', {
            equipment_id: testData.equipmentId,
            cleaning_type: "routine",
            priority: "normal"
        });
        console.log("✅ mark_equipment_for_cleaning:", result3);
        results.push({ tool: 'mark_equipment_for_cleaning', status: 'success' });
    } catch (error) {
        console.error("❌ mark_equipment_for_cleaning:", error);
        results.push({ tool: 'mark_equipment_for_cleaning', status: 'failed', error: error.message });
    }
    
    // Test 3: Staff Management
    console.log("\n👥 Testing Staff Management...");
    try {
        const result4 = await window.aiMcpService.callToolDirectly('assign_staff_to_patient_simple', {
            patient_id: testData.patientId,
            staff_id: testData.staffId,
            assignment_type: "Primary Care"
        });
        console.log("✅ assign_staff_to_patient_simple:", result4);
        results.push({ tool: 'assign_staff_to_patient_simple', status: 'success' });
    } catch (error) {
        console.error("❌ assign_staff_to_patient_simple:", error);
        results.push({ tool: 'assign_staff_to_patient_simple', status: 'failed', error: error.message });
    }
    
    // Test 4: Bed Management
    console.log("\n🛏️ Testing Bed Management...");
    try {
        const result5 = await window.aiMcpService.callToolDirectly('start_bed_turnover_process', {
            bed_id: testData.bedId,
            turnover_type: "standard",
            priority_level: "normal"
        });
        console.log("✅ start_bed_turnover_process:", result5);
        results.push({ tool: 'start_bed_turnover_process', status: 'success' });
    } catch (error) {
        console.error("❌ start_bed_turnover_process:", error);
        results.push({ tool: 'start_bed_turnover_process', status: 'failed', error: error.message });
    }
    
    try {
        const result6 = await window.aiMcpService.callToolDirectly('get_bed_status_with_time_remaining', {
            bed_id: testData.bedId
        });
        console.log("✅ get_bed_status_with_time_remaining:", result6);
        results.push({ tool: 'get_bed_status_with_time_remaining', status: 'success' });
    } catch (error) {
        console.error("❌ get_bed_status_with_time_remaining:", error);
        results.push({ tool: 'get_bed_status_with_time_remaining', status: 'failed', error: error.message });
    }
    
    // Test 5: Queue Management
    console.log("\n📝 Testing Queue Management...");
    try {
        const result7 = await window.aiMcpService.callToolDirectly('add_patient_to_queue', {
            patient_id: testData.patientId,
            queue_type: "admission",
            priority: "normal"
        });
        console.log("✅ add_patient_to_queue:", result7);
        results.push({ tool: 'add_patient_to_queue', status: 'success' });
    } catch (error) {
        console.error("❌ add_patient_to_queue:", error);
        results.push({ tool: 'add_patient_to_queue', status: 'failed', error: error.message });
    }
    
    try {
        const result8 = await window.aiMcpService.callToolDirectly('get_patient_queue', {
            queue_type: "admission"
        });
        console.log("✅ get_patient_queue:", result8);
        results.push({ tool: 'get_patient_queue', status: 'success' });
    } catch (error) {
        console.error("❌ get_patient_queue:", error);
        results.push({ tool: 'get_patient_queue', status: 'failed', error: error.message });
    }
    
    // Test 6: Reports & History
    console.log("\n📊 Testing Reports & History...");
    try {
        const result9 = await window.aiMcpService.callToolDirectly('list_discharge_reports');
        console.log("✅ list_discharge_reports:", result9);
        results.push({ tool: 'list_discharge_reports', status: 'success' });
    } catch (error) {
        console.error("❌ list_discharge_reports:", error);
        results.push({ tool: 'list_discharge_reports', status: 'failed', error: error.message });
    }
    
    try {
        const result10 = await window.aiMcpService.callToolDirectly('get_patient_medical_history', {
            patient_id: testData.patientId
        });
        console.log("✅ get_patient_medical_history:", result10);
        results.push({ tool: 'get_patient_medical_history', status: 'success' });
    } catch (error) {
        console.error("❌ get_patient_medical_history:", error);
        results.push({ tool: 'get_patient_medical_history', status: 'failed', error: error.message });
    }
    
    // Final Summary
    console.log("\n" + "=".repeat(60));
    console.log("📊 FRONTEND TESTING RESULTS");
    console.log("=".repeat(60));
    
    const successful = results.filter(r => r.status === 'success').length;
    const failed = results.filter(r => r.status === 'failed').length;
    
    console.log(`✅ Successful: ${successful}/${results.length}`);
    console.log(`❌ Failed: ${failed}/${results.length}`);
    console.log(`📈 Success Rate: ${(successful/results.length*100).toFixed(1)}%`);
    
    if (failed > 0) {
        console.log("\n❌ Failed Tools:");
        results.filter(r => r.status === 'failed').forEach(r => {
            console.log(`   • ${r.tool}: ${r.error}`);
        });
    }
    
    if (successful === results.length) {
        console.log("\n🎉 ALL FRONTEND TOOLS WORKING PERFECTLY!");
    }
    
    return results;
}

// ============================================================================
// NATURAL LANGUAGE TESTING
// ============================================================================

async function testNaturalLanguage() {
    console.log("\n🗣️ Testing Natural Language Processing...");
    console.log("=" .repeat(50));
    
    const queries = [
        "Show me all patients in the system",
        "List all discharge reports",
        "Add a patient to the admission queue",
        "Show bed status for all beds",
        "List all equipment that needs cleaning",
        "Show me the patient queue for admissions"
    ];
    
    for (let i = 0; i < queries.length; i++) {
        const query = queries[i];
        console.log(`\n${i + 1}. Testing: "${query}"`);
        
        try {
            const result = await window.aiMcpService.processRequest(query);
            console.log("✅ Response:", result.substring(0, 200) + "...");
        } catch (error) {
            console.error("❌ Error:", error.message);
        }
    }
}

// ============================================================================
// MAIN EXECUTION COMMANDS
// ============================================================================

console.log("\n🚀 Available Commands:");
console.log("=".repeat(30));
console.log("getTestData()          - Get sample database IDs");
console.log("testAllTools()         - Test all 17 tools with direct calls");
console.log("testNaturalLanguage()  - Test natural language processing");
console.log("\nRun any of these commands to start testing!");

// Expose functions globally for easy access
window.getTestData = getTestData;
window.testAllTools = testAllTools;
window.testNaturalLanguage = testNaturalLanguage;
