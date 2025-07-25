import React from 'react';

export const ProgressTracker: React.FC = () => {
  const weeklyData = [
    { day: 'Mon', hours: 2.5 },
    { day: 'Tue', hours: 1.8 },
    { day: 'Wed', hours: 3.2 },
    { day: 'Thu', hours: 2.1 },
    { day: 'Fri', hours: 2.8 },
    { day: 'Sat', hours: 4.0 },
    { day: 'Sun', hours: 1.5 },
  ];

  const maxHours = Math.max(...weeklyData.map(d => d.hours));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Weekly Study Progress</h2>
      
      <div className="flex items-end space-x-4 h-40">
        {weeklyData.map((data) => (
          <div key={data.day} className="flex flex-col items-center flex-1">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-t-lg relative overflow-hidden">
              <div
                className="bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-lg transition-all duration-700 ease-out"
                style={{
                  height: `${(data.hours / maxHours) * 120}px`,
                  minHeight: '4px',
                }}
              />
            </div>
            <div className="mt-2 text-center">
              <p className="text-xs font-medium text-gray-600 dark:text-gray-400">{data.day}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">{data.hours}h</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-between items-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Total this week: <span className="font-semibold">17.9 hours</span>
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Daily average: <span className="font-semibold">2.6 hours</span>
        </div>
      </div>
    </div>
  );
};