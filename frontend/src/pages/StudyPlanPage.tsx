import React, { useState } from 'react';
import { StudyPlanCalendar } from '../components/StudyPlanCalendar';

export const StudyPlanPage: React.FC = () => {
  const [studyPlan, setStudyPlan] = useState(null);
  const [formData, setFormData] = useState({
    examDate: '',
    studyHoursPerDay: 2,
    subjects: [] as string[],
    currentLevel: 'beginner',
    preferences: {
      morningStudy: true,
      eveningStudy: false,
      weekendIntensive: false,
    },
  });

  const availableSubjects = [
    'Mathematics',
    'Computer Science',
    'Physics',
    'Chemistry',
    'Biology',
    'English Literature',
    'History',
    'Psychology',
  ];

  const handleSubjectToggle = (subject: string) => {
    setFormData(prev => ({
      ...prev,
      subjects: prev.subjects.includes(subject)
        ? prev.subjects.filter(s => s !== subject)
        : [...prev.subjects, subject]
    }));
  };

  const generateStudyPlan = () => {
    // Mock study plan generation
    const mockPlan = {
      totalDays: 30,
      schedule: [
        { date: '2025-01-15', subject: 'Mathematics', topic: 'Algebra Review', duration: 2 },
        { date: '2025-01-16', subject: 'Computer Science', topic: 'Data Structures', duration: 2.5 },
        { date: '2025-01-17', subject: 'Mathematics', topic: 'Calculus Basics', duration: 1.5 },
      ],
      milestones: [
        { date: '2025-01-22', title: 'Complete Chapter 1 Review' },
        { date: '2025-02-05', title: 'Mid-term Practice Test' },
        { date: '2025-02-12', title: 'Final Review Week' },
      ],
    };
    setStudyPlan(mockPlan);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Study Plan Generator
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Create a personalized study schedule based on your goals and timeline
        </p>
      </div>

      {!studyPlan ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Plan Configuration</h2>
          
          <div className="space-y-6">
            {/* Exam Date */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Target Exam Date
                </label>
                <input
                  type="date"
                  value={formData.examDate}
                  onChange={(e) => setFormData(prev => ({ ...prev, examDate: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Study Hours Per Day
                </label>
                <select
                  value={formData.studyHoursPerDay}
                  onChange={(e) => setFormData(prev => ({ ...prev, studyHoursPerDay: Number(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value={1}>1 hour</option>
                  <option value={2}>2 hours</option>
                  <option value={3}>3 hours</option>
                  <option value={4}>4 hours</option>
                  <option value={5}>5+ hours</option>
                </select>
              </div>
            </div>

            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Select Subjects to Study
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {availableSubjects.map((subject) => (
                  <button
                    key={subject}
                    onClick={() => handleSubjectToggle(subject)}
                    className={`p-3 text-sm rounded-md border transition-colors ${
                      formData.subjects.includes(subject)
                        ? 'bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/20 dark:border-blue-600 dark:text-blue-400'
                        : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                    }`}
                  >
                    {subject}
                  </button>
                ))}
              </div>
            </div>

            {/* Current Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Current Knowledge Level
              </label>
              <select
                value={formData.currentLevel}
                onChange={(e) => setFormData(prev => ({ ...prev, currentLevel: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            {/* Study Preferences */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Study Preferences
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.preferences.morningStudy}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      preferences: { ...prev.preferences, morningStudy: e.target.checked }
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">I prefer morning study sessions</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.preferences.eveningStudy}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      preferences: { ...prev.preferences, eveningStudy: e.target.checked }
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">I prefer evening study sessions</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.preferences.weekendIntensive}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      preferences: { ...prev.preferences, weekendIntensive: e.target.checked }
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Intensive weekend study sessions</span>
                </label>
              </div>
            </div>

            <button
              onClick={generateStudyPlan}
              disabled={!formData.examDate || formData.subjects.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-md transition-colors"
            >
              Generate Study Plan
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-green-900 dark:text-green-300 mb-2">
              Study Plan Generated!
            </h2>
            <p className="text-green-700 dark:text-green-400">
              Your personalized {studyPlan.totalDays}-day study plan is ready. 
              Follow the schedule below to achieve your study goals.
            </p>
          </div>

          <StudyPlanCalendar studyPlan={studyPlan} />

          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setStudyPlan(null)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Create New Plan
            </button>
            
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
              Export to Google Calendar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};