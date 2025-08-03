import React, { useState, useEffect, useRef } from 'react';
import DirectAIMCPService from '../services/directAiMcpService.js';

const DirectMCPChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(true);
  
  // Configuration state
  const [openaiApiKey, setOpenaiApiKey] = useState(import.meta.env.VITE_OPENAI_API_KEY || '');
  const [mcpServerConfig, setMcpServerConfig] = useState({
    command: 'python',
    args: ['comprehensive_server.py'],
    env: {
      'PYTHONPATH': 'c:\\Users\\Arivanan\\hospital-management-system\\backend-python'
    },
    cwd: 'c:\\Users\\Arivanan\\hospital-management-system\\backend-python'
  });
  
  const [serverInfo, setServerInfo] = useState(null);
  const [connectionError, setConnectionError] = useState('');
  
  const aiMcpServiceRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Initialize the AI-MCP service
   */
  const initializeService = async () => {
    if (!openaiApiKey.trim()) {
      setConnectionError('Please enter your OpenAI API key');
      return;
    }

    setIsLoading(true);
    setConnectionError('');
    
    try {
      aiMcpServiceRef.current = new DirectAIMCPService();
      
      console.log('🚀 Initializing with config:', mcpServerConfig);
      
      const initialized = await aiMcpServiceRef.current.initialize(
        openaiApiKey,
        mcpServerConfig
      );
      
      if (initialized) {
        setIsConnected(true);
        setShowSetup(false);
        
        const info = aiMcpServiceRef.current.getServerInfo();
        setServerInfo(info);
        
        setMessages([{
          id: Date.now(),
          text: `🏥 Hello! I'm **Hospital AI**, your intelligent assistant for comprehensive hospital management. I've successfully connected to your hospital management system and have access to ${info.toolCount || 0} different tools.

🎯 **I can help you with:**
• 👥 **Patient Management** - Create, search, and update patient records
• 🏢 **Department Operations** - Manage hospital departments and assignments  
• 👨‍⚕️ **Staff Management** - Handle doctor, nurse, and staff information
• 🛏️ **Bed Management** - Track room assignments and bed availability
• 🏥 **Equipment Tracking** - Monitor medical devices and maintenance
• 📦 **Supply Inventory** - Manage medications and consumables
• 📅 **Appointment Scheduling** - Coordinate patient appointments

💡 **What would you like to help you with today?** You can ask me in natural language, like:
• "Show me all patients"
• "Create a new department for cardiology"
• "Check bed availability"
• "Schedule an appointment"

Ready to assist! 🚀`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString()
        }]);
        
      } else {
        throw new Error('Failed to initialize service');
      }
      
    } catch (error) {
      console.error('❌ Initialization failed:', error);
      setConnectionError(`Connection failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Send message to AI
   */
  const sendMessage = async () => {
    if (!inputMessage.trim() || !isConnected || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message
    const userMsg = {
      id: Date.now(),
      text: userMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await aiMcpServiceRef.current.processRequest(userMessage);
      
      if (response.success) {
        // Format the response in Claude's style
        let responseText = response.message || 'I\'ve processed your request successfully.';
        
        // Add function call results if any
        if (response.functionCalls && response.functionCalls.length > 0) {
          responseText += '\n\n';
          
          response.functionCalls.forEach((call) => {
            console.log('🔍 Function call result:', call); // Debug log
            console.log('🔍 Call result structure:', JSON.stringify(call.result, null, 2)); // Debug structure
            if (call.success) {
              // Enhanced visual formatting for function results
              const functionIcon = getFunctionIcon(call.function);
              responseText += `${functionIcon} **${call.function.toUpperCase()}**\n`;
              
              if (call.result && call.result.content) {
                // Try to format the result nicely
                const content = call.result.content;
                if (Array.isArray(content)) {
                  responseText += formatMCPData(content);
                } else if (typeof content === 'object') {
                  responseText += formatMCPData(content);
                } else {
                  responseText += `${content}\n`;
                }
              } else if (call.result) {
                // Handle direct result or MCP text response
                let result = call.result;
                
                // Handle different result formats
                if (Array.isArray(result)) {
                  // If result is an array, check first item
                  if (result.length > 0 && result[0].type === 'text' && result[0].text) {
                    try {
                      const parsedData = JSON.parse(result[0].text);
                      responseText += formatMCPData(parsedData);
                    } catch {
                      responseText += `${result[0].text}\n`;
                    }
                  } else {
                    responseText += formatMCPData(result);
                  }
                } else if (result.type === 'text' && result.text) {
                  // Handle MCP text response format
                  try {
                    const parsedData = JSON.parse(result.text);
                    responseText += formatMCPData(parsedData);
                  } catch {
                    responseText += `${result.text}\n`;
                  }
                } else if (result.text && typeof result.text === 'string') {
                  try {
                    // Try to parse the text as JSON
                    const parsedData = JSON.parse(result.text);
                    responseText += formatMCPData(parsedData);
                  } catch {
                    // If not JSON, display as text
                    responseText += `${result.text}\n`;
                  }
                } else if (result.content) {
                  // Handle result.content structure
                  if (Array.isArray(result.content)) {
                    responseText += formatMCPData(result.content);
                  } else if (typeof result.content === 'object') {
                    responseText += formatMCPData(result.content);
                  } else {
                    responseText += `${result.content}\n`;
                  }
                } else if (typeof result === 'object') {
                  responseText += formatMCPData(result);
                } else {
                  responseText += `ℹ️ ${result}\n`;
                }
              } else {
                responseText += '✅ **COMPLETED SUCCESSFULLY**\n';
              }
            } else {
              responseText += `❌ **${call.function.toUpperCase()} FAILED**: ${call.error}\n`;
            }
            responseText += '\n';
          });
        }
        
        const aiMsg = {
          id: Date.now() + 1,
          text: responseText,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          functionCalls: response.functionCalls
        };
        setMessages(prev => [...prev, aiMsg]);
        
      } else {
        const errorMsg = {
          id: Date.now() + 1,
          text: `I apologize, but I encountered an error: ${response.error || 'Unknown error occurred'}\n\nPlease try rephrasing your request or let me know if you need help with something specific.`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, errorMsg]);
      }
      
    } catch (error) {
      console.error('❌ Send message failed:', error);
      const errorMsg = {
        id: Date.now() + 1,
        text: `I'm sorry, but I'm having trouble processing your request right now: ${error.message}\n\nThis might be a temporary issue. Could you please try again?`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Format message text to render markdown formatting
   */
  const formatMessageText = (text) => {
    if (!text) return '';
    
    return text
      // Bold formatting: **text** -> <strong>text</strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic formatting: *text* -> <em>text</em>
      .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
      // Convert line breaks to <br> tags
      .replace(/\n/g, '<br>')
      // Handle bullet points with proper spacing
      .replace(/^• (.*$)/gm, '<div class="ml-4">• $1</div>')
      // Handle double spaces
      .replace(/\s{2}/g, '&nbsp;&nbsp;');
  };

  /**
   * Get appropriate icon for function calls
   */
  const getFunctionIcon = (functionName) => {
    const iconMap = {
      // Patient functions
      'list_patients': '👥',
      'create_patient': '🆕',
      'get_patient_by_id': '🔍',
      
      // Department functions
      'list_departments': '🏢',
      'create_department': '🏗️',
      'get_department_by_id': '🔍',
      
      // Staff functions
      'list_staff': '👨‍⚕️',
      'create_staff': '👤',
      
      // Bed functions
      'list_beds': '🛏️',
      'create_bed': '🆕',
      'assign_bed_to_patient': '📍',
      'discharge_bed': '🚪',
      
      // Appointment functions
      'list_appointments': '📅',
      'create_appointment': '🕐',
      
      // Equipment functions
      'list_equipment': '⚕️',
      'create_equipment': '🔧',
      'update_equipment_status': '🔄',
      
      // Supply functions
      'list_supplies': '📦',
      'create_supply': '📥',
      'update_supply_stock': '📊',
      
      // User functions
      'list_users': '👤',
      'create_user': '🆕',
      'update_user': '✏️',
      'delete_user': '🗑️',
      
      // Legacy functions
      'list_legacy_users': '👤',
      'create_legacy_user': '🆕',
      
      // Room functions
      'list_rooms': '🏠',
      'create_room': '🏗️'
    };
    
    return iconMap[functionName] || '⚡';
  };

  /**
   * Format MCP data responses for clean display
   */
  const formatMCPData = (data) => {
    if (!data) return '❌ No data available\n';
    
    console.log('🔍 formatMCPData received:', data); // Debug log
    
    // Handle MCP response array format
    if (Array.isArray(data)) {
      // Check if it's an array of MCP response objects with type and text
      if (data.length > 0 && data[0].type === 'text' && data[0].text) {
        try {
          const parsedData = JSON.parse(data[0].text);
          console.log('🔍 Parsed JSON from MCP array:', parsedData); // Debug log
          return formatMCPData(parsedData); // Recursive call with parsed data
        } catch (e) {
          console.log('🔍 Failed to parse JSON from MCP array:', e); // Debug log
          return `${data[0].text}\n`;
        }
      }
      
      // Handle regular array
      let result = `📋 **DATA RESULTS**\n📊 **Found ${data.length} Item(s)**\n\n`;
      data.forEach((item, i) => {
        result += `${i + 1}. ${formatResultItem(item)}\n`;
      });
      return result;
    }
    
    // Handle nested structure like { "patients": [...], "count": N }
    if (data.patients && Array.isArray(data.patients)) {
      const patients = data.patients;
      let result = `👥 **PATIENT REGISTRY**\n📊 **Found ${patients.length} Patient(s)**\n\n`;
      
      patients.forEach((patient, i) => {
        result += `🏥 **${i + 1}. ${patient.first_name} ${patient.last_name}**\n`;
        result += `   📋 **Patient ID:** ${patient.patient_number}\n`;
        if (patient.date_of_birth) result += `   📅 **Date of Birth:** ${patient.date_of_birth}\n`;
        if (patient.gender) result += `   👤 **Gender:** ${patient.gender}\n`;
        if (patient.phone) result += `   📞 **Phone:** ${patient.phone}\n`;
        if (patient.email) result += `   📧 **Email:** ${patient.email}\n`;
        if (patient.address) result += `   🏠 **Address:** ${patient.address}\n`;
        if (patient.blood_type) result += `   🩸 **Blood Type:** ${patient.blood_type}\n`;
        if (patient.allergies && patient.allergies !== 'null' && patient.allergies !== null) {
          result += `   ⚠️ **Allergies:** ${patient.allergies}\n`;
        }
        if (patient.medical_history && patient.medical_history !== 'null' && patient.medical_history !== null) {
          result += `   📝 **Medical History:** ${patient.medical_history}\n`;
        }
        if (patient.emergency_contact_name) {
          result += `   🆘 **Emergency Contact:** ${patient.emergency_contact_name}`;
          if (patient.emergency_contact_phone) result += ` (${patient.emergency_contact_phone})`;
          result += '\n';
        }
        result += '\n';
      });
      
      if (data.count && data.count !== patients.length) {
        result += `📈 *Total in database: ${data.count} patients*\n`;
      }
      
      result += `\n💡 **Quick Actions:**\n`;
      result += `• Create new patient: "Add new patient [Name]"\n`;
      result += `• Search patient: "Find patient [Name/ID]"\n`;
      result += `• Update records: "Update patient [ID]"\n`;
      
      return result;
    }
    
    // Handle departments
    if (data.departments && Array.isArray(data.departments)) {
      const departments = data.departments;
      let result = `🏢 **HOSPITAL DEPARTMENTS**\n📊 **Found ${departments.length} Department(s)**\n\n`;
      
      departments.forEach((dept, i) => {
        result += `🏥 **${i + 1}. ${dept.name}**\n`;
        result += `   🆔 **Department ID:** ${dept.department_id}\n`;
        if (dept.floor_number) result += `   🏗️ **Floor:** ${dept.floor_number}\n`;
        if (dept.phone) result += `   📞 **Phone:** ${dept.phone}\n`;
        if (dept.email) result += `   📧 **Email:** ${dept.email}\n`;
        if (dept.description) result += `   📝 **Description:** ${dept.description}\n`;
        if (dept.head_doctor_id) result += `   👨‍⚕️ **Head Doctor ID:** ${dept.head_doctor_id}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Department Actions:**\n`;
      result += `• Create department: "Add new department [Name]"\n`;
      result += `• Assign staff: "Assign staff to [Department]"\n`;
      result += `• Update info: "Update department [ID]"\n`;
      
      return result;
    }
    
    // Handle staff
    if (data.staff && Array.isArray(data.staff)) {
      const staff = data.staff;
      let result = `👨‍⚕️ **HOSPITAL STAFF**\n📊 **Found ${staff.length} Staff Member(s)**\n\n`;
      
      staff.forEach((member, i) => {
        result += `👤 **${i + 1}. ${member.position}**\n`;
        result += `   🆔 **Employee ID:** ${member.employee_id}\n`;
        if (member.department_id) result += `   🏢 **Department:** ${member.department_id}\n`;
        if (member.specialization) result += `   🎯 **Specialization:** ${member.specialization}\n`;
        if (member.status) result += `   📊 **Status:** ${member.status === 'active' ? '✅ Active' : '⏸️ Inactive'}\n`;
        if (member.hire_date) result += `   📅 **Hire Date:** ${member.hire_date}\n`;
        if (member.shift_pattern) result += `   ⏰ **Shift Pattern:** ${member.shift_pattern}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Staff Actions:**\n`;
      result += `• Add staff: "Add new staff member"\n`;
      result += `• Schedule shifts: "Update staff schedule"\n`;
      result += `• Assign department: "Transfer staff to [Department]"\n`;
      
      return result;
    }
    
    // Handle beds
    if (data.beds && Array.isArray(data.beds)) {
      const beds = data.beds;
      const availableBeds = beds.filter(bed => bed.status === 'available').length;
      const occupiedBeds = beds.filter(bed => bed.status === 'occupied').length;
      
      let result = `🛏️ **BED MANAGEMENT**\n📊 **Found ${beds.length} Bed(s)** | ✅ ${availableBeds} Available | 🔴 ${occupiedBeds} Occupied\n\n`;
      
      beds.forEach((bed, i) => {
        const statusIcon = bed.status === 'available' ? '✅' : bed.status === 'occupied' ? '🔴' : '⚠️';
        result += `${statusIcon} **${i + 1}. Bed ${bed.bed_number}**\n`;
        if (bed.room_id) result += `   🏠 **Room:** ${bed.room_id}\n`;
        if (bed.status) result += `   📊 **Status:** ${bed.status.toUpperCase()}\n`;
        if (bed.bed_type) result += `   🛏️ **Type:** ${bed.bed_type}\n`;
        if (bed.patient_id) result += `   👤 **Current Patient:** ${bed.patient_id}\n`;
        result += '\n';
      });
      
      if (availableBeds === 0) {
        result += `\n🚨 **ALERT: NO AVAILABLE BEDS**\n`;
        result += `⚡ **Emergency Actions:**\n`;
        result += `• Check room capacity for emergency beds\n`;
        result += `• Review discharge schedule\n`;
        result += `• Contact bed management team\n`;
      } else {
        result += `\n💡 **Bed Actions:**\n`;
        result += `• Assign patient: "Assign bed [Number] to patient [ID]"\n`;
        result += `• Discharge patient: "Discharge bed [Number]"\n`;
        result += `• Create emergency bed: "Add emergency bed"\n`;
      }
      
      return result;
    }
    
    // Handle appointments
    if (data.appointments && Array.isArray(data.appointments)) {
      const appointments = data.appointments;
      let result = `📅 **APPOINTMENT SCHEDULE**\n📊 **Found ${appointments.length} Appointment(s)**\n\n`;
      
      appointments.forEach((appt, i) => {
        result += `📋 **${i + 1}. Appointment**\n`;
        if (appt.appointment_date) result += `   📅 **Date & Time:** ${appt.appointment_date}\n`;
        if (appt.patient_id) result += `   👤 **Patient ID:** ${appt.patient_id}\n`;
        if (appt.doctor_id) result += `   👨‍⚕️ **Doctor ID:** ${appt.doctor_id}\n`;
        if (appt.department_id) result += `   🏢 **Department:** ${appt.department_id}\n`;
        if (appt.reason) result += `   🎯 **Reason:** ${appt.reason}\n`;
        if (appt.duration_minutes) result += `   ⏱️ **Duration:** ${appt.duration_minutes} minutes\n`;
        if (appt.notes) result += `   📝 **Notes:** ${appt.notes}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Appointment Actions:**\n`;
      result += `• Schedule new: "Book appointment for [Patient]"\n`;
      result += `• Reschedule: "Change appointment [ID]"\n`;
      result += `• Cancel: "Cancel appointment [ID]"\n`;
      
      return result;
    }
    
    // Handle equipment
    if (data.equipment && Array.isArray(data.equipment)) {
      const equipment = data.equipment;
      let result = `🏥 **MEDICAL EQUIPMENT**\n📊 **Found ${equipment.length} Equipment Item(s)**\n\n`;
      
      equipment.forEach((item, i) => {
        result += `⚕️ **${i + 1}. ${item.name}**\n`;
        if (item.equipment_id) result += `   🆔 **Equipment ID:** ${item.equipment_id}\n`;
        if (item.category_id) result += `   📂 **Category:** ${item.category_id}\n`;
        if (item.manufacturer) result += `   🏭 **Manufacturer:** ${item.manufacturer}\n`;
        if (item.model) result += `   📱 **Model:** ${item.model}\n`;
        if (item.location) result += `   📍 **Location:** ${item.location}\n`;
        if (item.status) {
          const statusIcon = item.status === 'operational' ? '✅' : item.status === 'maintenance' ? '🔧' : '❌';
          result += `   ${statusIcon} **Status:** ${item.status.toUpperCase()}\n`;
        }
        result += '\n';
      });
      
      result += `\n💡 **Equipment Actions:**\n`;
      result += `• Schedule maintenance: "Maintain equipment [ID]"\n`;
      result += `• Update status: "Update equipment [ID] status"\n`;
      result += `• Add equipment: "Add new equipment"\n`;
      
      return result;
    }
    
    // Handle supplies
    if (data.supplies && Array.isArray(data.supplies)) {
      const supplies = data.supplies;
      const lowStock = supplies.filter(item => item.current_stock <= item.minimum_stock_level).length;
      
      let result = `📦 **MEDICAL SUPPLIES**\n📊 **Found ${supplies.length} Supply Item(s)**`;
      if (lowStock > 0) result += ` | ⚠️ ${lowStock} Low Stock`;
      result += `\n\n`;
      
      supplies.forEach((item, i) => {
        const stockIcon = item.current_stock <= item.minimum_stock_level ? '⚠️' : '✅';
        result += `${stockIcon} **${i + 1}. ${item.name}**\n`;
        if (item.item_code) result += `   🆔 **Item Code:** ${item.item_code}\n`;
        if (item.current_stock !== undefined) result += `   📊 **Current Stock:** ${item.current_stock}\n`;
        if (item.unit_of_measure) result += `   📏 **Unit:** ${item.unit_of_measure}\n`;
        if (item.supplier) result += `   🏢 **Supplier:** ${item.supplier}\n`;
        if (item.location) result += `   📍 **Location:** ${item.location}\n`;
        if (item.expiry_date) result += `   ⏰ **Expiry Date:** ${item.expiry_date}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Supply Actions:**\n`;
      result += `• Restock: "Update stock for [Item Code]"\n`;
      result += `• Add supply: "Add new supply item"\n`;
      result += `• Check expiry: "Show expiring supplies"\n`;
      
      return result;
    }
    
    // Handle single objects
    if (typeof data === 'object') {
      return `✅ **RESULT:**\n${formatResultItem(data)}\n`;
    }
    
    // Handle simple values
    return `ℹ️ **INFO:** ${String(data)}\n`;
  };

  /**
   * Format individual result items for display
   */
  const formatResultItem = (item) => {
    if (!item) return 'No data';
    
    if (typeof item === 'string') {
      return item;
    }
    
    if (typeof item === 'object') {
      // For patient objects
      if (item.first_name && item.last_name) {
        let patientInfo = `${item.first_name} ${item.last_name}`;
        if (item.patient_number) patientInfo += ` (#${item.patient_number})`;
        if (item.date_of_birth) patientInfo += ` • Born: ${item.date_of_birth}`;
        if (item.phone) patientInfo += ` • Phone: ${item.phone}`;
        if (item.blood_type) patientInfo += ` • Blood Type: ${item.blood_type}`;
        return patientInfo;
      }
      // For department objects
      if (item.name && item.department_id) {
        let deptInfo = `${item.name} (ID: ${item.department_id})`;
        if (item.floor_number) deptInfo += ` • Floor ${item.floor_number}`;
        if (item.phone) deptInfo += ` • Phone: ${item.phone}`;
        return deptInfo;
      }
      // For staff objects
      if (item.user_id && item.position) {
        let staffInfo = `${item.position}`;
        if (item.employee_id) staffInfo += ` (#${item.employee_id})`;
        if (item.specialization) staffInfo += ` • ${item.specialization}`;
        if (item.department_id) staffInfo += ` • Dept: ${item.department_id}`;
        return staffInfo;
      }
      // For bed objects
      if (item.bed_number) {
        let bedInfo = `Bed ${item.bed_number}`;
        if (item.room_id) bedInfo += ` (Room ${item.room_id})`;
        if (item.status) bedInfo += ` • Status: ${item.status}`;
        if (item.bed_type) bedInfo += ` • Type: ${item.bed_type}`;
        return bedInfo;
      }
      // For appointment objects
      if (item.appointment_date && item.patient_id) {
        let apptInfo = `Appointment on ${item.appointment_date}`;
        if (item.doctor_id) apptInfo += ` with Dr. ${item.doctor_id}`;
        if (item.reason) apptInfo += ` • Reason: ${item.reason}`;
        return apptInfo;
      }
      // Generic object formatting
      const keys = Object.keys(item);
      if (keys.length > 0) {
        // Try to find a meaningful display field
        const nameField = keys.find(k => k.includes('name') || k.includes('title'));
        const idField = keys.find(k => k.includes('id') || k.includes('number'));
        
        if (nameField) {
          let result = `${item[nameField]}`;
          if (idField && item[idField]) result += ` (${item[idField]})`;
          return result;
        } else if (idField) {
          return `ID: ${item[idField]}`;
        } else {
          // Show first few key-value pairs
          return keys.slice(0, 2).map(k => `${k}: ${item[k]}`).join(', ');
        }
      }
    }
    
    return String(item);
  };

  /**
   * Disconnect from MCP server
   */
  const disconnect = async () => {
    if (aiMcpServiceRef.current) {
      await aiMcpServiceRef.current.disconnect();
    }
    setIsConnected(false);
    setShowSetup(true);
    setServerInfo(null);
    setMessages([]);
  };

  /**
   * Check server status
   */
  const checkStatus = async () => {
    if (aiMcpServiceRef.current) {
      try {
        const status = await aiMcpServiceRef.current.checkStatus();
        setServerInfo(status);
        
        if (status && !status.isConnected) {
          setIsConnected(false);
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: '🔌 MCP server connection lost. Please reconnect.',
            sender: 'ai',
            timestamp: new Date().toLocaleTimeString()
          }]);
        }
      } catch (error) {
        console.error('Status check failed:', error);
      }
    }
  };

  // Setup Panel - Claude Desktop Style
  if (showSetup) {
    return (
      <div className="h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Hospital Assistant
            </h1>
            <p className="text-gray-600">
              Connect to your hospital management system
            </p>
          </div>

          <div className="space-y-6">
            {/* OpenAI API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key
              </label>
              <input
                type="password"
                value={openaiApiKey}
                onChange={(e) => setOpenaiApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            {/* Advanced Configuration - Collapsible */}
            <div>
              <details className="group">
                <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  <span>Advanced Configuration</span>
                  <svg className="w-4 h-4 transform group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                
                <div className="mt-4 space-y-4">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Command</label>
                    <input
                      type="text"
                      value={mcpServerConfig.command}
                      onChange={(e) => setMcpServerConfig(prev => ({
                        ...prev,
                        command: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Arguments</label>
                    <textarea
                      value={mcpServerConfig.args ? mcpServerConfig.args.join('\n') : ''}
                      onChange={(e) => setMcpServerConfig(prev => ({
                        ...prev,
                        args: e.target.value.split('\n').filter(arg => arg.trim())
                      }))}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Working Directory</label>
                    <input
                      type="text"
                      value={mcpServerConfig.cwd || ''}
                      onChange={(e) => setMcpServerConfig(prev => ({
                        ...prev,
                        cwd: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm"
                    />
                  </div>
                </div>
              </details>
            </div>

            {/* Connection Status */}
            {connectionError && (
              <div className={`p-4 rounded-xl text-sm ${
                connectionError.includes('✅') 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                {connectionError}
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={async () => {
                  setConnectionError('');
                  try {
                    const response = await fetch('http://localhost:3001/mcp/status');
                    if (response.ok) {
                      setConnectionError('✅ MCP Process Manager is running and ready');
                    } else {
                      setConnectionError(`❌ Process Manager error: ${response.status}`);
                    }
                  } catch (error) {
                    setConnectionError(`❌ Cannot reach Process Manager: ${error.message}`);
                  }
                }}
                className="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-colors text-sm font-medium"
              >
                Test Connection
              </button>
              
              <button
                onClick={initializeService}
                disabled={isLoading || !openaiApiKey.trim()}
                className="w-full py-3 px-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-xl transition-all duration-200 font-medium"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Connecting...</span>
                  </div>
                ) : (
                  'Connect to Hospital System'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main Chat Interface - Claude Desktop Style
  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Claude-style Header */}
      <div className="border-b border-gray-200 px-6 py-4 bg-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Hospital Assistant</h1>
              {serverInfo && (
                <p className="text-sm text-gray-500">
                  Connected • {serverInfo.toolCount} tools • {aiMcpServiceRef.current?.getConversationSummary?.()?.messageCount || 0} messages in memory
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                if (aiMcpServiceRef.current) {
                  aiMcpServiceRef.current.resetConversation();
                  setMessages(prev => [...prev, {
                    id: Date.now(),
                    text: '🔄 **Conversation Reset** - Memory cleared. Starting fresh!',
                    sender: 'ai',
                    timestamp: new Date().toLocaleTimeString()
                  }]);
                }
              }}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Reset Conversation Memory"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              onClick={checkStatus}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Check Status"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
            <button
              onClick={disconnect}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Disconnect"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Container - Claude Style */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-center px-6">
              <div className="max-w-md">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                  </svg>
                </div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                  Hospital Management Assistant
                </h2>
                <p className="text-gray-600 mb-6">
                  I'm your AI assistant for hospital management tasks. I can help you manage patients, staff, departments, equipment, and more through natural conversation.
                </p>
                <div className="grid grid-cols-1 gap-3 text-sm">
                  <div className="bg-gray-50 rounded-lg p-3 text-left">
                    <div className="font-medium text-gray-900 mb-1">Try asking:</div>
                    <div className="text-gray-600">"List all patients" or "Create a new department"</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className="px-6 py-6 border-b border-gray-100 last:border-b-0">
              <div className="flex space-x-4">
                {message.sender === 'user' ? (
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                ) : (
                  <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                  </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <div className="prose prose-sm max-w-none">
                    <div 
                      className="whitespace-pre-wrap text-gray-900 leading-relaxed"
                      dangerouslySetInnerHTML={{
                        __html: formatMessageText(message.text)
                      }}
                    />
                  </div>
                  <div className="mt-2 text-xs text-gray-400">
                    {message.timestamp}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="px-6 py-6 border-b border-gray-100">
              <div className="flex space-x-4">
                <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 text-gray-500">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Claude-style Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Message Hospital Assistant..."
              disabled={!isConnected || isLoading}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none disabled:bg-gray-50 disabled:text-gray-500"
              style={{
                minHeight: '48px',
                maxHeight: '120px'
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!isConnected || isLoading || !inputMessage.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 text-white rounded-lg transition-colors duration-200"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DirectMCPChatbot;
