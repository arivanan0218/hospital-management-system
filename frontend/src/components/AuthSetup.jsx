import React, { useState } from 'react';
import { User, Mail, Lock, Key, ArrowRight, ArrowLeft } from 'lucide-react';
import authService from '../services/authService';

const AuthSetup = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState('auth'); // 'auth' or 'apikey'
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: 'staff',
    apiKey: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error and success message when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
    if (successMessage) {
      setSuccessMessage('');
    }
  };

  const validateAuthForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (authMode === 'signup') {
      if (!formData.fullName) {
        newErrors.fullName = 'Full name is required';
      }
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateApiKey = () => {
    const newErrors = {};
    
    if (!formData.apiKey) {
      newErrors.apiKey = 'OpenAI API key is required';
    } else if (!formData.apiKey.startsWith('sk-')) {
      newErrors.apiKey = 'Please enter a valid OpenAI API key (starts with sk-)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAuthSubmit = async () => {
    if (!validateAuthForm()) return;

    setIsLoading(true);
    try {
      let result;
      
      if (authMode === 'signin') {
        result = await authService.signIn(formData.email, formData.password);
      } else {
        result = await authService.signUp({
          email: formData.email,
          password: formData.password,
          fullName: formData.fullName,
          role: formData.role
        });
      }

      if (result.success) {
        // Store user data and proceed to API key step
        setFormData(prev => ({ 
          ...prev, 
          ...result.user,
          token: result.token 
        }));
        
        if (authMode === 'signup') {
          setSuccessMessage('Account created successfully! Please configure your API key.');
        }
        
        setCurrentStep('apikey');
      } else {
        setErrors({ submit: result.error });
      }
    } catch (error) {
      setErrors({ submit: 'Authentication failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!validateApiKey()) return;

    setIsLoading(true);
    try {
      // Validate API key
      const apiResult = await authService.validateApiKey(formData.apiKey);
      
      if (!apiResult.success) {
        setErrors({ apiKey: apiResult.error });
        return;
      }
      
      // Complete setup data
      const userData = {
        id: formData.id,
        email: formData.email,
        fullName: formData.fullName,
        role: formData.role,
        department: formData.department,
        token: formData.token,
        apiKey: formData.apiKey
      };
      
      // Pass the complete setup data to parent
      onComplete(userData);
    } catch (error) {
      setErrors({ apiKey: 'Setup failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const renderAuthStep = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
          <User className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-2xl font-medium text-white mb-2">
          {authMode === 'signin' ? 'Welcome Back' : 'Create Account'}
        </h1>
        <p className="text-gray-400 text-sm">
          {authMode === 'signin' 
            ? 'Sign in to access your hospital management dashboard'
            : 'Join the hospital management system'
          }
        </p>
      </div>

      {/* Auth Form */}
      <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-700 space-y-4">
        {authMode === 'signup' && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Full Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                placeholder="Enter your full name"
                className={`w-full pl-10 pr-4 py-3 bg-[#1a1a1a] border rounded-lg focus:outline-none focus:ring-1 text-white placeholder-gray-400 text-sm ${
                  errors.fullName ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'
                }`}
              />
            </div>
            {errors.fullName && <p className="text-red-400 text-xs mt-1">{errors.fullName}</p>}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="Enter your email"
              className={`w-full pl-10 pr-4 py-3 bg-[#1a1a1a] border rounded-lg focus:outline-none focus:ring-1 text-white placeholder-gray-400 text-sm ${
                errors.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'
              }`}
            />
          </div>
          {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              placeholder="Enter your password"
              className={`w-full pl-10 pr-4 py-3 bg-[#1a1a1a] border rounded-lg focus:outline-none focus:ring-1 text-white placeholder-gray-400 text-sm ${
                errors.password ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'
              }`}
            />
          </div>
          {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
        </div>

        {authMode === 'signup' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  placeholder="Confirm your password"
                  className={`w-full pl-10 pr-4 py-3 bg-[#1a1a1a] border rounded-lg focus:outline-none focus:ring-1 text-white placeholder-gray-400 text-sm ${
                    errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'
                  }`}
                />
              </div>
              {errors.confirmPassword && <p className="text-red-400 text-xs mt-1">{errors.confirmPassword}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Role
              </label>
              <select
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
                className="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-600 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-white text-sm"
              >
                <option value="staff">Staff</option>
                <option value="doctor">Doctor</option>
                <option value="nurse">Nurse</option>
                <option value="admin">Administrator</option>
                <option value="manager">Manager</option>
              </select>
            </div>
          </>
        )}

        {errors.submit && (
          <div className="p-3 bg-red-900/20 border border-red-800 rounded-lg">
            <p className="text-red-400 text-sm">{errors.submit}</p>
          </div>
        )}

        {successMessage && (
          <div className="p-3 bg-green-900/20 border border-green-800 rounded-lg">
            <p className="text-green-400 text-sm">{successMessage}</p>
          </div>
        )}

        <button
          onClick={handleAuthSubmit}
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white py-3 px-4 rounded-lg font-medium text-sm transition-colors flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <span>{authMode === 'signin' ? 'Sign In' : 'Create Account'}</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {/* Toggle Auth Mode */}
      <div className="text-center space-y-3">
        <p className="text-gray-400 text-sm">
          {authMode === 'signin' ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => {
              setAuthMode(authMode === 'signin' ? 'signup' : 'signin');
              setErrors({});
              setSuccessMessage('');
              setFormData(prev => ({ 
                ...prev, 
                password: '', 
                confirmPassword: '', 
                fullName: authMode === 'signin' ? '' : prev.fullName 
              }));
            }}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            {authMode === 'signin' ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
        
        {/* Demo Credentials Info */}
        {authMode === 'signin' && (
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3">
            <p className="text-blue-400 text-xs font-medium mb-2">💡 Demo Credentials:</p>
            <div className="text-xs text-blue-300 space-y-1">
              <div><strong>Admin:</strong> admin@hospital.com / admin123</div>
              <div><strong>Doctor:</strong> doctor@hospital.com / doctor123</div>
              <div><strong>Nurse:</strong> nurse@hospital.com / nurse123</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderApiKeyStep = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
          <Key className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-2xl font-medium text-white mb-2">
          Configure AI Assistant
        </h1>
        <p className="text-gray-400 text-sm">
          Enter your OpenAI API key to enable AI-powered hospital management features
        </p>
      </div>

      {/* User Info Display */}
      <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">
              {formData.fullName ? formData.fullName.charAt(0).toUpperCase() : formData.email.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <p className="text-white font-medium text-sm">{formData.fullName || 'User'}</p>
            <p className="text-gray-400 text-xs">
              {formData.email} • {formData.role}
              {formData.department && ` • ${formData.department}`}
            </p>
          </div>
        </div>
      </div>

      {/* API Key Input */}
      <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
            <Key className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-white font-medium">OpenAI API Key</h3>
            <p className="text-xs text-gray-400">Required for AI conversation processing</p>
          </div>
        </div>
        
        <input
          type="password"
          value={formData.apiKey}
          onChange={(e) => handleInputChange('apiKey', e.target.value)}
          placeholder="sk-..."
          className={`w-full px-4 py-3 bg-[#1a1a1a] border rounded-lg focus:outline-none focus:ring-1 text-white placeholder-gray-400 text-sm ${
            errors.apiKey ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'
          }`}
        />
        {errors.apiKey && <p className="text-red-400 text-xs mt-2">{errors.apiKey}</p>}
        
        <div className="mt-3 p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
          <p className="text-blue-400 text-xs">
            💡 <strong>Tip:</strong> Get your API key from{' '}
            <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-300">
              OpenAI Platform
            </a>
            . Your key is stored locally and never shared.
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={() => setCurrentStep('auth')}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-lg font-medium text-sm transition-colors flex items-center justify-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>
        
        <button
          onClick={handleComplete}
          disabled={isLoading}
          className="flex-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white py-3 px-4 rounded-lg font-medium text-sm transition-colors flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <span>Complete Setup</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-[#1a1a1a] flex flex-col text-white">
      {/* Header */}
      <div className="border-b border-gray-700 px-4 py-3 bg-[#1a1a1a]">
        <div className="flex items-center space-x-3">
          <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-lg">
            H
          </div>
          <div>
            <h1 className="text-sm font-medium text-white">Hospital Management System</h1>
            <p className="text-xs text-gray-400">
              {currentStep === 'auth' ? 'User Authentication' : 'AI Configuration'}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-[#1a1a1a] flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          {currentStep === 'auth' ? renderAuthStep() : renderApiKeyStep()}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-700 px-4 py-3 bg-[#1a1a1a]">
        <p className="text-xs text-gray-500 text-center">
          Secure hospital management with AI assistance
        </p>
      </div>
    </div>
  );
};

export default AuthSetup;
