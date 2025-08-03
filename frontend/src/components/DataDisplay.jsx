/**
 * Data Display Component - Shows hospital data in a formatted way
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';

const DataDisplay = ({ data, type, title }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const renderTableData = (items) => {
    if (!Array.isArray(items) || items.length === 0) {
      return <div className="text-gray-500 text-sm">No data available</div>;
    }

    const firstItem = items[0];
    const headers = Object.keys(firstItem).filter(key => 
      !key.includes('id') || key === 'patient_id' || key === 'user_id'
    ).slice(0, 5); // Show max 5 columns

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              {headers.map(header => (
                <th key={header} className="text-left py-2 px-2 font-medium text-gray-700 capitalize">
                  {header.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.slice(0, 10).map((item, index) => ( // Show max 10 rows
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                {headers.map(header => (
                  <td key={header} className="py-2 px-2 text-gray-600">
                    {typeof item[header] === 'string' && item[header].length > 30
                      ? `${item[header].substring(0, 30)}...`
                      : String(item[header] || '-')
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {items.length > 10 && (
          <div className="text-xs text-gray-500 mt-2 text-center">
            Showing 10 of {items.length} records
          </div>
        )}
      </div>
    );
  };

  const getDataSummary = () => {
    if (Array.isArray(data)) {
      return `${data.length} ${type || 'records'}`;
    } else if (typeof data === 'object') {
      return `${Object.keys(data).length} properties`;
    }
    return 'Data available';
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <div 
        className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <span className="font-medium text-gray-700">
            {title || `${type} Data`}
          </span>
          <span className="text-sm text-gray-500">
            ({getDataSummary()})
          </span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleCopy();
          }}
          className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      
      {isExpanded && (
        <div className="p-3">
          {Array.isArray(data) ? (
            renderTableData(data)
          ) : (
            <pre className="text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
};

export default DataDisplay;
