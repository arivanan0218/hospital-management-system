import React, { useState, useEffect } from 'react';
import { Calendar, FileText, Pill, Heart, Activity, AlertTriangle, Search, Filter } from 'lucide-react';

const MedicalHistoryViewer = ({ patientId }) => {
  const [medicalHistory, setMedicalHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    if (patientId) {
      fetchMedicalHistory();
    }
  }, [patientId]);

  const fetchMedicalHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/tools/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'tools/call',
          params: {
            name: 'get_patient_medical_history',
            arguments: {
              patient_id: patientId
            }
          }
        })
      });

      const result = await response.json();

      if (result.result?.content?.[0]?.text) {
        const data = JSON.parse(result.result.content[0].text);
        
        if (data.success) {
          setMedicalHistory(data.medical_history);
        } else {
          throw new Error(data.message || 'Failed to fetch medical history');
        }
      } else {
        throw new Error('Invalid response from server');
      }

    } catch (error) {
      console.error('Error fetching medical history:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const queryMedicalKnowledge = async (query) => {
    try {
      const response = await fetch('http://localhost:8000/tools/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 2,
          method: 'tools/call',
          params: {
            name: 'query_medical_knowledge',
            arguments: {
              query: query,
              patient_id: patientId
            }
          }
        })
      });

      const result = await response.json();

      if (result.result?.content?.[0]?.text) {
        const data = JSON.parse(result.result.content[0].text);
        return data;
      }
    } catch (error) {
      console.error('Error querying medical knowledge:', error);
    }
    return null;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    const results = await queryMedicalKnowledge(searchQuery);
    if (results && results.success) {
      // Display search results in a modal or expand section
      console.log('Search results:', results);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date not available';
    return new Date(dateString).toLocaleDateString();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBar = (confidence) => {
    const percentage = Math.round(confidence * 100);
    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${
            confidence >= 0.8 ? 'bg-green-500' :
            confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    );
  };

  const categoryIcons = {
    medications: <Pill className="w-5 h-5" />,
    conditions: <Heart className="w-5 h-5" />,
    procedures: <Activity className="w-5 h-5" />,
    allergies: <AlertTriangle className="w-5 h-5" />,
    vital_signs: <Activity className="w-5 h-5" />,
    documents: <FileText className="w-5 h-5" />
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Heart className="w-4 h-4" /> },
    { id: 'medications', label: 'Medications', icon: <Pill className="w-4 h-4" /> },
    { id: 'conditions', label: 'Conditions', icon: <Heart className="w-4 h-4" /> },
    { id: 'allergies', label: 'Allergies', icon: <AlertTriangle className="w-4 h-4" /> },
    { id: 'documents', label: 'Documents', icon: <FileText className="w-4 h-4" /> }
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center text-red-600">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <p className="text-lg font-medium">Error Loading Medical History</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={fetchMedicalHistory}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!medicalHistory) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-4" />
          <p className="text-lg font-medium">No Medical History Available</p>
          <p className="text-sm">Upload medical documents to build patient history</p>
        </div>
      </div>
    );
  }

  const renderCategoryData = (categoryName, data) => {
    if (!data || data.length === 0) {
      return (
        <div className="text-center text-gray-500 py-8">
          <p>No {categoryName} records found</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {data.map((item, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-medium text-gray-900">{item.name}</h4>
              <span className="text-xs text-gray-500">
                {formatDate(item.date)}
              </span>
            </div>
            
            {item.value && (
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Value:</span> {item.value} {item.unit || ''}
              </p>
            )}
            
            {item.doctor && (
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Prescribed by:</span> {item.doctor}
              </p>
            )}
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">
                Confidence: {Math.round(item.confidence * 100)}%
              </span>
              <div className="w-24">
                {getConfidenceBar(item.confidence)}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderOverview = () => {
    const totalItems = Object.values(medicalHistory).reduce((total, category) => {
      return total + (Array.isArray(category) ? category.length : 0);
    }, 0);

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(medicalHistory).map(([key, data]) => {
            if (!Array.isArray(data)) return null;
            
            return (
              <div key={key} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  {categoryIcons[key]}
                  <h3 className="font-medium text-gray-900 capitalize">
                    {key.replace('_', ' ')}
                  </h3>
                </div>
                <p className="text-2xl font-bold text-blue-600">{data.length}</p>
                <p className="text-xs text-gray-500">
                  {data.length === 1 ? 'record' : 'records'}
                </p>
              </div>
            );
          })}
        </div>

        {/* Recent Items */}
        <div>
          <h3 className="text-lg font-medium mb-4">Recent Medical Records</h3>
          <div className="space-y-3">
            {Object.entries(medicalHistory).map(([category, items]) => {
              if (!Array.isArray(items) || items.length === 0) return null;
              
              return items.slice(0, 3).map((item, index) => (
                <div key={`${category}-${index}`} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  {categoryIcons[category]}
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-sm text-gray-500">
                      {category.charAt(0).toUpperCase() + category.slice(1)} • {formatDate(item.date)}
                    </p>
                  </div>
                  <div className={`text-sm font-medium ${getConfidenceColor(item.confidence)}`}>
                    {Math.round(item.confidence * 100)}%
                  </div>
                </div>
              ));
            })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Medical History</h2>
          <button
            onClick={fetchMedicalHistory}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            Refresh
          </button>
        </div>

        {/* Search Bar */}
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search medical history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' ? renderOverview() : 
         renderCategoryData(activeTab, medicalHistory[activeTab])}
      </div>
    </div>
  );
};

export default MedicalHistoryViewer;
