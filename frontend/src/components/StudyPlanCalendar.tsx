import React, { useState } from 'react';
import { Calendar, Clock, BookOpen, Target, ChevronLeft, ChevronRight } from 'lucide-react';

interface StudySession {
  date: string;
  subject: string;
  topic: string;
  duration: number;
}

interface Milestone {
  date: string;
  title: string;
}

interface StudyPlan {
  totalDays: number;
  schedule: StudySession[];
  milestones: Milestone[];
}

interface StudyPlanCalendarProps {
  studyPlan: StudyPlan;
}

export const StudyPlanCalendar: React.FC<StudyPlanCalendarProps> = ({ studyPlan }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');

  const today = new Date();
  const startOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const endOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
  const startDate = new Date(startOfMonth);
  startDate.setDate(startDate.getDate() - startOfMonth.getDay());

  const days = [];
  const currentDate = new Date(startDate);
  while (currentDate <= endOfMonth || days.length % 7 !== 0) {
    days.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }

  const getSessionsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return studyPlan.schedule.filter(session => session.date === dateStr);
  };

  const getMilestonesForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return studyPlan.milestones.filter(milestone => milestone.date === dateStr);
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + (direction === 'next' ? 1 : -1));
      return newDate;
    });
  };

  const subjectColors = {
    'Mathematics': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    'Computer Science': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    'Physics': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
    'Chemistry': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
    'Biology': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-400',
  };

  return (
    <div className="space-y-6">
      {/* View Toggle */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              viewMode === 'calendar'
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <Calendar className="h-4 w-4 inline mr-2" />
            Calendar
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              viewMode === 'list'
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <BookOpen className="h-4 w-4 inline mr-2" />
            List
          </button>
        </div>

        {viewMode === 'calendar' && (
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h2>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>

      {viewMode === 'calendar' ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          {/* Calendar Header */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="p-2 text-center text-sm font-medium text-gray-500 dark:text-gray-400">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {days.map((day, index) => {
              const sessions = getSessionsForDate(day);
              const milestones = getMilestonesForDate(day);
              const isCurrentMonth = day.getMonth() === currentMonth.getMonth();
              const isToday = day.toDateString() === today.toDateString();

              return (
                <div
                  key={index}
                  className={`min-h-24 p-2 border border-gray-100 dark:border-gray-700 ${
                    isCurrentMonth ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700/50'
                  } ${isToday ? 'ring-2 ring-blue-500' : ''}`}
                >
                  <div className={`text-sm font-medium mb-1 ${
                    isCurrentMonth ? 'text-gray-900 dark:text-white' : 'text-gray-400 dark:text-gray-500'
                  }`}>
                    {day.getDate()}
                  </div>
                  
                  <div className="space-y-1">
                    {sessions.slice(0, 2).map((session, i) => (
                      <div
                        key={i}
                        className={`text-xs px-2 py-1 rounded ${
                          subjectColors[session.subject] || 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200'
                        }`}
                      >
                        {session.subject}
                      </div>
                    ))}
                    
                    {milestones.map((milestone, i) => (
                      <div
                        key={i}
                        className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
                      >
                        <Target className="h-3 w-3 inline mr-1" />
                        Goal
                      </div>
                    ))}
                    
                    {sessions.length > 2 && (
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        +{sessions.length - 2} more
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {studyPlan.schedule.map((session, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <Calendar className="h-5 w-5 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {session.subject} - {session.topic}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(session.date).toLocaleDateString('en-US', { 
                        weekday: 'long', 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                  <Clock className="h-4 w-4" />
                  <span>{session.duration}h</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Study Plan Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Calendar className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Days</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{studyPlan.totalDays}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Clock className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Hours</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {studyPlan.schedule.reduce((total, session) => total + session.duration, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Target className="h-8 w-8 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Milestones</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{studyPlan.milestones.length}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};