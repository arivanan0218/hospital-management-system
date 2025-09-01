import React, { useState, useEffect, useContext, createContext } from 'react';
import { Activity, Users, Bed, AlertTriangle, TrendingUp, TrendingDown, ArrowLeft } from 'lucide-react';

// Dashboard Context for real-time data
const DashboardContext = createContext();

export const DashboardProvider = ({ children, mcpClient }) => {
  const [dashboardData, setDashboardData] = useState({
    stats: null,
    beds: null,
    alerts: null,
    activity: null,
    patientFlow: null,
    lastUpdated: null
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    if (!mcpClient) return;

    try {
      setError(null);
      
      // Fetch all dashboard data concurrently
      const [statsResult, bedsResult, alertsResult, activityResult, flowResult] = await Promise.all([
        mcpClient.callTool('get_dashboard_stats'),
        mcpClient.callTool('get_live_bed_occupancy'),
        mcpClient.callTool('get_emergency_alerts'),
        mcpClient.callTool('get_recent_activity', { limit: 10 }),
        mcpClient.callTool('get_patient_flow_data', { hours: 24 })
      ]);

      setDashboardData({
        stats: statsResult.success ? statsResult : null,
        beds: bedsResult.success ? bedsResult : null,
        alerts: alertsResult.success ? alertsResult : null,
        activity: activityResult.success ? activityResult : null,
        patientFlow: flowResult.success ? flowResult : null,
        lastUpdated: new Date()
      });
      
      setIsLoading(false);
    } catch (error) {
      console.error('Dashboard data fetch failed:', error);
      setError(error.message);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [mcpClient]);

  return (
    <DashboardContext.Provider value={{ 
      dashboardData, 
      isLoading, 
      error, 
      refresh: fetchDashboardData 
    }}>
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
};

// Stat Card Component
const StatCard = ({ title, value, trend, icon, color = "blue", subtext }) => {
  const colorClasses = {
    blue: "bg-blue-600",
    green: "bg-green-600", 
    red: "bg-red-600",
    orange: "bg-orange-600",
    purple: "bg-purple-600"
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.startsWith('+')) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (trend.startsWith('-')) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return null;
  };

  return (
    <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-600">
      <div className="flex items-center justify-between mb-2">
        <div className={`w-10 h-10 ${colorClasses[color]} rounded-lg flex items-center justify-center`}>
          <span className="text-xl">{icon}</span>
        </div>
        {trend && (
          <div className="flex items-center space-x-1">
            {getTrendIcon()}
            <span className={`text-sm ${trend.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
              {trend}
            </span>
          </div>
        )}
      </div>
      <h3 className="text-2xl font-bold text-white mb-1">{value}</h3>
      <p className="text-sm text-gray-400">{title}</p>
      {subtext && (
        <p className="text-xs text-gray-500 mt-1">{subtext}</p>
      )}
    </div>
  );
};

// Hospital Stats Grid Component
const HospitalStatsGrid = () => {
  const { dashboardData } = useDashboard();
  const stats = dashboardData.stats;

  if (!stats) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-600 animate-pulse">
            <div className="w-10 h-10 bg-gray-600 rounded-lg mb-2"></div>
            <div className="h-6 bg-gray-600 rounded mb-1"></div>
            <div className="h-4 bg-gray-600 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Active Patients"
        value={stats.patients?.total || 0}
        trend={stats.patients?.trend}
        icon="👥"
        color="blue"
        subtext={`${stats.patients?.admissions_today || 0} admitted today`}
      />
      <StatCard
        title="Available Beds" 
        value={`${stats.beds?.available || 0}/${stats.beds?.total || 0}`}
        icon="🛏️"
        color="green"
        subtext={`${stats.beds?.occupancy_rate || 0}% occupied`}
      />
      <StatCard
        title="Staff on Duty"
        value={`${stats.staff?.on_duty || 0}/${stats.staff?.total_active || 0}`}
        icon="👨‍⚕️"
        color="purple"
        subtext="Active staff members"
      />
      <StatCard
        title="Today's Activity"
        value={`${(stats.patients?.admissions_today || 0) + (stats.patients?.discharges_today || 0)}`}
        icon="📊"
        color="orange"
        subtext={`${stats.patients?.admissions_today || 0} in, ${stats.patients?.discharges_today || 0} out`}
      />
    </div>
  );
};

// Department Occupancy Bar Component
const DepartmentOccupancy = ({ name, occupied, total, color }) => {
  const percentage = total > 0 ? (occupied / total) * 100 : 0;
  const colorClasses = {
    red: "bg-red-500",
    orange: "bg-orange-500", 
    green: "bg-green-500",
    blue: "bg-blue-500"
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-white">{name}</span>
        <span className="text-sm text-gray-400">{occupied}/{total} ({percentage.toFixed(1)}%)</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-3">
        <div 
          className={`h-3 rounded-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

// Bed Occupancy Chart Component
const BedOccupancyChart = () => {
  const { dashboardData } = useDashboard();
  const bedsData = dashboardData.beds;

  if (!bedsData || !bedsData.departments) {
    return (
      <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
        <h3 className="text-lg font-medium text-white mb-4">🏥 Bed Occupancy by Department</h3>
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map(i => (
            <div key={i} className="space-y-2">
              <div className="h-4 bg-gray-600 rounded w-1/3"></div>
              <div className="h-3 bg-gray-700 rounded-full"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
      <h3 className="text-lg font-medium text-white mb-4">🏥 Bed Occupancy by Department</h3>
      <div className="space-y-4">
        {bedsData.departments.map((dept, index) => (
          <DepartmentOccupancy
            key={index}
            name={dept.name}
            occupied={dept.occupied}
            total={dept.total_beds}
            color={dept.status_color || 'blue'}
          />
        ))}
      </div>
    </div>
  );
};

// Alert Item Component
const AlertItem = ({ alert }) => {
  const priorityColors = {
    high: "border-red-500 bg-red-900/20",
    medium: "border-orange-500 bg-orange-900/20",
    low: "border-blue-500 bg-blue-900/20"
  };

  const timeAgo = (timestamp) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now - alertTime;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className={`border rounded-lg p-3 ${priorityColors[alert.priority] || priorityColors.low}`}>
      <div className="flex items-start space-x-3">
        <span className="text-lg flex-shrink-0">{alert.icon}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-white font-medium">{alert.message}</p>
          <p className="text-xs text-gray-400 mt-1">{timeAgo(alert.timestamp)}</p>
        </div>
        {alert.action_required && (
          <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">Action Required</span>
        )}
      </div>
    </div>
  );
};

// Emergency Alerts Panel Component
const EmergencyAlertsPanel = () => {
  const { dashboardData } = useDashboard();
  const alertsData = dashboardData.alerts;

  if (!alertsData) {
    return (
      <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
        <h3 className="text-lg font-medium text-white mb-4">🚨 Emergency Alerts</h3>
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-600 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-white">🚨 Emergency Alerts</h3>
        <div className="flex space-x-2">
          {alertsData.critical_count > 0 && (
            <span className="bg-red-600 text-white text-xs px-2 py-1 rounded">
              {alertsData.critical_count} Critical
            </span>
          )}
          {alertsData.warning_count > 0 && (
            <span className="bg-orange-600 text-white text-xs px-2 py-1 rounded">
              {alertsData.warning_count} Warning
            </span>
          )}
        </div>
      </div>
      
      <div className="space-y-3">
        {alertsData.alerts && alertsData.alerts.length > 0 ? (
          alertsData.alerts.map((alert, index) => (
            <AlertItem key={alert.id || index} alert={alert} />
          ))
        ) : (
          <div className="text-center text-gray-400 py-4">
            <span className="text-green-400">✅</span>
            <p className="mt-2">No active alerts - All systems normal</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Recent Activity Panel Component
const RecentActivityPanel = () => {
  const { dashboardData } = useDashboard();
  const activityData = dashboardData.activity;

  const timeAgo = (timestamp) => {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffMs = now - activityTime;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ago`;
  };

  if (!activityData) {
    return (
      <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
        <h3 className="text-lg font-medium text-white mb-4">📋 Recent Activity</h3>
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-600 rounded"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-600 rounded w-3/4 mb-1"></div>
                <div className="h-3 bg-gray-600 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
      <h3 className="text-lg font-medium text-white mb-4">📋 Recent Activity</h3>
      <div className="space-y-3">
        {activityData.activities && activityData.activities.length > 0 ? (
          activityData.activities.map((activity, index) => (
            <div key={activity.id || index} className="flex items-center space-x-3">
              <span className="text-lg flex-shrink-0">{activity.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white">{activity.message}</p>
                <p className="text-xs text-gray-400">{timeAgo(activity.timestamp)}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-400 py-4">
            <p>No recent activity</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Last Updated Component
const LastUpdated = () => {
  const { dashboardData } = useDashboard();
  
  if (!dashboardData.lastUpdated) return null;

  return (
    <div className="text-center text-gray-400 text-sm">
      Last updated: {dashboardData.lastUpdated.toLocaleTimeString()}
    </div>
  );
};

// Main Real-time Dashboard Component
const RealTimeDashboard = ({ setActiveTab }) => {
  const { isLoading, error, refresh } = useDashboard();

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <h3 className="text-red-400 font-medium mb-2">Dashboard Error</h3>
          <p className="text-red-300 text-sm mb-4">{error}</p>
          <div className="flex space-x-3">
            <button 
              onClick={refresh}
              className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700"
            >
              Retry
            </button>
            {setActiveTab && (
              <button 
                onClick={() => setActiveTab('chat')}
                className="bg-gray-600 text-white px-4 py-2 rounded text-sm hover:bg-gray-700"
              >
                Back to Chat
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6 bg-[#1a1a1a] min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {setActiveTab && (
            <button 
              onClick={() => setActiveTab('chat')}
              className="p-2 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
              title="Back to Chat"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <h1 className="text-2xl font-bold text-white">📊 Hospital Dashboard</h1>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={refresh}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 flex items-center space-x-2"
          >
            <Activity className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <HospitalStatsGrid />

      {/* Charts and Alerts Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <BedOccupancyChart />
        <EmergencyAlertsPanel />
      </div>

      {/* Activity Feed */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <RecentActivityPanel />
        <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-600">
          <h3 className="text-lg font-medium text-white mb-4">🎯 Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <button className="bg-blue-600 text-white p-4 rounded-lg text-sm hover:bg-blue-700">
              📋 View All Patients
            </button>
            <button className="bg-green-600 text-white p-4 rounded-lg text-sm hover:bg-green-700">
              🛏️ Check Bed Status
            </button>
            <button className="bg-purple-600 text-white p-4 rounded-lg text-sm hover:bg-purple-700">
              📊 Generate Report
            </button>
            <button className="bg-orange-600 text-white p-4 rounded-lg text-sm hover:bg-orange-700">
              🚨 Emergency Protocol
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <LastUpdated />
    </div>
  );
};

export default RealTimeDashboard;
