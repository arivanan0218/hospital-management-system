/**
 * Hospital Tools Service - Intelligent wrapper for MCP tools
 * This service provides smart tool calling based on user queries
 */

class HospitalToolsService {
  constructor() {
    this.baseUrl = import.meta.env.VITE_MCP_BRIDGE_URL || 'http://localhost:8080';
    
    // Define all available tools with their descriptions and parameters
    this.availableTools = {
      // Patient Management
      'list_patients': {
        description: 'Get all patients in the hospital',
        parameters: {},
        category: 'patient'
      },
      'get_patient_by_id': {
        description: 'Get specific patient by ID',
        parameters: { patient_id: 'string' },
        category: 'patient'
      },
      'create_patient': {
        description: 'Create a new patient record',
        parameters: {
          patient_number: 'string',
          first_name: 'string',
          last_name: 'string',
          date_of_birth: 'string (YYYY-MM-DD)',
          gender: 'string (optional)',
          phone: 'string (optional)',
          email: 'string (optional)',
          address: 'string (optional)'
        },
        category: 'patient'
      },
      
      // Bed Management
      'list_beds': {
        description: 'Get all beds, optionally filter by status',
        parameters: { status: 'string (optional: available, occupied, maintenance)' },
        category: 'bed'
      },
      'assign_bed_to_patient': {
        description: 'Assign a bed to a patient',
        parameters: {
          bed_id: 'string',
          patient_id: 'string',
          admission_date: 'string (optional, YYYY-MM-DD)'
        },
        category: 'bed'
      },
      'discharge_bed': {
        description: 'Discharge patient from bed',
        parameters: {
          bed_id: 'string',
          discharge_date: 'string (optional, YYYY-MM-DD)'
        },
        category: 'bed'
      },
      'create_bed': {
        description: 'Create a new bed',
        parameters: {
          bed_number: 'string',
          room_id: 'string',
          bed_type: 'string (optional)',
          status: 'string (optional, default: available)'
        },
        category: 'bed'
      },
      
      // Staff Management
      'list_staff': {
        description: 'Get all staff, optionally filter by department or status',
        parameters: {
          department_id: 'string (optional)',
          status: 'string (optional: active, inactive)'
        },
        category: 'staff'
      },
      'create_staff': {
        description: 'Create new staff member',
        parameters: {
          user_id: 'string',
          employee_id: 'string',
          department_id: 'string',
          position: 'string',
          specialization: 'string (optional)',
          salary: 'number (optional)'
        },
        category: 'staff'
      },
      
      // Appointment Management
      'list_appointments': {
        description: 'Get appointments, optionally filter by doctor, patient, or date',
        parameters: {
          doctor_id: 'string (optional)',
          patient_id: 'string (optional)',
          date: 'string (optional, YYYY-MM-DD)'
        },
        category: 'appointment'
      },
      'create_appointment': {
        description: 'Create new appointment',
        parameters: {
          patient_id: 'string',
          doctor_id: 'string',
          department_id: 'string',
          appointment_date: 'string (YYYY-MM-DD HH:MM)',
          reason: 'string (optional)',
          duration_minutes: 'number (optional, default: 30)'
        },
        category: 'appointment'
      },
      
      // Equipment Management
      'list_equipment': {
        description: 'Get all equipment, optionally filter by status or department',
        parameters: {
          status: 'string (optional: operational, maintenance, out_of_order)',
          department_id: 'string (optional)'
        },
        category: 'equipment'
      },
      'create_equipment': {
        description: 'Add new equipment',
        parameters: {
          equipment_id: 'string',
          name: 'string',
          category_id: 'string',
          model: 'string (optional)',
          manufacturer: 'string (optional)',
          department_id: 'string (optional)'
        },
        category: 'equipment'
      },
      'update_equipment_status': {
        description: 'Update equipment status',
        parameters: {
          equipment_id: 'string',
          status: 'string',
          notes: 'string (optional)'
        },
        category: 'equipment'
      },
      
      // Supply Management
      'list_supplies': {
        description: 'Get all supplies, optionally show only low stock items',
        parameters: {
          low_stock_only: 'boolean (optional, default: false)'
        },
        category: 'supply'
      },
      'create_supply': {
        description: 'Add new supply item',
        parameters: {
          item_code: 'string',
          name: 'string',
          category_id: 'string',
          unit_of_measure: 'string',
          current_stock: 'number (optional)',
          minimum_stock_level: 'number (optional)'
        },
        category: 'supply'
      },
      'update_supply_stock': {
        description: 'Update supply stock levels',
        parameters: {
          supply_id: 'string',
          quantity_change: 'number',
          transaction_type: 'string (purchase, usage, adjustment)',
          performed_by: 'string'
        },
        category: 'supply'
      },
      
      // Department & Room Management
      'list_departments': {
        description: 'Get all hospital departments',
        parameters: {},
        category: 'department'
      },
      'create_department': {
        description: 'Create new department',
        parameters: {
          name: 'string',
          description: 'string (optional)',
          head_doctor_id: 'string (optional)'
        },
        category: 'department'
      },
      'get_department_by_id': {
        description: 'Get specific department by ID',
        parameters: { department_id: 'string' },
        category: 'department'
      },
      'list_rooms': {
        description: 'Get all hospital rooms',
        parameters: {},
        category: 'room'
      },
      'create_room': {
        description: 'Create new room',
        parameters: {
          room_number: 'string',
          department_id: 'string',
          room_type: 'string (optional)',
          capacity: 'number (optional, default: 1)'
        },
        category: 'room'
      },
      
      // User Management
      'list_users': {
        description: 'Get all system users',
        parameters: {},
        category: 'user'
      },
      'create_user': {
        description: 'Create new system user',
        parameters: {
          username: 'string',
          email: 'string',
          password_hash: 'string',
          role: 'string',
          first_name: 'string',
          last_name: 'string'
        },
        category: 'user'
      }
    };
  }

  /**
   * Intelligently determine which tools to call based on user query
   */
  async analyzeAndExecuteQuery(userMessage) {
    const message = userMessage.toLowerCase();
    const toolsToCall = [];
    
    // CREATION OPERATIONS - Handle add/create/register requests
    if (message.includes('add') || message.includes('create') || message.includes('register') || 
        message.includes('new') || message.includes('admit') || message.includes('admission')) {
      
      // Create Patient - Enhanced detection
      if (message.includes('patient') || message.includes('full name') || 
          (message.includes('name') && (message.includes('dob') || message.includes('date of birth')))) {
        // Try to extract patient information from the message
        const patientInfo = this.extractPatientInfo(userMessage);
        console.log('🔍 Patient extraction result:', patientInfo);
        if (patientInfo) {
          console.log('✅ Creating patient with info:', patientInfo);
          toolsToCall.push({ tool: 'create_patient', params: patientInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          console.log('❌ Could not extract sufficient patient information');
          // Return an error response indicating what information is needed
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract patient information. Please provide: full name, date of birth (YYYY-MM-DD), and optionally phone, gender, address.',
            example: 'Example: "Create patient with full name: John Doe, date of birth: 1990-01-15, phone: 555-1234"',
            query: userMessage,
            description: 'Patient creation failed - insufficient information'
          };
        }
      }
      
      // Create Bed
      if (message.includes('bed')) {
        const bedInfo = await this.extractBedInfo(userMessage);
        if (bedInfo) {
          toolsToCall.push({ tool: 'create_bed', params: bedInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract bed information. Please provide: bed number and room ID.',
            example: 'Example: "Create bed number: B001, room: room-id-here"',
            query: userMessage,
            description: 'Bed creation failed - insufficient information'
          };
        }
      }
      
      // Create Staff
      if (message.includes('staff') || message.includes('employee')) {
        const staffInfo = this.extractStaffInfo(userMessage);
        if (staffInfo) {
          toolsToCall.push({ tool: 'create_staff', params: staffInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Staff creation not yet implemented. Please use the direct API.',
            query: userMessage,
            description: 'Staff creation failed - not implemented'
          };
        }
      }
      
      // Create Department
      if (message.includes('department')) {
        const departmentInfo = this.extractDepartmentInfo(userMessage);
        if (departmentInfo) {
          toolsToCall.push({ tool: 'create_department', params: departmentInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract department information. Please provide: department name and optionally description.',
            example: 'Example: "Create department: Cardiology, description: Heart and cardiovascular care"',
            query: userMessage,
            description: 'Department creation failed - insufficient information'
          };
        }
      }
      
      // Create Room
      if (message.includes('room')) {
        const roomInfo = await this.extractRoomInfo(userMessage);
        if (roomInfo) {
          toolsToCall.push({ tool: 'create_room', params: roomInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract room information. Please provide: room number and department ID.',
            example: 'Example: "Create room: R101, department: dept-id-here"',
            query: userMessage,
            description: 'Room creation failed - insufficient information'
          };
        }
      }
      
      // Create Equipment
      if (message.includes('equipment')) {
        const equipmentInfo = this.extractEquipmentInfo(userMessage);
        if (equipmentInfo) {
          toolsToCall.push({ tool: 'create_equipment', params: equipmentInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract equipment information. Please provide: equipment ID, name, and category.',
            example: 'Example: "Create equipment: EQ001, name: MRI Scanner, category: imaging"',
            query: userMessage,
            description: 'Equipment creation failed - insufficient information'
          };
        }
      }
      
      // Create Supply
      if (message.includes('supply') || message.includes('inventory')) {
        const supplyInfo = this.extractSupplyInfo(userMessage);
        if (supplyInfo) {
          toolsToCall.push({ tool: 'create_supply', params: supplyInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract supply information. Please provide: item code, name, category, and unit of measure.',
            example: 'Example: "Create supply: S001, name: Bandages, category: medical, unit: pieces"',
            query: userMessage,
            description: 'Supply creation failed - insufficient information'
          };
        }
      }
      
      // Create Appointment
      if (message.includes('appointment')) {
        const appointmentInfo = this.extractAppointmentInfo(userMessage);
        if (appointmentInfo) {
          toolsToCall.push({ tool: 'create_appointment', params: appointmentInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract appointment information. Please provide: patient ID, doctor ID, department ID, and date.',
            example: 'Example: "Create appointment for patient P001 with doctor D001 in cardiology on 2025-08-05 10:00"',
            query: userMessage,
            description: 'Appointment creation failed - insufficient information'
          };
        }
      }
      
      // If we reach here, it's a creation request but we don't know what to create
      return {
        success: false,
        error: 'UNKNOWN_CREATION',
        message: 'Creation request detected but unable to determine what to create. Supported: patient, bed, department, room, equipment, supply, appointment.',
        query: userMessage,
        description: 'Unknown creation request'
      };
    }
    
    // UPDATE OPERATIONS - Handle update requests
    if (message.includes('update') || message.includes('modify') || message.includes('change')) {
      
      // Update Equipment Status
      if (message.includes('equipment') && (message.includes('status') || message.includes('maintenance') || message.includes('operational'))) {
        const updateInfo = this.extractEquipmentUpdateInfo(userMessage);
        if (updateInfo) {
          toolsToCall.push({ tool: 'update_equipment_status', params: updateInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract equipment update information. Please provide: equipment ID and new status.',
            example: 'Example: "Update equipment EQ001 status to maintenance"',
            query: userMessage,
            description: 'Equipment update failed - insufficient information'
          };
        }
      }
      
      // Update Supply Stock
      if (message.includes('supply') || message.includes('stock') || message.includes('inventory')) {
        const updateInfo = this.extractSupplyUpdateInfo(userMessage);
        if (updateInfo) {
          toolsToCall.push({ tool: 'update_supply_stock', params: updateInfo, priority: 1 });
          return await this.executeTools(toolsToCall, userMessage);
        } else {
          return {
            success: false,
            error: 'EXTRACTION_FAILED',
            message: 'Unable to extract supply update information. Please provide: supply ID, quantity change, transaction type, and performed by.',
            example: 'Example: "Update supply S001 add 50 units purchase by admin"',
            query: userMessage,
            description: 'Supply update failed - insufficient information'
          };
        }
      }
      
      // If we reach here, it's an update request but we don't know what to update
      return {
        success: false,
        error: 'UNKNOWN_UPDATE',
        message: 'Update request detected but unable to determine what to update. Supported: equipment status, supply stock.',
        query: userMessage,
        description: 'Unknown update request'
      };
    }
    
    // EXISTING READ OPERATIONS
    // Patient queries
    if (message.includes('patient')) {
      if (message.includes('arivu') || message.includes('specific patient')) {
        toolsToCall.push({ tool: 'list_patients', params: {}, priority: 1 });
      } else if (message.includes('list') || message.includes('all') || message.includes('show')) {
        toolsToCall.push({ tool: 'list_patients', params: {}, priority: 1 });
      }
    }
    
    // Bed queries
    if (message.includes('bed')) {
      const params = {};
      if (message.includes('available') || message.includes('free')) {
        params.status = 'available';
      } else if (message.includes('occupied')) {
        params.status = 'occupied';
      }
      toolsToCall.push({ tool: 'list_beds', params, priority: 1 });
    }
    
    // Staff queries
    if (message.includes('staff') || message.includes('doctor') || message.includes('nurse')) {
      toolsToCall.push({ tool: 'list_staff', params: {}, priority: 1 });
    }
    
    // Appointment queries
    if (message.includes('appointment')) {
      const params = {};
      if (message.includes('today')) {
        params.date = new Date().toISOString().split('T')[0];
      }
      toolsToCall.push({ tool: 'list_appointments', params, priority: 1 });
    }
    
    // Equipment queries
    if (message.includes('equipment')) {
      toolsToCall.push({ tool: 'list_equipment', params: {}, priority: 1 });
    }
    
    // Supply queries
    if (message.includes('supply') || message.includes('inventory')) {
      const params = {};
      if (message.includes('low') || message.includes('running out')) {
        params.low_stock_only = true;
      }
      toolsToCall.push({ tool: 'list_supplies', params, priority: 1 });
    }
    
    // Department queries
    if (message.includes('department')) {
      toolsToCall.push({ tool: 'list_departments', params: {}, priority: 1 });
    }
    
    // Room queries
    if (message.includes('room')) {
      toolsToCall.push({ tool: 'list_rooms', params: {}, priority: 1 });
    }
    
    // Overview/Dashboard queries
    if (message.includes('overview') || message.includes('summary') || message.includes('dashboard') || toolsToCall.length === 0) {
      toolsToCall.push(
        { tool: 'list_patients', params: {}, priority: 2 },
        { tool: 'list_beds', params: {}, priority: 2 },
        { tool: 'list_staff', params: {}, priority: 2 },
        { tool: 'list_appointments', params: {}, priority: 2 }
      );
    }
    
    return await this.executeTools(toolsToCall, userMessage);
  }

  /**
   * Execute tools and return formatted results
   */
  async executeTools(toolsToCall, userMessage) {
    // Execute tools in priority order
    const results = {};
    const errors = {};
    let toolResult = null;
    let operation = null;
    
    for (const toolCall of toolsToCall.sort((a, b) => a.priority - b.priority)) {
      try {
        console.log(`🚀 Calling tool: ${toolCall.tool} with params:`, toolCall.params);
        const result = await this.callTool(toolCall.tool, toolCall.params);
        results[toolCall.tool] = result;
        
        // For creation operations, capture the tool result
        if (toolCall.tool.startsWith('create_')) {
          // Extract the actual created data from the MCP bridge response
          if (result && result.result && result.result.data) {
            toolResult = result.result.data;  // The actual created record
          } else if (result && result.data) {
            toolResult = result.data;
          } else {
            toolResult = result;
          }
          operation = toolCall.tool;
          console.log(`✅ Creation tool ${toolCall.tool} completed with result:`, toolResult);
        }
        
      } catch (error) {
        errors[toolCall.tool] = error.message;
        console.error(`❌ Tool ${toolCall.tool} failed:`, error);
      }
    }
    
    const response = {
      success: Object.keys(results).length > 0,
      data: results,
      errors: errors,
      toolsCalled: toolsToCall.map(t => t.tool),
      query: userMessage,
      description: this.generateDescription(toolsToCall, results)
    };
    
    // Add tool result for creation operations
    if (toolResult && operation) {
      response.toolResult = toolResult;
      response.operation = operation;
      console.log(`🎯 Returning creation result:`, { operation, toolResult });
    }
    
    return response;
  }

  /**
   * Extract patient information from user message
   */
  extractPatientInfo(message) {
    console.log('🔍 Extracting patient info from:', message);
    
    // Enhanced patterns for detailed patient information
    const patterns = {
      // More flexible name patterns
      fullName: /(?:full.?name|name|patient.?name):?\s*[:\-]?\s*([a-zA-Z\s]{2,40})(?:\s*(?:date|dob|gender|phone|address|emergency|medical|reason|born|age|\d{4})|$)/i,
      firstName: /(?:first.?name):?\s*[:\-]?\s*([a-zA-Z]+)/i,
      lastName: /(?:last.?name):?\s*[:\-]?\s*([a-zA-Z]+)/i,
      
      // More flexible date patterns
      dob: /(?:dob|date.?of.?birth|born|birth.?date):?\s*[:\-]?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})/i,
      
      // Phone patterns
      primaryPhone: /(?:primary.?contact.?number|primary.?phone|phone):?\s*[:\-]?\s*([\+\d\s\-()]{7,15})/i,
      emergencyContactName: /(?:emergency.?contact.?(?:information|name)|emergency.?name):?\s*[:\-]?\s*([a-zA-Z\s]{2,40})(?:\s*(?:relationship|phone|address)|$)/i,
      emergencyContactPhone: /(?:emergency.?contact.?phone|emergency.?phone):?\s*[:\-]?\s*([\+\d\s\-()]{7,15})/i,
      
      // Other patterns
      gender: /(?:gender):?\s*[:\-]?\s*(male|female|m|f)/i,
      address: /(?:address):?\s*[:\-]?\s*([^,\n\r]{5,100})/i,
      medicalHistory: /(?:medical.?history):?\s*[:\-]?\s*([^,\n\r]+)/i,
      reason: /(?:reason.?for.?admission|reason.?for.?visit|reason):?\s*[:\-]?\s*([^,\n\r]+)/i,
      
      // Simple patterns for basic cases
      simpleName: /(?:create|add|register).+?patient.+?([A-Z][a-z]+\s+[A-Z][a-z]+)/i,
      simpleDate: /(\d{4}-\d{2}-\d{2})/g
    };

    const info = {};
    
    // Try simple name extraction first (for cases like "create patient John Doe")
    const simpleNameMatch = message.match(patterns.simpleName);
    if (simpleNameMatch) {
      const fullName = simpleNameMatch[1].trim();
      const nameParts = fullName.split(' ');
      if (nameParts.length >= 2) {
        info.first_name = nameParts[0];
        info.last_name = nameParts.slice(1).join(' ');
        console.log('✅ Extracted simple name:', info.first_name, info.last_name);
      }
    }
    
    // Try detailed extraction
    if (!info.first_name) {
      const fullNameMatch = message.match(patterns.fullName);
      if (fullNameMatch) {
        const fullName = fullNameMatch[1].trim();
        // Remove common words that might be captured
        const cleanName = fullName.replace(/\b(with|patient|create|add|register|new)\b/gi, '').trim();
        const nameParts = cleanName.split(' ').filter(part => part.length > 0);
        if (nameParts.length >= 2) {
          info.first_name = nameParts[0];
          info.last_name = nameParts.slice(1).join(' ');
          console.log('✅ Extracted full name:', info.first_name, info.last_name);
        }
      }
    }
    
    // If still no names, try individual patterns
    if (!info.first_name) {
      const firstNameMatch = message.match(patterns.firstName);
      const lastNameMatch = message.match(patterns.lastName);
      if (firstNameMatch) info.first_name = firstNameMatch[1].trim();
      if (lastNameMatch) info.last_name = lastNameMatch[1].trim();
    }
    
    // Extract date of birth
    const dobMatch = message.match(patterns.dob);
    if (dobMatch) {
      let dob = dobMatch[1];
      // Convert DD/MM/YYYY or DD-MM-YYYY to YYYY-MM-DD
      if (dob.match(/\d{1,2}[-/]\d{1,2}[-/]\d{4}/)) {
        const parts = dob.split(/[-/]/);
        dob = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      info.date_of_birth = dob;
      console.log('✅ Extracted DOB:', info.date_of_birth);
    } else {
      // Try simple date pattern
      const simpleDateMatches = message.match(patterns.simpleDate);
      if (simpleDateMatches && simpleDateMatches.length > 0) {
        info.date_of_birth = simpleDateMatches[0];
        console.log('✅ Extracted simple date:', info.date_of_birth);
      }
    }
    
    // If no date found, try to generate a reasonable default for testing
    if (!info.date_of_birth && info.first_name && info.last_name) {
      console.log('⚠️ No date of birth found, using default for testing');
      info.date_of_birth = '1990-01-01';
    }
    
    // Extract other fields
    const phoneMatch = message.match(patterns.primaryPhone);
    if (phoneMatch) {
      info.phone = phoneMatch[1].trim();
      console.log('✅ Extracted phone:', info.phone);
    }
    
    const emergencyNameMatch = message.match(patterns.emergencyContactName);
    if (emergencyNameMatch) {
      info.emergency_contact_name = emergencyNameMatch[1].trim();
      console.log('✅ Extracted emergency contact name:', info.emergency_contact_name);
    }
    
    const emergencyPhoneMatch = message.match(patterns.emergencyContactPhone);
    if (emergencyPhoneMatch) {
      info.emergency_contact_phone = emergencyPhoneMatch[1].trim();
      console.log('✅ Extracted emergency contact phone:', info.emergency_contact_phone);
    }
    
    const genderMatch = message.match(patterns.gender);
    if (genderMatch) {
      const gender = genderMatch[1].toLowerCase();
      info.gender = gender === 'm' || gender === 'male' ? 'male' : 'female';
      console.log('✅ Extracted gender:', info.gender);
    }
    
    const addressMatch = message.match(patterns.address);
    if (addressMatch) {
      info.address = addressMatch[1].trim();
      console.log('✅ Extracted address:', info.address);
    }
    
    const medicalHistoryMatch = message.match(patterns.medicalHistory);
    if (medicalHistoryMatch) {
      info.medical_history = medicalHistoryMatch[1].trim();
      console.log('✅ Extracted medical history:', info.medical_history);
    }
    
    // Generate patient number if we have minimum required info
    if (info.first_name && info.last_name && info.date_of_birth) {
      info.patient_number = `P${Date.now().toString().slice(-6)}`;
      console.log('✅ Generated patient info:', info);
      return info;
    }
    
    console.log('❌ Insufficient patient information extracted. Need at least: first_name, last_name, date_of_birth');
    console.log('Found:', { 
      first_name: info.first_name, 
      last_name: info.last_name, 
      date_of_birth: info.date_of_birth 
    });
    return null;
  }

  /**
   * Extract bed information from user message
   */
  async extractBedInfo(message) {
    console.log('🔍 Extracting bed info from:', message);
    
    const patterns = {
      bedNumber: /(?:bed.?number|bed):?\s*([A-Za-z0-9]+)/i,
      roomId: /(?:room.?id|room):?\s*([a-f0-9-]{36})/i,
      roomNumber: /(?:room[\s:]*(?:number[\s:]*)?)([A-Za-z0-9]+)/i,
      bedType: /(?:type|bed.?type):?\s*(emergency|icu|standard|general)/i
    };

    const info = {};
    
    const bedMatch = message.match(patterns.bedNumber);
    if (bedMatch) {
      info.bed_number = bedMatch[1];
      console.log('✅ Extracted bed number:', info.bed_number);
    }
    
    // Try to extract room ID first, then room number
    const roomIdMatch = message.match(patterns.roomId);
    if (roomIdMatch) {
      info.room_id = roomIdMatch[1];
      console.log('✅ Extracted room ID:', info.room_id);
    } else {
      const roomNumberMatch = message.match(patterns.roomNumber);
      if (roomNumberMatch) {
        const roomNumber = roomNumberMatch[1];
        console.log('🔍 Looking up room by number:', roomNumber);
        
        const roomId = await this.getRoomIdByNumber(roomNumber);
        if (roomId) {
          info.room_id = roomId;
          console.log('✅ Found room ID:', info.room_id);
        }
      }
    }
    
    const typeMatch = message.match(patterns.bedType);
    if (typeMatch) {
      info.bed_type = typeMatch[1];
      console.log('✅ Extracted bed type:', info.bed_type);
    }
    
    if (info.bed_number && info.room_id) {
      info.status = 'available';
      return info;
    }
    
    console.log('❌ Missing required fields:', { bed_number: info.bed_number, room_id: info.room_id });
    return null;
  }

  /**
   * Extract staff information from user message
   */
  extractStaffInfo(_message) {
    // Basic staff extraction - would need more sophisticated parsing
    return null; // For now, return null to avoid errors
  }

  /**
   * Extract department information from user message
   */
  extractDepartmentInfo(message) {
    console.log('🔍 Extracting department info from:', message);
    
    const patterns = {
      // More flexible department name patterns
      name: /(?:department|dept)[\s:]*(?:name[\s:]*)?([a-zA-Z\s]{2,50})(?:\s*(?:description|desc|floor|phone|email)|$)/i,
      description: /(?:description|desc)[\s:]*([^,\n\r]{5,200})(?:\s*(?:floor|phone|email)|$)/i,
      floor: /(?:floor|floor[\s]*number)[\s:]*(\d+)/i,
      phone: /(?:phone)[\s:]*([0-9\-\+\s()]{7,15})/i,
      email: /(?:email)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i
    };

    const info = {};
    
    const nameMatch = message.match(patterns.name);
    if (nameMatch) {
      info.name = nameMatch[1].trim();
      console.log('✅ Extracted department name:', info.name);
    }
    
    const descMatch = message.match(patterns.description);
    if (descMatch) {
      info.description = descMatch[1].trim();
      console.log('✅ Extracted description:', info.description);
    }
    
    const floorMatch = message.match(patterns.floor);
    if (floorMatch) {
      info.floor_number = parseInt(floorMatch[1]);
      console.log('✅ Extracted floor number:', info.floor_number);
    }
    
    const phoneMatch = message.match(patterns.phone);
    if (phoneMatch) {
      info.phone = phoneMatch[1].trim();
      console.log('✅ Extracted phone:', info.phone);
    }
    
    const emailMatch = message.match(patterns.email);
    if (emailMatch) {
      info.email = emailMatch[1].trim();
      console.log('✅ Extracted email:', info.email);
    }
    
    if (info.name) {
      return info;
    }
    
    return null;
  }

  /**
   * Extract room information from user message
   */
  async extractRoomInfo(message) {
    console.log('🔍 Extracting room info from:', message);
    
    const patterns = {
      roomNumber: /(?:room[\s:]*)(?:number[\s:]*)?([A-Za-z0-9]+)/i,
      departmentId: /(?:department[\s:]*(?:id[\s:]*)?)([a-f0-9-]{36})/i,
      departmentName: /(?:department[\s:]*(?:name[\s:]*)?)([a-zA-Z\s]+)(?:\s*(?:type|floor|capacity)|$)/i,
      roomType: /(?:type[\s:]*)(emergency|icu|standard|general|private|ward)/i,
      floor: /(?:floor|floor[\s]*number)[\s:]*(\d+)/i,
      capacity: /(?:capacity)[\s:]*(\d+)/i
    };

    const info = {};
    
    const roomMatch = message.match(patterns.roomNumber);
    if (roomMatch) {
      info.room_number = roomMatch[1];
      console.log('✅ Extracted room number:', info.room_number);
    }
    
    // Try to extract department ID first, then department name
    const deptIdMatch = message.match(patterns.departmentId);
    if (deptIdMatch) {
      info.department_id = deptIdMatch[1];
      console.log('✅ Extracted department ID:', info.department_id);
    } else {
      const deptNameMatch = message.match(patterns.departmentName);
      if (deptNameMatch) {
        const deptName = deptNameMatch[1].trim();
        console.log('🔍 Looking up department by name:', deptName);
        
        const departmentId = await this.getDepartmentIdByName(deptName);
        if (departmentId) {
          info.department_id = departmentId;
          console.log('✅ Found department ID:', info.department_id);
        }
      }
    }
    
    const typeMatch = message.match(patterns.roomType);
    if (typeMatch) {
      info.room_type = typeMatch[1];
      console.log('✅ Extracted room type:', info.room_type);
    }
    
    const floorMatch = message.match(patterns.floor);
    if (floorMatch) {
      info.floor_number = parseInt(floorMatch[1]);
      console.log('✅ Extracted floor number:', info.floor_number);
    }
    
    const capacityMatch = message.match(patterns.capacity);
    if (capacityMatch) {
      info.capacity = parseInt(capacityMatch[1]);
      console.log('✅ Extracted capacity:', info.capacity);
    }
    
    if (info.room_number && info.department_id) {
      return info;
    }
    
    console.log('❌ Missing required fields:', { room_number: info.room_number, department_id: info.department_id });
    return null;
  }

  /**
   * Extract equipment information from user message
   */
  extractEquipmentInfo(message) {
    console.log('🔍 Extracting equipment info from:', message);
    
    const patterns = {
      equipmentId: /(?:equipment[\s:]*(?:id[\s:]*)?)([A-Za-z0-9]+)/i,
      name: /(?:name[\s:]*)([a-zA-Z\s]{2,50})(?:\s*(?:category|type)|$)/i,
      category: /(?:category[\s:]*)([a-zA-Z]+)/i
    };

    const info = {};
    
    const idMatch = message.match(patterns.equipmentId);
    if (idMatch) {
      info.equipment_id = idMatch[1];
      console.log('✅ Extracted equipment ID:', info.equipment_id);
    }
    
    const nameMatch = message.match(patterns.name);
    if (nameMatch) {
      info.name = nameMatch[1].trim();
      console.log('✅ Extracted equipment name:', info.name);
    }
    
    const categoryMatch = message.match(patterns.category);
    if (categoryMatch) {
      info.category_id = categoryMatch[1];
      console.log('✅ Extracted category:', info.category_id);
    }
    
    if (info.equipment_id && info.name && info.category_id) {
      return info;
    }
    
    return null;
  }

  /**
   * Extract supply information from user message
   */
  extractSupplyInfo(message) {
    console.log('🔍 Extracting supply info from:', message);
    
    const patterns = {
      itemCode: /(?:code[\s:]*)([A-Za-z0-9]+)/i,
      name: /(?:name[\s:]*)([a-zA-Z\s]{2,50})(?:\s*(?:category|type)|$)/i,
      category: /(?:category[\s:]*)([a-zA-Z]+)/i,
      unit: /(?:unit[\s:]*)([a-zA-Z]+)/i
    };

    const info = {};
    
    const codeMatch = message.match(patterns.itemCode);
    if (codeMatch) {
      info.item_code = codeMatch[1];
      console.log('✅ Extracted item code:', info.item_code);
    }
    
    const nameMatch = message.match(patterns.name);
    if (nameMatch) {
      info.name = nameMatch[1].trim();
      console.log('✅ Extracted supply name:', info.name);
    }
    
    const categoryMatch = message.match(patterns.category);
    if (categoryMatch) {
      info.category_id = categoryMatch[1];
      console.log('✅ Extracted category:', info.category_id);
    }
    
    const unitMatch = message.match(patterns.unit);
    if (unitMatch) {
      info.unit_of_measure = unitMatch[1];
      console.log('✅ Extracted unit:', info.unit_of_measure);
    }
    
    if (info.item_code && info.name && info.category_id && info.unit_of_measure) {
      return info;
    }
    
    return null;
  }

  /**
   * Extract appointment information from user message
   */
  extractAppointmentInfo(message) {
    console.log('🔍 Extracting appointment info from:', message);
    
    const patterns = {
      patientId: /(?:patient[\s:]*(?:id[\s:]*)?)([A-Za-z0-9-]+)/i,
      doctorId: /(?:doctor[\s:]*(?:id[\s:]*)?)([A-Za-z0-9-]+)/i,
      departmentId: /(?:department[\s:]*(?:id[\s:]*)?)([A-Za-z0-9-]+)/i,
      date: /(\d{4}-\d{2}-\d{2}[\s]\d{2}:\d{2})/i
    };

    const info = {};
    
    const patientMatch = message.match(patterns.patientId);
    if (patientMatch) {
      info.patient_id = patientMatch[1];
      console.log('✅ Extracted patient ID:', info.patient_id);
    }
    
    const doctorMatch = message.match(patterns.doctorId);
    if (doctorMatch) {
      info.doctor_id = doctorMatch[1];
      console.log('✅ Extracted doctor ID:', info.doctor_id);
    }
    
    const deptMatch = message.match(patterns.departmentId);
    if (deptMatch) {
      info.department_id = deptMatch[1];
      console.log('✅ Extracted department ID:', info.department_id);
    }
    
    const dateMatch = message.match(patterns.date);
    if (dateMatch) {
      info.appointment_date = dateMatch[1];
      console.log('✅ Extracted appointment date:', info.appointment_date);
    }
    
    if (info.patient_id && info.doctor_id && info.department_id && info.appointment_date) {
      return info;
    }
    
    return null;
  }

  /**
   * Extract equipment update information from user message
   */
  extractEquipmentUpdateInfo(message) {
    console.log('🔍 Extracting equipment update info from:', message);
    
    const patterns = {
      equipmentId: /(?:equipment[\s:]*(?:id[\s:]*)?)([A-Za-z0-9]+)/i,
      status: /(?:status[\s:]*(?:to[\s:]*)?)?(operational|maintenance|out_of_order)/i,
      notes: /(?:notes?[\s:]*)([^,\n\r]{5,200})/i
    };

    const info = {};
    
    const idMatch = message.match(patterns.equipmentId);
    if (idMatch) {
      info.equipment_id = idMatch[1];
      console.log('✅ Extracted equipment ID:', info.equipment_id);
    }
    
    const statusMatch = message.match(patterns.status);
    if (statusMatch) {
      info.status = statusMatch[1];
      console.log('✅ Extracted status:', info.status);
    }
    
    const notesMatch = message.match(patterns.notes);
    if (notesMatch) {
      info.notes = notesMatch[1].trim();
      console.log('✅ Extracted notes:', info.notes);
    }
    
    if (info.equipment_id && info.status) {
      return info;
    }
    
    return null;
  }

  /**
   * Extract supply update information from user message
   */
  extractSupplyUpdateInfo(message) {
    console.log('🔍 Extracting supply update info from:', message);
    
    const patterns = {
      supplyId: /(?:supply[\s:]*(?:id[\s:]*)?)([A-Za-z0-9]+)/i,
      quantityChange: /(?:add|remove|increase|decrease)[\s]*(\d+)/i,
      transactionType: /(purchase|usage|adjustment)/i,
      performedBy: /(?:by[\s:]*)([a-zA-Z\s]+)/i
    };

    const info = {};
    
    const idMatch = message.match(patterns.supplyId);
    if (idMatch) {
      info.supply_id = idMatch[1];
      console.log('✅ Extracted supply ID:', info.supply_id);
    }
    
    const quantityMatch = message.match(patterns.quantityChange);
    if (quantityMatch) {
      let quantity = parseInt(quantityMatch[1]);
      // Make negative if it's a remove/decrease operation
      if (message.includes('remove') || message.includes('decrease')) {
        quantity = -quantity;
      }
      info.quantity_change = quantity;
      console.log('✅ Extracted quantity change:', info.quantity_change);
    }
    
    const typeMatch = message.match(patterns.transactionType);
    if (typeMatch) {
      info.transaction_type = typeMatch[1];
      console.log('✅ Extracted transaction type:', info.transaction_type);
    }
    
    const performedMatch = message.match(patterns.performedBy);
    if (performedMatch) {
      info.performed_by = performedMatch[1].trim();
      console.log('✅ Extracted performed by:', info.performed_by);
    }
    
    if (info.supply_id && info.quantity_change !== undefined && info.transaction_type && info.performed_by) {
      return info;
    }
    
    return null;
  }

  /**
   * Generate description for the operation
   */
  generateDescription(toolsToCall, _results) {
    if (toolsToCall.length === 1) {
      const tool = toolsToCall[0];
      if (tool.tool.startsWith('create_')) {
        return `Created new ${tool.tool.replace('create_', '')}`;
      } else if (tool.tool.startsWith('list_')) {
        return `Retrieved ${tool.tool.replace('list_', '')} data`;
      }
    }
    return 'Hospital operation completed';
  }

  /**
   * Call a specific MCP tool
   */
  async callTool(toolName, parameters = {}) {
    try {
      console.log(`🔧 Calling MCP tool: ${toolName}`, parameters);
      
      const response = await fetch(`${this.baseUrl}/tools/${toolName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(parameters)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Tool ${toolName} HTTP error:`, response.status, errorText);
        throw new Error(`Tool ${toolName} failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      console.log(`✅ Tool ${toolName} executed successfully:`, {
        toolName,
        parameters,
        result: result,
        resultType: typeof result,
        hasContent: !!result && Object.keys(result).length > 0
      });
      
      // For create operations, the result should contain the created record
      if (toolName.startsWith('create_') && result) {
        console.log(`🎯 Creation tool result:`, result);
      }
      
      return result;
    } catch (error) {
      console.error(`❌ Error calling tool ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Get available tools for a specific category
   */
  getToolsByCategory(category) {
    return Object.entries(this.availableTools)
      .filter(([, tool]) => tool.category === category)
      .map(([name, tool]) => ({ name, ...tool }));
  }

  /**
   * Get all available tools
   */
  getAllTools() {
    return Object.entries(this.availableTools).map(([name, tool]) => ({ name, ...tool }));
  }

  /**
   * Get department ID by name
   */
  async getDepartmentIdByName(name) {
    try {
      const response = await this.callTool('list_departments');
      if (response && response.departments) {
        const dept = response.departments.find(d => 
          d.name.toLowerCase() === name.toLowerCase()
        );
        return dept ? dept.id : null;
      }
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
    return null;
  }

  /**
   * Get room ID by number
   */
  async getRoomIdByNumber(roomNumber) {
    try {
      const response = await this.callTool('list_rooms');
      if (response && response.rooms) {
        const room = response.rooms.find(r => 
          r.room_number.toLowerCase() === roomNumber.toLowerCase()
        );
        return room ? room.id : null;
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
    return null;
  }

  /**
   * Format tool results for AI consumption
   */
  formatResultsForAI(results) {
    if (!results.success) {
      return 'No data could be retrieved from the hospital system.';
    }

    let formatted = '\n**REAL HOSPITAL SYSTEM DATA:**\n\n';
    
    Object.entries(results.data).forEach(([toolName, data]) => {
      formatted += `**${toolName.replace(/_/g, ' ').toUpperCase()}:**\n`;
      
      if (data && typeof data === 'object') {
        if (Array.isArray(data)) {
          formatted += `Found ${data.length} records\n`;
          if (data.length > 0) {
            formatted += JSON.stringify(data, null, 2) + '\n';
          }
        } else if (data.patients || data.beds || data.staff) {
          // Handle structured responses
          Object.entries(data).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              formatted += `${key}: ${value.length} records\n`;
              if (value.length > 0 && value.length <= 10) {
                formatted += JSON.stringify(value, null, 2) + '\n';
              }
            } else {
              formatted += `${key}: ${JSON.stringify(value)}\n`;
            }
          });
        } else {
          formatted += JSON.stringify(data, null, 2) + '\n';
        }
      } else {
        formatted += `Data: ${data}\n`;
      }
      formatted += '\n';
    });

    if (Object.keys(results.errors).length > 0) {
      formatted += '**ERRORS:**\n';
      Object.entries(results.errors).forEach(([tool, error]) => {
        formatted += `${tool}: ${error}\n`;
      });
    }

    return formatted;
  }
}

export default new HospitalToolsService();
