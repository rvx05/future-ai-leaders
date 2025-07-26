import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Loader2, RefreshCw, Eye, EyeOff, Brain } from "lucide-react"
import { useAgenticAI } from "../hooks/useAgenticAi"

export const AgenticChat: React.FC = () => {
  const [input, setInput] = useState("")
  const [showPlan, setShowPlan] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
    const { messages, loading, error, sendMessage, clearMessages } = useAgenticAI()
  const [placeholder, setPlaceholder] = useState('Ask me anything about your course materials...')

  const placeholders = [
    'Summarize my notes on photosynthesis...',
    'Create 10 flashcards for my history exam.',
    'Quiz me on the key concepts of calculus.',
    'Help me build a study plan for next week.',
    'Explain the concept of recursion in simple terms.',
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      const randomIndex = Math.floor(Math.random() * placeholders.length)
      setPlaceholder(placeholders[randomIndex])
    }, 5000) // Change placeholder every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const message = input.trim()
    setInput("")

    try {
      await sendMessage(message)
    } catch (err) {
      console.error("Failed to send message:", err)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-2">
          <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Study Buddy Assistant</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPlan(!showPlan)}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            title={showPlan ? "Hide execution details" : "Show execution details"}
          >
            {showPlan ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
          <button
            onClick={clearMessages}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            title="Clear conversation"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <Bot className="h-12 w-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
            <p className="text-lg font-medium mb-2">Welcome to your AI Study Assistant!</p>
            <p className="text-sm">
              Ask me to help you create flashcards, generate study plans, or answer questions about your course
              materials.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className="space-y-2">
            <div className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`flex items-start space-x-2 max-w-[80%] ${
                  message.role === "user" ? "flex-row-reverse space-x-reverse" : ""
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                  }`}
                >
                  {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                <div
                  className={`rounded-lg p-3 shadow-sm ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1 text-right">{message.timestamp.toLocaleTimeString()}</p>
                </div>
              </div>
            </div>
            {showPlan && message.plan && (
              <div className="flex justify-start">
                <div className="ml-10 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg w-[calc(80%-40px)]">
                  <p className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">Execution Plan:</p>
                  <pre className="text-xs text-gray-500 dark:text-gray-400 whitespace-pre-wrap font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded">{JSON.stringify(message.plan, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-lg p-3 shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <div className="flex items-center space-x-1">
                  <span className="h-2 w-2 bg-blue-500 rounded-full animate-pulse delay-0"></span>
                  <span className="h-2 w-2 bg-blue-500 rounded-full animate-pulse delay-150"></span>
                  <span className="h-2 w-2 bg-blue-500 rounded-full animate-pulse delay-300"></span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-700 flex-shrink-0">
          <p className="text-sm text-red-700 dark:text-red-400">Error: {error}</p>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={placeholder}
            className="w-full px-4 py-2 border-t border-gray-200 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-shadow"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md transition-colors flex items-center space-x-2"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </form>
    </div>
  )
}
