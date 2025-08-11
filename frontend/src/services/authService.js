/**
 * Mock Authentication Service for Hospital Management System
 * In a real application, this would connect to your backend API
 */

class AuthService {
  constructor() {
    this.baseURL = 'http://localhost:8000'; // Your FastAPI backend
    this.storageKey = 'hospital_users_db';
    this.initializeDefaultUsers();
  }

  /**
   * Initialize default demo users in localStorage if not exists
   */
  initializeDefaultUsers() {
    const existingUsers = this.getStoredUsers();
    if (existingUsers.length === 0) {
      const defaultUsers = [
        {
          id: '1',
          email: 'admin@hospital.com',
          password: 'admin123', // In real app, this would be hashed
          fullName: 'Dr. Administrator',
          role: 'admin',
          department: 'Administration',
          createdAt: new Date().toISOString()
        },
        {
          id: '2', 
          email: 'doctor@hospital.com',
          password: 'doctor123',
          fullName: 'Dr. Sarah Johnson',
          role: 'doctor',
          department: 'Cardiology',
          createdAt: new Date().toISOString()
        },
        {
          id: '3',
          email: 'nurse@hospital.com',
          password: 'nurse123',
          fullName: 'Mary Wilson',
          role: 'nurse',
          department: 'Emergency',
          createdAt: new Date().toISOString()
        }
      ];
      
      localStorage.setItem(this.storageKey, JSON.stringify(defaultUsers));
    }
  }

  /**
   * Get stored users from localStorage
   */
  getStoredUsers() {
    try {
      const users = localStorage.getItem(this.storageKey);
      return users ? JSON.parse(users) : [];
    } catch (error) {
      console.error('Error reading stored users:', error);
      return [];
    }
  }

  /**
   * Store users to localStorage
   */
  storeUsers(users) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(users));
      return true;
    } catch (error) {
      console.error('Error storing users:', error);
      return false;
    }
  }

  /**
   * Simulate user sign in
   */
  async signIn(email, password) {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Get all stored users (demo + registered users)
      const allUsers = this.getStoredUsers();

      // Find user by email
      const user = allUsers.find(u => u.email.toLowerCase() === email.toLowerCase());
      
      if (!user) {
        throw new Error('Invalid email or password');
      }

      // Validate password
      if (user.password !== password) {
        throw new Error('Invalid email or password');
      }

      // Return user data without password
      const { password: _, ...userWithoutPassword } = user;

      return {
        success: true,
        user: userWithoutPassword,
        token: `mock_token_${user.id}_${Date.now()}` // In real app, this would be a JWT
      };

    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Simulate user sign up
   */
  async signUp(userData) {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Simple validation
      if (!userData.email || !userData.password || !userData.fullName) {
        throw new Error('All fields are required');
      }

      if (userData.password.length < 6) {
        throw new Error('Password must be at least 6 characters long');
      }

      // Get existing users
      const existingUsers = this.getStoredUsers();
      
      // Check if user already exists
      const existingUser = existingUsers.find(u => 
        u.email.toLowerCase() === userData.email.toLowerCase()
      );
      
      if (existingUser) {
        throw new Error('User with this email already exists');
      }

      // Create new user
      const newUser = {
        id: Date.now().toString(),
        email: userData.email,
        password: userData.password, // In real app, this would be hashed
        fullName: userData.fullName,
        role: userData.role,
        department: this.getDepartmentByRole(userData.role),
        createdAt: new Date().toISOString()
      };

      // Add to stored users
      const updatedUsers = [...existingUsers, newUser];
      const stored = this.storeUsers(updatedUsers);
      
      if (!stored) {
        throw new Error('Failed to create user account');
      }

      // Return user data without password
      const { password: _, ...userWithoutPassword } = newUser;

      return {
        success: true,
        user: userWithoutPassword,
        token: `mock_token_${newUser.id}_${Date.now()}`
      };

    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Validate API key (mock)
   */
  async validateApiKey(apiKey) {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 500));

      // Basic OpenAI API key format validation
      if (!apiKey || !apiKey.startsWith('sk-')) {
        throw new Error('Invalid API key format');
      }

      if (apiKey.length < 20) {
        throw new Error('API key appears to be invalid');
      }

      return {
        success: true,
        message: 'API key validated successfully'
      };

    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get user profile (mock)
   */
  async getUserProfile(token) {
    try {
      // In real app, this would validate the JWT token
      // const response = await fetch(`${this.baseURL}/auth/profile`, {
      //   headers: { 'Authorization': `Bearer ${token}` }
      // });

      // For demo, extract user ID from mock token
      const parts = token.split('_');
      const userId = parts[2];

      // Mock user data
      return {
        success: true,
        user: {
          id: userId,
          email: 'user@hospital.com',
          fullName: 'Hospital User',
          role: 'staff'
        }
      };

    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Sign out user
   */
  async signOut(token) {
    try {
      // In real app:
      // await fetch(`${this.baseURL}/auth/signout`, {
      //   method: 'POST',
      //   headers: { 'Authorization': `Bearer ${token}` }
      // });

      return {
        success: true,
        message: 'Signed out successfully'
      };

    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Helper to map roles to departments
   */
  getDepartmentByRole(role) {
    const roleMap = {
      admin: 'Administration',
      doctor: 'General Medicine',
      nurse: 'Nursing',
      manager: 'Management',
      staff: 'General'
    };
    return roleMap[role] || 'General';
  }

  /**
   * Get all registered users (for admin purposes - removes passwords)
   */
  getAllUsers() {
    const users = this.getStoredUsers();
    return users.map(({ password, ...user }) => user);
  }

  /**
   * Check if backend is available
   */
  async checkBackendHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        timeout: 5000
      });
      
      return response.ok;
    } catch (error) {
      console.warn('Backend health check failed:', error.message);
      return false;
    }
  }

  /**
   * Clear all stored users (for testing purposes)
   */
  clearAllUsers() {
    localStorage.removeItem(this.storageKey);
    this.initializeDefaultUsers();
  }
}

export default new AuthService();
