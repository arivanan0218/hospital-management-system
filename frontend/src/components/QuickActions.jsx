/**
 * Quick Action Component - Provides preset queries for common hospital operations
 */

import React from 'react';
import { Users, Bed, Calendar, Package, Wrench, UserCheck } from 'lucide-react';

const QuickActions = ({ onActionClick }) => {
  const actions = [
    {
      id: 'list-patients',
      icon: Users,
      label: 'List Patients',
      query: 'Show me all patients in the system',
      description: 'View all registered patients'
    },
    {
      id: 'available-beds',
      icon: Bed,
      label: 'Available Beds',
      query: 'Show me all available beds',
      description: 'Find open beds for new admissions'
    },
    {
      id: 'today-appointments',
      icon: Calendar,
      label: 'Today\'s Appointments',
      query: 'Show me today\'s appointments',
      description: 'View scheduled appointments for today'
    },
    {
      id: 'low-supplies',
      icon: Package,
      label: 'Low Stock Supplies',
      query: 'Show me supplies that are low in stock',
      description: 'Check inventory levels'
    },
    {
      id: 'staff-list',
      icon: UserCheck,
      label: 'Staff Members',
      query: 'Show me all staff members',
      description: 'View hospital staff directory'
    },
    {
      id: 'equipment-status',
      icon: Wrench,
      label: 'Equipment Status',
      query: 'Show me all equipment and their status',
      description: 'Check equipment availability'
    }
  ];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => {
          const IconComponent = action.icon;
          return (
            <button
              key={action.id}
              onClick={() => onActionClick(action.query)}
              className="flex items-center space-x-2 p-2 text-left hover:bg-gray-50 rounded-lg transition-colors text-sm"
              title={action.description}
            >
              <IconComponent size={16} className="text-blue-500 flex-shrink-0" />
              <span className="text-gray-700 truncate">{action.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions;
