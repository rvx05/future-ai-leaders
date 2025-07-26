import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';

interface StudySession {
  id: string;
  session_number: number;
  title: string;
  topics: string[];
  scheduled_date: string;
  estimated_duration: number;
  content_requirements: string[];
  study_guide: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'skipped';
  completed_at?: string;
  validation_score?: number;
  notes?: string;
}

interface StudyPlan {
  id: string;
  course_id: string;
  plan_data: {
    title: string;
    duration_weeks: number;
    sessions_per_week: number;
    total_sessions: number;
    weekly_breakdown: any[];
    calendar_events: any[];
  };
  created_at: string;
  updated_at: string;
  status: string;
  sessions?: StudySession[];
}

interface Course {
  id: string;
  title: string;
  description: string;
  progress: {
    completion_percentage: number;
    sessions_completed: number;
    total_sessions: number;
  };
  study_plan?: StudyPlan;
}

export const StudyPlanPage: React.FC = () => {
  const { callApi } = useApi();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const response = await callApi('/api/courses');
      if (response.courses) {
        setCourses(response.courses);
        // Auto-select first course with a study plan
        const courseWithPlan = response.courses.find((c: Course) => c.study_plan);
        if (courseWithPlan) {
          setSelectedCourse(courseWithPlan);
        }
      }
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeSession = async (sessionId: string, score: number, notes: string) => {
    if (!selectedCourse?.study_plan) return;

    try {
      await callApi(`/api/study-plans/${selectedCourse.study_plan.id}/sessions/${sessionId}/complete`, {
        method: 'POST',
        body: JSON.stringify({
          validation_score: score,
          notes: notes
        })
      });
      
      // Reload courses to get updated progress
      await loadCourses();
    } catch (error) {
      console.error('Failed to complete session:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="mb-4">
            <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Study Plans Yet</h3>
          <p className="text-gray-500 mb-6">Create your first course and study plan to get started with personalized learning.</p>
          <button
            onClick={() => window.location.href = '/chat'}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Create Study Plan
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Study Plans</h1>
        <p className="text-gray-600">Track your progress and manage your study sessions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Course List Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Your Courses</h3>
            <div className="space-y-2">
              {courses.map((course) => (
                <button
                  key={course.id}
                  onClick={() => setSelectedCourse(course)}
                  className={`w-full text-left p-3 rounded-md transition-colors ${
                    selectedCourse?.id === course.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'hover:bg-gray-50 border border-gray-200'
                  }`}
                >
                  <div className="font-medium text-sm mb-1">{course.title}</div>
                  {course.study_plan && (
                    <div className="text-xs text-gray-500">
                      {course.progress.completion_percentage}% Complete
                    </div>
                  )}
                  {!course.study_plan && (
                    <div className="text-xs text-orange-600">No study plan</div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {selectedCourse ? (
            <div className="space-y-6">
              {/* Course Header */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedCourse.title}</h2>
                    <p className="text-gray-600">{selectedCourse.description}</p>
                  </div>
                  {selectedCourse.study_plan && (
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedCourse.progress.completion_percentage}%
                      </div>
                      <div className="text-sm text-gray-500">Complete</div>
                    </div>
                  )}
                </div>

                {selectedCourse.study_plan && (
                  <div className="bg-gray-50 rounded p-4">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-lg font-semibold text-gray-900">
                          {selectedCourse.study_plan.plan_data.duration_weeks}
                        </div>
                        <div className="text-sm text-gray-500">Weeks</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-gray-900">
                          {selectedCourse.study_plan.plan_data.sessions_per_week}
                        </div>
                        <div className="text-sm text-gray-500">Sessions/Week</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-gray-900">
                          {selectedCourse.progress.sessions_completed}/{selectedCourse.progress.total_sessions}
                        </div>
                        <div className="text-sm text-gray-500">Sessions</div>
                      </div>
                    </div>
                  </div>
                )}

                {!selectedCourse.study_plan && (
                  <div className="bg-orange-50 border border-orange-200 rounded p-4">
                    <div className="flex items-center">
                      <svg className="h-5 w-5 text-orange-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <span className="text-orange-800">No study plan created for this course yet.</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Study Sessions */}
              {selectedCourse.study_plan?.sessions && (
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">Study Sessions</h3>
                  </div>
                  
                  <div className="divide-y divide-gray-200">
                    {selectedCourse.study_plan.sessions.map((session) => (
                      <div key={session.id} className="p-6">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full mr-3 ${
                              session.status === 'completed' ? 'bg-green-400' :
                              session.status === 'in_progress' ? 'bg-yellow-400' :
                              'bg-gray-300'
                            }`}></div>
                            <h4 className="text-lg font-medium text-gray-900">
                              Session {session.session_number}: {session.title}
                            </h4>
                          </div>
                          <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-500">
                              {formatDate(session.scheduled_date)}
                            </span>
                            <span className="text-sm text-gray-500">
                              {session.estimated_duration} min
                            </span>
                            <button
                              onClick={() => setExpandedSession(
                                expandedSession === session.id ? null : session.id
                              )}
                              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                            >
                              {expandedSession === session.id ? 'Collapse' : 'Expand'}
                            </button>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-2 mb-3">
                          {session.topics.map((topic, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {topic}
                            </span>
                          ))}
                        </div>

                        {expandedSession === session.id && (
                          <div className="mt-4 space-y-4">
                            <div>
                              <h5 className="font-medium text-gray-900 mb-2">Study Guide</h5>
                              <div className="prose prose-sm max-w-none text-gray-700">
                                {session.study_guide.split('\n').map((line, index) => (
                                  <p key={index}>{line}</p>
                                ))}
                              </div>
                            </div>

                            {session.content_requirements.length > 0 && (
                              <div>
                                <h5 className="font-medium text-gray-900 mb-2">Required Materials</h5>
                                <ul className="list-disc list-inside text-sm text-gray-700">
                                  {session.content_requirements.map((req, index) => (
                                    <li key={index}>{req}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {session.status === 'scheduled' && (
                              <div className="flex space-x-3">
                                <button
                                  onClick={() => {
                                    const score = prompt('Session completion score (0-100):');
                                    const notes = prompt('Session notes (optional):');
                                    if (score) {
                                      completeSession(session.id, parseInt(score), notes || '');
                                    }
                                  }}
                                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium"
                                >
                                  Mark Complete
                                </button>
                              </div>
                            )}

                            {session.status === 'completed' && (
                              <div className="bg-green-50 border border-green-200 rounded p-3">
                                <div className="flex items-center">
                                  <svg className="h-5 w-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                  </svg>
                                  <span className="text-green-800 font-medium">
                                    Completed on {session.completed_at ? formatDate(session.completed_at) : 'Unknown'}
                                  </span>
                                  {session.validation_score && (
                                    <span className="ml-4 text-green-700">
                                      Score: {session.validation_score}%
                                    </span>
                                  )}
                                </div>
                                {session.notes && (
                                  <div className="mt-2 text-sm text-gray-700">
                                    <strong>Notes:</strong> {session.notes}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Course</h3>
                <p className="text-gray-500">Choose a course from the sidebar to view its study plan and sessions.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
