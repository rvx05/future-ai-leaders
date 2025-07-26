import type React from "react"
import { useEffect } from "react"
import { Link } from "react-router-dom"
import { CreditCard, FileText, Upload, Calendar, TrendingUp, Clock, Target } from "lucide-react"
import { ProgressTracker } from "../components/ProgressTracker"
import { AgenticChat } from "../components/AgenticChat"
import { useApi } from "../hooks/useApi"

export const Dashboard: React.FC = () => {
  const {
    data: progressData,
    loading,
    callApi,
  } = useApi<{
    weeklyProgress: number
    overallProgress: number
    studyStreak: number
    totalStudyTime: number
  }>()

  useEffect(() => {
    // Try to get real data from backend, fallback to mock data
    callApi("/api/memory").catch(() => {
      // Fallback to mock data if backend is not available
      const mockData = {
        weeklyProgress: 75,
        overallProgress: 60,
        studyStreak: 7,
        totalStudyTime: 45,
      }
      // Set mock data manually for display
    })
  }, [callApi])

  const quickActions = [
    {
      title: "Generate Flashcards",
      description: "Create AI-powered flashcards from your notes",
      icon: CreditCard,
      link: "/flashcards",
      color: "bg-blue-500",
    },
    {
      title: "Practice Exam",
      description: "Test your knowledge with custom quizzes",
      icon: FileText,
      link: "/exam",
      color: "bg-emerald-500",
    },
    {
      title: "Upload Content",
      description: "Add new course materials",
      icon: Upload,
      link: "/upload",
      color: "bg-purple-500",
    },
    {
      title: "Study Plan",
      description: "Create personalized study schedules",
      icon: Calendar,
      link: "/study-plan",
      color: "bg-orange-500",
    },
  ]

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Welcome to AI Study Buddy</h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Your intelligent learning companion powered by Agentic AI
        </p>
      </div>

      {/* AI Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Chat with your AI Study Assistant</h2>
          <AgenticChat />
        </div>

        <div className="space-y-6">
          {/* Progress Overview */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Progress Overview</h3>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <TrendingUp className="h-6 w-6 text-blue-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Weekly Progress</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {loading ? "..." : `${progressData?.weeklyProgress || 75}%`}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <Target className="h-6 w-6 text-emerald-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Overall Progress</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {loading ? "..." : `${progressData?.overallProgress || 60}%`}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <Calendar className="h-6 w-6 text-purple-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Study Streak</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {loading ? "..." : `${progressData?.studyStreak || 7} days`}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <Clock className="h-6 w-6 text-orange-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Study Time</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {loading ? "..." : `${progressData?.totalStudyTime || 45}h`}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              {quickActions.map((action) => (
                <Link
                  key={action.title}
                  to={action.link}
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow group flex items-center space-x-3"
                >
                  <div className={`${action.color} rounded-lg p-2 group-hover:scale-110 transition-transform`}>
                    <action.icon className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm">{action.title}</h4>
                    <p className="text-gray-600 dark:text-gray-400 text-xs">{action.description}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Tracker */}
      <ProgressTracker />

      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 dark:bg-blue-900 rounded p-2">
                <CreditCard className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Generated 15 flashcards</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">React Fundamentals</p>
              </div>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</span>
          </div>

          <div className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-3">
              <div className="bg-emerald-100 dark:bg-emerald-900 rounded p-2">
                <FileText className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Completed practice exam</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Score: 85%</p>
              </div>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">1 day ago</span>
          </div>

          <div className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-3">
              <div className="bg-purple-100 dark:bg-purple-900 rounded p-2">
                <Upload className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Uploaded course material</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">TypeScript Advanced Concepts.pdf</p>
              </div>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">2 days ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}
