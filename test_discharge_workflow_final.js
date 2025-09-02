async function testDischargeWorkflow() {
    console.log('🧪 Testing Discharge Workflow with Patient Number P1025...\n');
    
    const baseURL = 'http://localhost:8000';
    
    try {
        // Test 1: Discharge patient P1025
        console.log('📋 Test 1: Discharging patient P1025...');
        
        const response = await fetch(`${baseURL}/tools/call`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                id: 1,
                params: {
                    name: "discharge_patient_complete",
                    arguments: {
                        patient_number: 'P1025',
                        discharge_condition: 'stable',
                        discharge_destination: 'home'
                    }
                }
            })
        });
        
        const responseData = await response.json();
        console.log('✅ Raw Response:', JSON.stringify(responseData, null, 2));
        
        // Extract the actual result from JSON-RPC format
        const dischargeResult = responseData.result?.content?.[0]?.text;
        let parsedResult;
        
        try {
            parsedResult = JSON.parse(dischargeResult);
        } catch (e) {
            console.log('⚠️ Response is not JSON, treating as text:', dischargeResult);
            parsedResult = { message: dischargeResult };
        }
        
        console.log('✅ Parsed Discharge Result:', JSON.stringify(parsedResult, null, 2));
        
        if (parsedResult.success) {
            console.log('\n🎉 SUCCESS: Patient P1025 discharged successfully!');
            
            // Extract data from the nested result structure
            const result = parsedResult.result;
            if (result) {
                console.log(`📄 Report Number: ${result.report_number || 'N/A'}`);
                console.log(`🛏️ Bed ID: ${result.bed_id || 'N/A'}`);
                console.log(`⏰ Cleaning Timer: ${result.cleaning_timer || 'N/A'}`);
                console.log(`👤 Patient Name: ${result.discharge_report?.patient_name || 'N/A'}`);
                console.log(`🛏️ Bed Number: ${result.discharge_report?.raw_data?.patient_summary?.bed_number || 'N/A'}`);
                console.log(`🏥 Department: ${result.discharge_report?.raw_data?.patient_summary?.department || 'N/A'}`);
                console.log(`📋 Next Steps: ${result.next_steps?.join(', ') || 'N/A'}`);
            }
        } else {
            console.log('\n❌ FAILED: Discharge failed');
            console.log(`Error: ${parsedResult.message || parsedResult.error || 'Unknown error'}`);
        }
        
    } catch (error) {
        console.error('💥 Error during discharge workflow test:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
        }
    }
}

// Run the test
testDischargeWorkflow().catch(console.error);
