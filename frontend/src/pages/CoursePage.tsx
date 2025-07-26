import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../contexts/AuthContext';

interface Course {
  id: string;
  title: string;
  description: string;
  course_outline: any;
  created_at: string;
  progress?: {
    total_sessions: number;
    completed_sessions: number;
    progress_percentage: number;
    next_session?: {
      id: string;
      title: string;
      scheduled_date: string;
      topics: string[];
    };
  };
}

const CoursePage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [newCourse, setNewCourse] = useState({
    title: '',
    description: '',
    outline: ''
  });
  const [loading, setLoading] = useState(false);
  const [agentResponse, setAgentResponse] = useState<string>('');
  
  const { callApi } = useApi();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchCourses();
    }
  }, [user]);

  const fetchCourses = async () => {
    try {
      const response = await callApi('/api/courses');
      setCourses(response.courses || []);
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAgentResponse('');
    
    try {
      const response = await callApi('/api/courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newCourse),
      });
      setAgentResponse(response.response);
      setShowCreateForm(false);
      setNewCourse({ title: '', description: '', outline: '' });
      await fetchCourses();
    } catch (error: any) {
      console.error('Failed to create course:', error);
      setAgentResponse(error.message || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  const handleCourseSelect = async (course: Course) => {
    try {
      const response = await callApi(`/api/courses/${course.id}`);
      setSelectedCourse(response);
    } catch (error) {
      console.error('Failed to fetch course details:', error);
    }
  };

  const CourseCard: React.FC<{ course: Course }> = ({ course }) => (
    <div 
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700"
      onClick={() => handleCourseSelect(course)}
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{course.title}</h3>
      <p className="text-gray-600 dark:text-gray-300 mb-4">{course.description}</p>
      <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">
        Created: {new Date(course.created_at).toLocaleDateString()}
      </div>
      
      {course.progress && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-700 dark:text-gray-300">Progress</span>
            <span className="text-gray-700 dark:text-gray-300">{course.progress.progress_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full" 
              style={{ width: `${course.progress.progress_percentage}%` }}
            ></div>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {course.progress.completed_sessions}/{course.progress.total_sessions} sessions completed
          </div>
          
          {course.progress.next_session && (
            <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="text-sm font-medium text-blue-900 dark:text-blue-100">Next Session:</div>
              <div className="text-sm text-blue-700 dark:text-blue-200">{course.progress.next_session.title}</div>
              <div className="text-xs text-blue-600 dark:text-blue-300">
                {new Date(course.progress.next_session.scheduled_date).toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const CreateCourseForm: React.FC = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">Create New Course</h2>
        
        <form onSubmit={handleCreateCourse} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Course Title *
            </label>
            <input
              type="text"
              value={newCourse.title}
              onChange={(e) => setNewCourse({ ...newCourse, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="e.g., Data Structures and Algorithms"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Course Description
            </label>
            <textarea
              value={newCourse.description}
              onChange={(e) => setNewCourse({ ...newCourse, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              rows={3}
              placeholder="Brief description of the course"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Course Outline/Syllabus *
            </label>
            <textarea
              value={newCourse.outline}
              onChange={(e) => setNewCourse({ ...newCourse, outline: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              rows={8}
              placeholder="Paste your course syllabus or outline here..."
              required
            />
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
        
        {agentResponse && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <h3 className="font-medium text-green-900 dark:text-green-100 mb-2">AI Assistant Response:</h3>
            <div className="text-sm text-green-800 dark:text-green-200 whitespace-pre-wrap">{agentResponse}</div>
          </div>
        )}
      </div>
    </div>
  );

  const CourseDetails: React.FC<{ course: Course }> = ({ course }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">{course.title}</h2>
          <button
            onClick={() => setSelectedCourse(null)}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Description</h3>
            <p className="text-gray-600 dark:text-gray-300">{course.description}</p>
          </div>
          
          {course.progress && (
            <div>
              <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Progress Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {course.progress.progress_percentage}%
                  </div>
                  <div className="text-sm text-blue-800 dark:text-blue-300">Overall Progress</div>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {course.progress.completed_sessions}
                  </div>
                  <div className="text-sm text-green-800 dark:text-green-300">Sessions Completed</div>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg border border-orange-200 dark:border-orange-800">
                  <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {course.progress.total_sessions - course.progress.completed_sessions}
                  </div>
                  <div className="text-sm text-orange-800 dark:text-orange-300">Sessions Remaining</div>
                </div>
              </div>
            </div>
          )}
          
          <div>
            <h3 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Course Outline</h3>
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                {typeof course.course_outline === 'string' 
                  ? course.course_outline 
                  : JSON.stringify(course.course_outline, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Please log in</h1>
          <p className="text-gray-600 dark:text-gray-300">You need to be logged in to access your courses.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Courses</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              Manage your courses and track your study progress
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create New Course
          </button>
        </div>

        {courses.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No courses yet</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Create your first course to start building personalized study plans
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Your First Course
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}

        {showCreateForm && <CreateCourseForm />}
        {selectedCourse && <CourseDetails course={selectedCourse} />}
      </div>
    </div>
  );
};

export default CoursePage;
