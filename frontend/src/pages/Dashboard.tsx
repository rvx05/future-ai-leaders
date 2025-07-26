import React, { useEffect } from "react";
import { Link } from 'react-router-dom';
import { AgenticChat } from "../components/AgenticChat";
import { ProgressTracker } from "../components/ProgressTracker";
import { DailyMotivation } from "../components/DailyMotivation";
import { BookOpen, Clock, Target, TrendingUp, Calendar, FileText, Upload, MessageCircle, CreditCard } from "lucide-react";
import { useApi } from '../hooks/useApi';

interface ProgressData {
  totalStudyTime: number;
  completedSessions: number;
  studyStreak: number;
  averageScore: number;
}

interface ActivityData {
  id: string;
  type: string;
  description: string;
  details: string;
  timestamp: string;
}

export const Dashboard: React.FC = () => {
  const { data: progressData, loading: progressLoading, callApi: fetchProgress } = useApi<ProgressData>();
  const { data: recentActivity, callApi: fetchActivity } = useApi<ActivityData[]>();

  useEffect(() => {
    fetchProgress('/api/progress');
    fetchActivity('/api/activity/recent');
  }, [fetchProgress, fetchActivity]);

  const quickActions = [
    {
      title: 'AI Chat Assistant',
      description: 'Chat with your AI tutor for instant help',
      icon: MessageCircle,
      link: '/chat',
      color: 'bg-indigo-500',
    },
    {
      title: 'Generate Flashcards',
      description: 'Create AI-powered flashcards from your notes',
      icon: CreditCard,
      link: '/flashcards',
      color: 'bg-blue-500',
    },
    {
      title: 'Practice Exam',
      description: 'Test your knowledge with custom quizzes',
      icon: FileText,
      link: '/exam',
      color: 'bg-emerald-500',
    },
    {
      title: 'Upload Content',
      description: 'Add new course materials',
      icon: Upload,
      link: '/upload',
      color: 'bg-purple-500',
    },
    {
      title: 'Study Plan',
      description: 'Create personalized study schedules',
      icon: Calendar,
      link: '/study-plan',
      color: 'bg-orange-500',
    },
  ];

  const activityIcons: { [key: string]: React.ElementType } = {
    flashcards: CreditCard,
    exam: FileText,
    upload: Upload,
    default: BookOpen,
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back to Study Buddy!
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Your personal AI study companion.
          </p>
        </div>

        <DailyMotivation />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-[600px] lg:h-[800px]">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">AI Study Assistant</h2>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  Ask questions, get study help, or generate practice materials
                </p>
              </div>
              <div className="h-[calc(100%-88px)]">
                <AgenticChat />
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Progress Overview</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Clock className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{progressLoading ? '...' : progressData?.totalStudyTime || 0}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Hours Studied</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <Target className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {progressLoading ? '...' : progressData?.completedSessions || 0}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Sessions</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <TrendingUp className="h-8 w-8 text-orange-600 dark:text-orange-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{progressLoading ? '...' : progressData?.studyStreak || 0}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Day Streak</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <BookOpen className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{progressLoading ? '...' : progressData?.averageScore || 0}%</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Avg Score</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
              <div className="space-y-3">
                {recentActivity?.map((activity: ActivityData) => {
                  const Icon = activityIcons[activity.type] || activityIcons.default;
                  return (
                    <div key={activity.id} className="flex items-center justify-between py-2">
                      <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 dark:bg-blue-900 rounded p-2">
                          <Icon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{activity.description}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{activity.details}</p>
                        </div>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{activity.timestamp}</span>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {quickActions.map((action) => (
              <Link
                key={action.title}
                to={action.link}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow group"
              >
                <div className={`${action.color} rounded-lg p-3 w-fit mb-4 group-hover:scale-110 transition-transform`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {action.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {action.description}
                </p>
              </Link>
            ))}
          </div>
        </div>

        <div className="mt-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Weekly Study Progress</h2>
              <ProgressTracker />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
