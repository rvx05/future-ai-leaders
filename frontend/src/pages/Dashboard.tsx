import type React from "react"
import { useEffect, useState } from "react"
import { AgenticChat } from "../components/AgenticChat"
import { ProgressTracker } from "../components/ProgressTracker"
import { BookOpen, Clock, Target, TrendingUp, Calendar, FileText, Upload } from "lucide-react"

interface StudyStats {
  totalHours: number
  completedSessions: number
  streak: number
  averageScore: number
}

export const Dashboard: React.FC = () => {
  const [studyStats, setStudyStats] = useState<StudyStats>({
    totalHours: 0,
    completedSessions: 0,
    streak: 0,
    averageScore: 0,
  })

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0)

    // Mock data for demonstration
    setStudyStats({
      totalHours: 24.5,
      completedSessions: 12,
      streak: 7,
      averageScore: 85,
    })
  }, [])

  const quickActions = [
    { icon: BookOpen, label: "Start Study Session", color: "bg-blue-500", href: "/flashcards" },
    { icon: FileText, label: "Take Practice Exam", color: "bg-green-500", href: "/exam" },
    { icon: Upload, label: "Upload Materials", color: "bg-purple-500", href: "/upload" },
    { icon: Calendar, label: "View Study Plan", color: "bg-orange-500", href: "/study-plan" },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back to your AI Study Buddy!
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Let's continue your learning journey. Here's your progress overview.
          </p>
        </div>

        {/* Main Content Grid - Responsive layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* AI Chat Section - Full width on mobile, 2/3 on desktop */}
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

          {/* Right Sidebar - Stack vertically on mobile */}
          <div className="space-y-6 lg:space-y-0 lg:flex lg:flex-col lg:h-[800px] lg:gap-6">
            {/* Progress Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 lg:flex-1">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Progress Overview</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Clock className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{studyStats.totalHours}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Hours Studied</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <Target className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {studyStats.completedSessions}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Sessions</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <TrendingUp className="h-8 w-8 text-orange-600 dark:text-orange-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{studyStats.streak}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Day Streak</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <BookOpen className="h-8 w-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{studyStats.averageScore}%</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Avg Score</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 lg:flex-1">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3">
                  {quickActions.map((action, index) => (
                    <a
                      key={index}
                      href={action.href}
                      className="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors group"
                    >
                      <div
                        className={`p-2 rounded-lg ${action.color} text-white mr-4 group-hover:scale-110 transition-transform`}
                      >
                        <action.icon className="h-5 w-5" />
                      </div>
                      <span className="font-medium text-gray-900 dark:text-white">{action.label}</span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Progress Section */}
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
  )
}
