/**
 * MCP Bridge Service - Handles communication with the MCP bridge server
 */

import axios from 'axios';

class MCPBridgeService {
  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  }

  // List all available tools
  async listTools() {
    try {
      const response = await this.client.get('/tools');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to list tools: ${error.message}`);
    }
  }

  // Call a specific tool
  async callTool(toolName, args = {}) {
    try {
      const response = await this.client.post(`/tools/${toolName}`, args);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to call tool ${toolName}: ${error.message}`);
    }
  }

  // Query analyzer that determines which tools to call based on user intent
  async analyzeAndExecuteQuery(userMessage) {
    try {
      // Simple keyword-based analysis to determine what data the user wants
      const message = userMessage.toLowerCase();
      
      if (message.includes('patient') || message.includes('arivu')) {
        if (message.includes('list') || message.includes('all') || message.includes('show')) {
          return await this.listPatients();
        } else if (message.includes('arivu') || message.includes('specific patient')) {
          // For now, list all patients since we need to find the specific patient
          return await this.listPatients();
        }
      } else if (message.includes('bed')) {
        if (message.includes('available') || message.includes('free')) {
          return await this.listBeds({ status: 'available' });
        } else {
          return await this.listBeds();
        }
      } else if (message.includes('appointment')) {
        if (message.includes('today')) {
          const today = new Date().toISOString().split('T')[0];
          return await this.listAppointments({ date: today });
        } else {
          return await this.listAppointments();
        }
      } else if (message.includes('staff') || message.includes('doctor') || message.includes('nurse')) {
        return await this.listStaff();
      } else if (message.includes('equipment')) {
        return await this.listEquipment();
      } else if (message.includes('supply') || message.includes('inventory')) {
        if (message.includes('low') || message.includes('stock')) {
          return await this.listSupplies({ low_stock_only: true });
        } else {
          return await this.listSupplies();
        }
      } else if (message.includes('department')) {
        return await this.listDepartments();
      } else if (message.includes('room')) {
        return await this.listRooms();
      } else {
        // Default: show basic hospital overview
        const [patients, beds, staff] = await Promise.all([
          this.listPatients().catch(() => null),
          this.listBeds().catch(() => null),
          this.listStaff().catch(() => null)
        ]);
        
        return {
          type: 'overview',
          description: 'Hospital system overview',
          data: {
            patients: patients?.data || [],
            beds: beds?.data || [],
            staff: staff?.data || []
          }
        };
      }
    } catch (error) {
      console.error('Query analysis failed:', error);
      throw error;
    }
  }

  // Convenience methods for common operations

  // User operations
  async createUser(userData) {
    return this.client.post('/users', userData);
  }

  async listUsers() {
    return this.client.get('/users');
  }

  async getUser(userId) {
    return this.client.get(`/users/${userId}`);
  }

  // Patient operations
  async createPatient(patientData) {
    return this.client.post('/patients', patientData);
  }

  async listPatients() {
    return this.client.get('/patients');
  }

  async getPatient(patientId) {
    return this.client.get(`/patients/${patientId}`);
  }

  // Department operations
  async createDepartment(departmentData) {
    return this.client.post('/departments', departmentData);
  }

  async listDepartments() {
    return this.client.get('/departments');
  }

  async getDepartment(departmentId) {
    return this.client.get(`/departments/${departmentId}`);
  }

  // Bed operations
  async createBed(bedData) {
    return this.client.post('/beds', bedData);
  }

  async listBeds(status = null) {
    const params = status ? { status } : {};
    return this.client.get('/beds', { params });
  }

  async assignBed(bedId, assignmentData) {
    return this.client.post(`/beds/${bedId}/assign`, assignmentData);
  }

  async dischargeBed(bedId, dischargeData = {}) {
    return this.client.post(`/beds/${bedId}/discharge`, dischargeData);
  }

  // Staff operations
  async listStaff(departmentId = null, status = null) {
    const params = {};
    if (departmentId) params.department_id = departmentId;
    if (status) params.status = status;
    return this.client.get('/staff', { params });
  }

  // Equipment operations
  async listEquipment(status = null, departmentId = null) {
    const params = {};
    if (status) params.status = status;
    if (departmentId) params.department_id = departmentId;
    return this.client.get('/equipment', { params });
  }

  // Supply operations
  async listSupplies(lowStockOnly = false) {
    return this.client.get('/supplies', { 
      params: { low_stock_only: lowStockOnly } 
    });
  }

  // Appointment operations
  async listAppointments(doctorId = null, patientId = null, date = null) {
    const params = {};
    if (doctorId) params.doctor_id = doctorId;
    if (patientId) params.patient_id = patientId;
    if (date) params.date = date;
    return this.client.get('/appointments', { params });
  }

  // Smart query execution based on natural language
  async executeSmartQuery(query) {
    const lowerQuery = query.toLowerCase();
    
    try {
      // Simple keyword-based routing for common queries
      if (lowerQuery.includes('user') && lowerQuery.includes('list')) {
        const response = await this.listUsers();
        return {
          type: 'users',
          data: response.data,
          description: 'List of all users in the system'
        };
      }
      
      if (lowerQuery.includes('patient') && lowerQuery.includes('list')) {
        const response = await this.listPatients();
        return {
          type: 'patients',
          data: response.data,
          description: 'List of all patients in the system'
        };
      }
      
      if (lowerQuery.includes('department') && lowerQuery.includes('list')) {
        const response = await this.listDepartments();
        return {
          type: 'departments',
          data: response.data,
          description: 'List of all departments in the hospital'
        };
      }
      
      if (lowerQuery.includes('bed') && (lowerQuery.includes('available') || lowerQuery.includes('free'))) {
        const response = await this.listBeds('available');
        return {
          type: 'beds',
          data: response.data,
          description: 'List of available beds'
        };
      }
      
      if (lowerQuery.includes('bed') && lowerQuery.includes('list')) {
        const response = await this.listBeds();
        return {
          type: 'beds',
          data: response.data,
          description: 'List of all beds in the hospital'
        };
      }
      
      if (lowerQuery.includes('staff') && lowerQuery.includes('list')) {
        const response = await this.listStaff();
        return {
          type: 'staff',
          data: response.data,
          description: 'List of all staff members'
        };
      }
      
      if (lowerQuery.includes('equipment') && lowerQuery.includes('list')) {
        const response = await this.listEquipment();
        return {
          type: 'equipment',
          data: response.data,
          description: 'List of all equipment'
        };
      }
      
      if (lowerQuery.includes('supply') || lowerQuery.includes('supplies')) {
        if (lowerQuery.includes('low') || lowerQuery.includes('stock')) {
          const response = await this.listSupplies(true);
          return {
            type: 'supplies',
            data: response.data,
            description: 'List of low stock supplies'
          };
        } else {
          const response = await this.listSupplies();
          return {
            type: 'supplies',
            data: response.data,
            description: 'List of all supplies'
          };
        }
      }
      
      if (lowerQuery.includes('appointment') && lowerQuery.includes('list')) {
        const response = await this.listAppointments();
        return {
          type: 'appointments',
          data: response.data,
          description: 'List of all appointments'
        };
      }
      
      // If no specific query matched, return available tools
      const tools = await this.listTools();
      return {
        type: 'tools',
        data: tools,
        description: 'Available tools in the hospital management system'
      };
      
    } catch (error) {
      throw new Error(`Failed to execute query: ${error.message}`);
    }
  }
}

export default MCPBridgeService;
