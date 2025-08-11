import React, { useState, useEffect, useRef } from 'react';
import { LogOut, User, Settings } from 'lucide-react';
import DirectHttpAIMCPService from '../services/directHttpAiMcpService.js';

const DirectMCPChatbot = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(false); // Start with false since auth is handled by parent
  
  // Configuration state - get API key from authenticated user
  const [openaiApiKey, setOpenaiApiKey] = useState(user?.apiKey || import.meta.env.VITE_OPENAI_API_KEY || '');
  
  const [serverInfo, setServerInfo] = useState(null);
  const [connectionError, setConnectionError] = useState('');
  const [expandedThinking, setExpandedThinking] = useState({}); // Track which thinking messages are expanded
  const [isInputFocused, setIsInputFocused] = useState(false); // Track input focus state
  
  // Auto-scroll to bottom only when new messages are added, not on timer updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]); // Only trigger on message count change, not message content changes

  // Auto-connect when component mounts if user is authenticated
  useEffect(() => {
    if (user && openaiApiKey && !isConnected && !showSetup) {
      console.log('🔄 Auto-connecting for authenticated user...');
      initializeService();
    }
  }, [user, openaiApiKey, isConnected, showSetup]); // Dependencies that should trigger auto-connection

  // Component to display thinking duration
  const ThinkingDuration = React.memo(({ startTime }) => {
    const [duration, setDuration] = React.useState(1);
    
    React.useEffect(() => {
      if (!startTime) return;
      
      // Update every 500ms instead of 100ms for better performance
      const interval = setInterval(() => {
        setDuration(Math.ceil((Date.now() - startTime) / 1000));
      }, 500);
      
      return () => clearInterval(interval);
    }, [startTime]);
    
    return <span>{duration}s</span>;
  });
  
  const aiMcpServiceRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const lastMessageCountRef = useRef(0);
  const inputFieldRef = useRef(null); // Add ref for input field

  // Controlled scroll function
  const scrollToBottom = React.useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  // Auto-scroll only when new messages are added, with smart scrolling
  useEffect(() => {
    const currentMessageCount = messages.length;
    if (currentMessageCount > lastMessageCountRef.current) {
      // Only scroll if user is near the bottom (within 100px) or if it's the first message
      if (messagesContainerRef.current) {
        const container = messagesContainerRef.current;
        const isNearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 100;
        
        if (isNearBottom || currentMessageCount === 1) {
          setTimeout(scrollToBottom, 50); // Small delay to ensure DOM is updated
        }
      } else {
        setTimeout(scrollToBottom, 50);
      }
    }
    lastMessageCountRef.current = currentMessageCount;
  }, [messages.length, scrollToBottom]);

  // Add keyboard shortcut to focus input (Ctrl/Cmd + /)
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        if (inputFieldRef.current && isConnected) {
          inputFieldRef.current.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isConnected]);

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
      aiMcpServiceRef.current = new DirectHttpAIMCPService();
      
      console.log('🚀 Initializing Direct HTTP MCP Service...');
      
      const initialized = await aiMcpServiceRef.current.initialize(openaiApiKey);
      
      if (initialized) {
        setIsConnected(true);
        setShowSetup(false);
        
        const info = aiMcpServiceRef.current.getServerInfo();
        setServerInfo(info);
        
        setMessages([{
          id: Date.now(),
          text: `👋 Welcome to Hospital Agent! How can I help you today? 🏥`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString()
        }]);
        
        // Auto-focus the input field after successful connection
        setTimeout(() => {
          if (inputFieldRef.current) {
            inputFieldRef.current.focus();
          }
        }, 100); // Reduced delay for faster UI response
        
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
   * Smart conversation flow: only show thinking when tools are needed
   */
  const sendMessageClaudeStyle = async () => {
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

    // Check if this request likely needs tool calls
    const toolKeywords = ['list', 'show', 'get', 'find', 'search', 'create', 'add', 'update', 'delete', 'assign', 'check', 'manage', 'patient', 'staff', 'bed', 'department', 'appointment', 'equipment', 'supply'];
    const needsTools = toolKeywords.some(keyword => 
      userMessage.toLowerCase().includes(keyword)
    );

    let thinkingMessageId = null;
    let thinkingStartTime = null;

    try {
      // Only show thinking if we expect tool usage
      if (needsTools) {
        thinkingStartTime = Date.now();
        thinkingMessageId = Date.now() + Math.random();
        
        // Generate contextual thinking message based on user input
        let thinkingText = 'Thinking about ';
        if (userMessage.toLowerCase().includes('list') || userMessage.toLowerCase().includes('show')) {
          thinkingText += 'listing ';
        } else if (userMessage.toLowerCase().includes('create') || userMessage.toLowerCase().includes('add')) {
          thinkingText += 'creating ';
        } else if (userMessage.toLowerCase().includes('find') || userMessage.toLowerCase().includes('search')) {
          thinkingText += 'finding ';
        } else if (userMessage.toLowerCase().includes('update') || userMessage.toLowerCase().includes('assign')) {
          thinkingText += 'updating ';
        } else {
          thinkingText += 'processing ';
        }

        // Add the subject based on keywords
        if (userMessage.toLowerCase().includes('patient')) {
          thinkingText += 'patient information';
        } else if (userMessage.toLowerCase().includes('staff')) {
          thinkingText += 'staff records';
        } else if (userMessage.toLowerCase().includes('bed')) {
          thinkingText += 'available beds';
        } else if (userMessage.toLowerCase().includes('department')) {
          thinkingText += 'departments';
        } else if (userMessage.toLowerCase().includes('appointment')) {
          thinkingText += 'appointments';
        } else if (userMessage.toLowerCase().includes('equipment')) {
          thinkingText += 'equipment status';
        } else if (userMessage.toLowerCase().includes('supply')) {
          thinkingText += 'supply inventory';
        } else {
          thinkingText += 'your request';
        }

        const thinkingMessage = {
          id: thinkingMessageId,
          text: thinkingText,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isThinking: true,
          startTime: thinkingStartTime
        };
        setMessages(prev => [...prev, thinkingMessage]);
      }

      // Process the request
      const response = await aiMcpServiceRef.current.processRequest(userMessage);
      
      // Remove thinking message if present
      if (thinkingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== thinkingMessageId));
        
        // Remove artificial delay for faster response
        // await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      if (response.success) {
        // Show tool execution if tools were called
        if (response.functionCalls && response.functionCalls.length > 0) {
          response.functionCalls.forEach((call, index) => {
            // Create contextual thinking message for each tool
            let thinkingText = '';
            switch (call.function) {
              case 'search_patients':
                thinkingText = `Great! I found a patient named ${call.arguments?.first_name || 'the patient'}.`;
                break;
              case 'list_patients':
                thinkingText = 'I can see the patient registry with all available patients.';
                break;
              case 'list_appointments':
                thinkingText = `I can see ${call.arguments?.patient_id ? call.arguments.patient_id + ' has' : 'there are'} appointment${call.result && Array.isArray(call.result) && call.result.length !== 1 ? 's' : ''} scheduled.`;
                break;
              case 'list_beds':
                thinkingText = "Identified patient's bed assignment and prepared overview.";
                break;
              case 'list_departments':
                thinkingText = 'I can see all hospital departments and their information.';
                break;
              case 'list_staff':
                thinkingText = 'I can see the hospital staff directory.';
                break;
              case 'get_patient_by_id':
                thinkingText = `Found detailed information for patient ${call.arguments?.patient_id || 'ID'}.`;
                break;
              case 'get_staff_by_id':
                thinkingText = `Located staff member ${call.arguments?.staff_id || 'information'}.`;
                break;
              case 'create_patient':
                thinkingText = 'Successfully created new patient record.';
                break;
              case 'create_appointment':
                thinkingText = 'Successfully scheduled new appointment.';
                break;
              default:
                thinkingText = `Executed ${call.function.replace(/_/g, ' ')} successfully.`;
            }

            const toolMessage = {
              id: Date.now() + index + 100,
              text: thinkingText,
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString(),
              isThinking: true,
              toolFunction: call.function,
              startTime: Date.now() // No artificial delay
            };
            setMessages(prev => [...prev, toolMessage]);
          });
        }

        // Final response with the processed data
        const finalResponse = {
          id: Date.now() + 1000,
          text: response.response || response.message || 'Here\'s what I found based on your request.',
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isFinalAnswer: true
        };
        setMessages(prev => [...prev, finalResponse]);
        
      } else {
        // Direct error response without thinking for simple errors
        const errorResponse = {
          id: Date.now() + 1000,
          text: `I apologize, but I encountered an error: ${response.error || 'Unknown error occurred'}\n\nPlease try rephrasing your request or let me know if you need help with something specific.`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isError: true
        };
        setMessages(prev => [...prev, errorResponse]);
      }
      
    } catch (error) {
      console.error('❌ Send message failed:', error);
      
      // Remove thinking message if present
      if (thinkingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== thinkingMessageId));
      }

      // Direct error message
      const errorMsg = {
        id: Date.now() + 1000,
        text: `I'm having trouble processing your request: ${error.message}\n\nThis might be a temporary connection issue. Please try again in a moment.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      
      // Auto-focus the input field after sending message
      setTimeout(() => {
        if (inputFieldRef.current) {
          inputFieldRef.current.focus();
        }
      }, 100); // Small delay to ensure state updates are complete
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
   * Handle sending messages with Claude-style conversation flow
   */
  const handleSendMessage = () => {
    sendMessageClaudeStyle();
  };

  /**
   * Format MCP data responses for clean display
   */
  // eslint-disable-next-line no-unused-vars
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

  // Setup Panel - Dark Chatbot Style
  if (showSetup) {
    return (
      <div className="h-screen bg-[#1a1a1a] flex flex-col text-white">
        {/* Header */}
        <div className="border-b border-gray-700 px-4 py-3 bg-[#1a1a1a]">
          <div className="flex items-center space-x-3">
            <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-lg">
              H
            </div>
            <div>
              <h1 className="text-sm font-medium text-white">Hospital Assistant</h1>
              <p className="text-xs text-gray-400">Setup & Configuration</p>
            </div>
          </div>
        </div>

        {/* Main Setup Content */}
        <div className="flex-1 overflow-y-auto bg-[#1a1a1a] flex items-center justify-center">
          <div className="max-w-lg w-full mx-4">
            {/* Welcome Section */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-2xl font-medium text-white">H</span>
              </div>
              <h1 className="text-2xl font-medium text-white mb-3">
                Welcome to Hospital Assistant
              </h1>
              <p className="text-gray-400 mb-6 text-sm">
                Connect to your hospital management system to get started with AI-powered healthcare administration.
              </p>
            </div>

            {/* Configuration Form */}
            <div className="space-y-6">
              {/* API Key Section */}
              <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-700">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-white font-medium">OpenAI API Key</h3>
                    <p className="text-xs text-gray-400">Required for AI conversation processing</p>
                  </div>
                </div>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-600 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-white placeholder-gray-400 text-sm"
                />
              </div>

              {/* Server Status */}
              <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-700">
                <h4 className="text-white font-medium mb-2 text-sm">📡 Server Connection</h4>
                <p className="text-xs text-gray-400">
                  Connecting directly to FastMCP server at: <br/>
                  <code className="text-green-400">http://127.0.0.1:8000</code>
                </p>
              </div>

              {/* Connection Status */}
              {connectionError && (
                <div className={`p-4 rounded-lg text-sm border ${
                  connectionError.includes('✅') 
                    ? 'bg-green-900/20 text-green-400 border-green-800' 
                    : 'bg-red-900/20 text-red-400 border-red-800'
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
                      const response = await fetch('http://127.0.0.1:8000/');
                      if (response.ok) {
                        setConnectionError('✅ FastMCP Server is running and ready');
                      } else {
                        setConnectionError(`❌ Server error: ${response.status}`);
                      }
                    } catch (error) {
                      setConnectionError(`❌ Cannot reach FastMCP Server: ${error.message}\nMake sure comprehensive_server.py is running on port 8000`);
                    }
                  }}
                  className="w-full py-3 px-4 bg-[#333] hover:bg-[#404040] text-white rounded-lg transition-colors text-sm font-medium border border-gray-600"
                >
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Test Server Connection</span>
                  </div>
                </button>
                
                <button
                  onClick={initializeService}
                  disabled={isLoading || !openaiApiKey.trim()}
                  className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 font-medium"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Connecting to Hospital System...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span>Connect to Hospital System</span>
                    </div>
                  )}
                </button>
              </div>

              {/* Quick Tips */}
              <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-700">
                <h4 className="text-white font-medium mb-2 text-sm">Quick Tips:</h4>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Make sure comprehensive_server.py is running on port 8000</li>
                  <li>• Your OpenAI API key needs GPT-4 access for best results</li>
                  <li>• No process manager needed - direct HTTP connection</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main Chat Interface - Claude Desktop Style
  return (
    <div className="h-screen bg-[#1a1a1a] flex flex-col text-white">
      {/* Claude-style Header */}
      <div className="border-b border-gray-700 px-4 py-3 bg-[#1a1a1a]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-lg">
              H
            </div>
            <div>
              <h1 className="text-sm font-medium text-white">Hospital Assistant</h1>
              {serverInfo && (
                <p className="text-xs text-gray-400">
                  Connected • {serverInfo.toolCount} tools • {aiMcpServiceRef.current?.getConversationSummary?.()?.messageCount || 0} messages in memory
                </p>
              )}
            </div>
          </div>
          
          {/* User Info and Actions */}
          <div className="flex items-center space-x-3">
            {/* User Profile */}
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">
                  {user?.fullName ? user.fullName.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="hidden sm:block">
                <p className="text-xs text-white font-medium">{user?.fullName || 'User'}</p>
                <p className="text-xs text-gray-400">{user?.role || 'Staff'}</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-1">
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
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                title="Reset Conversation Memory"
              >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button
              onClick={checkStatus}
              className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
              title="Check Status"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
            <button
              onClick={disconnect}
              className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
              title="Disconnect"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            {/* Settings Button */}
            <button
              onClick={() => setShowSetup(true)}
              className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            
            {/* Logout Button */}
            <button
              onClick={onLogout}
              className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-md transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container - Claude Style */}
      <div 
        ref={messagesContainerRef} 
        className="flex-1 overflow-y-auto bg-[#1a1a1a]"
        onClick={() => {
          // Focus input when clicking anywhere in the chat area, but not when selecting text
          const selection = window.getSelection();
          if (inputFieldRef.current && isConnected && selection.toString().length === 0) {
            inputFieldRef.current.focus();
          }
        }}
      >
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-center px-6">
              <div className="max-w-md">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <span className="text-2xl font-medium text-white">H</span>
                </div>
                <h2 className="text-xl font-medium text-white mb-3">
                  Welcome back, {user?.fullName?.split(' ')[0] || 'User'}!
                </h2>
                <p className="text-gray-400 mb-6 text-sm">
                  I'm your AI assistant for hospital management tasks. I can help you manage patients, staff, departments, equipment, and more through natural conversation.
                </p>
                {/* <div className="grid grid-cols-1 gap-3 text-sm">
                  <div className="bg-[#2a2a2a] rounded-lg p-3 text-left">
                    <div className="font-medium text-white mb-1">Try asking:</div>
                    <div className="text-gray-400">"List all patients" or "Create a new department"</div>
                  </div>
                </div> */}
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`px-4 py-2 ${
              message.isThinking ? 'bg-[#1a1a1a]' : 
              message.isFinalAnswer ? 'bg-[#1a1a1a]' : 
              message.isError ? 'bg-[#1a1a1a]' : 'bg-[#1a1a1a]'
            }`}>
              {message.sender === 'user' ? (
                // User message - aligned to the right
                <div className="flex justify-end">
                  <div className="max-w-[80%]">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap leading-relaxed text-sm text-white bg-slate-700 rounded-2xl px-4 py-2">
                        <div dangerouslySetInnerHTML={{ __html: formatMessageText(message.text) }} />
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // AI message - aligned to the left (existing layout)
                <div className="flex space-x-3">
                  <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-medium text-white shadow-lg">
                    {message.isThinking ? (
                      <div className="w-3 h-3 border border-gray-400 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      'H'
                    )}
                  </div>
                
                <div className="flex-1 min-w-0">
                  {message.isThinking && (
                    <div className="mb-1">
                      <button
                        onClick={() => setExpandedThinking(prev => ({
                          ...prev,
                          [message.id]: !prev[message.id]
                        }))}
                        className="flex items-center space-x-2 text-xs text-gray-500 italic hover:text-gray-400 transition-colors w-full justify-between"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-400">🔧</span>
                          <span className="font-mono text-blue-400">{message.toolFunction || 'thinking'}</span>
                        </div>
                        <span className="ml-auto flex items-center space-x-1">
                          <ThinkingDuration startTime={message.startTime} />
                          <svg 
                            className={`w-3 h-3 transform transition-transform ${expandedThinking[message.id] ? 'rotate-180' : ''}`} 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </span>
                      </button>
                      {expandedThinking[message.id] && (
                        <div className="mt-2 text-sm text-gray-300 pl-6">
                          {message.text}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Tool Call Display */}
                  {message.isToolCall && (
                    <div className="mb-2">
                      <div className="flex items-center space-x-2 text-xs text-gray-400 mb-1">
                        <span className="text-blue-400">🔧</span>
                        <span>Tool Execution</span>
                      </div>
                    </div>
                  )}
                  
                  <div className="prose prose-sm max-w-none">
                    {(!message.isThinking || expandedThinking[message.id]) && (
                      <div 
                        className={`whitespace-pre-wrap leading-relaxed text-sm ${
                          message.isThinking ? 'text-gray-300' :
                          message.isFinalAnswer ? 'text-white' :
                          message.isError ? 'text-red-400' :
                          message.isToolCall ? 'text-blue-200 bg-gray-800 p-3 rounded-lg border-l-2 border-blue-500' :
                          'text-white'
                        }`}
                        dangerouslySetInnerHTML={{
                          __html: formatMessageText(message.text)
                        }}
                      />
                    )}
                  </div>
                </div>
              </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="px-4 py-2 bg-[#1a1a1a]">
              <div className="flex space-x-3">
                <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                  <div className="w-3 h-3 border border-gray-400 border-t-white rounded-full animate-spin"></div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="mb-1">
                    <button
                      onClick={() => setExpandedThinking(prev => ({
                        ...prev,
                        ['loading']: !prev['loading']
                      }))}
                      className="flex items-center space-x-2 text-xs text-gray-500 italic hover:text-gray-400 transition-colors"
                    >
                      <span>Processing your request...</span>
                      <span className="ml-auto flex items-center space-x-1">
                        <span>0s</span>
                        <svg 
                          className={`w-3 h-3 transform transition-transform ${expandedThinking['loading'] ? 'rotate-180' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </span>
                    </button>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-300 mb-1">
                    <span className="text-blue-400">🔍</span>
                    <span className="text-xs text-gray-400">Request Analysis</span>
                  </div>
                  {expandedThinking['loading'] && (
                    <div className="text-sm text-gray-300">
                      Analyzing your request and determining the best approach...
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Action Buttons Above Input */}
      <div className="bg-[#1a1a1a] px-4 py-1">
        <div className="max-w-4xl mx-auto">
          {/* Desktop: 1 row 4 columns, Mobile: 2 rows 2 columns */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-1">
            {/* View All Patients */}
            <button
              onClick={() => {
                setInputMessage("List all patients");
                setTimeout(() => {
                  if (inputFieldRef.current) {
                    inputFieldRef.current.focus();
                  }
                }, 100);
              }}
              className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md px-1.5 py-1 sm:px-2 sm:py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
              title="View all patients"
            >
              <span className="font-medium">View Patients</span>
            </button>

            {/* Check Bed Status */}
            <button
              onClick={() => {
                setInputMessage("Show bed availability");
                setTimeout(() => {
                  if (inputFieldRef.current) {
                    inputFieldRef.current.focus();
                  }
                }, 100);
              }}
              className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md px-1.5 py-1 sm:px-2 sm:py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
              title="Check bed availability"
            >
              <span className="font-medium">Bed Status</span>
            </button>

            {/* Emergency Alert */}
            <button
              onClick={() => {
                setInputMessage("Show emergency status and available emergency beds");
                setTimeout(() => {
                  if (inputFieldRef.current) {
                    inputFieldRef.current.focus();
                  }
                }, 100);
              }}
              className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md px-1.5 py-1 sm:px-2 sm:py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
              title="Emergency status"
            >
              <span className="font-medium">Emergency</span>
            </button>

            {/* Today's Schedule */}
            <button
              onClick={() => {
                setInputMessage("Show today's appointments");
                setTimeout(() => {
                  if (inputFieldRef.current) {
                    inputFieldRef.current.focus();
                  }
                }, 100);
              }}
              className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md px-1.5 py-1 sm:px-2 sm:py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
              title="Today's appointments"
            >
              <span className="font-medium">Today's Schedule</span>
            </button>
          </div>
        </div>
      </div>

      {/* Modern Chat Input - Two Row Layout */}
      <div className="bg-[#1a1a1a] px-4 py-2">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            {/* Main Input Container - Rounded Rectangle */}
            <div className={`bg-[#2a2a2a] rounded-3xl border px-4 py-4 transition-colors duration-200 ${
              isInputFocused ? 'border-blue-500' : 'border-gray-600'
            }`}>
              
              {/* First Row - Text Input (Full Width) */}
              <div className="mb-3">
                <textarea
                  ref={inputFieldRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  onFocus={() => setIsInputFocused(true)}
                  onBlur={() => setIsInputFocused(false)}
                  placeholder={isConnected ? "Ask anything (Ctrl+/ to focus)" : "Ask anything"}
                  disabled={!isConnected || isLoading}
                  rows={1}
                  className="w-full bg-transparent border-none outline-none resize-none text-white placeholder-gray-400 text-base"
                  style={{
                    minHeight: '24px',
                    maxHeight: '120px'
                  }}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = e.target.scrollHeight + 'px';
                  }}
                />
              </div>
              
              {/* Second Row - Icons */}
              <div className="flex items-center justify-between">
                {/* Left Side - Plus and Tools Icons */}
                <div className="flex items-center space-x-3">
                  {/* Plus Button */}
                  <button
                    className="text-gray-400 hover:text-white transition-colors p-1"
                    title="Add attachment"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                  
                  {/* Tools Button */}
                  <button
                    className="text-gray-400 hover:text-white transition-colors p-1 flex items-center space-x-2"
                    title="Tools"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                    </svg>
                    <span className="text-sm">MCP</span>
                  </button>
                </div>
                
                {/* Right Side - Microphone and Send Icons */}
                <div className="flex items-center space-x-3">
                  {/* Microphone Button */}
                  <button
                    className="text-gray-400 hover:text-white transition-colors p-1"
                    title="Voice input"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </button>
                  
                  {/* Send Button - Circular */}
                  <button
                    onClick={handleSendMessage}
                    disabled={!isConnected || isLoading || !inputMessage.trim()}
                    className="w-8 h-8 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 text-white rounded-full flex items-center justify-center transition-colors duration-200"
                    title="Send message"
                  >
                    {isLoading ? (
                      <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DirectMCPChatbot;
