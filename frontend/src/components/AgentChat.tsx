import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Loader2, RefreshCw, Eye, EyeOff, Paperclip, X } from "lucide-react"
import { useAgenticAI } from "../hooks/useAgenticAi"

export const AgenticChat: React.FC = () => {
  const [input, setInput] = useState("")
  const [showPlan, setShowPlan] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [dragActive, setDragActive] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { messages, loading, error, sendMessage, clearMessages } = useAgenticAI()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleFileSelect = (files: FileList | null) => {
    if (files) {
      const newFiles = Array.from(files).filter(file => 
        file.type === 'application/pdf' || 
        file.type === 'text/plain' || 
        file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
        file.type === 'application/msword'
      )
      setSelectedFiles(prev => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && selectedFiles.length === 0) || loading) return

    const message = input.trim()
    const files = selectedFiles
    setInput("")
    setSelectedFiles([])

    try {
      // If there are files, we need to upload them first
      if (files.length > 0) {
        // Add file upload message
        const fileMessage = `Uploading ${files.length} file(s): ${files.map(f => f.name).join(', ')}`
        await sendMessage(fileMessage + (message ? `\n\n${message}` : ''), files)
      } else {
        await sendMessage(message)
      }
    } catch (err) {
      console.error("Failed to send message:", err)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-2">
          <Bot className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Study Assistant</h2>
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
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                  }`}
                >
                  {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                <div
                  className={`rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                </div>
              </div>
            </div>

            {/* Show execution details for assistant messages */}
            {message.role === "assistant" && showPlan && (message.plan || message.execution_results) && (
              <div className="ml-10 space-y-2">
                {message.plan && message.plan.length > 0 && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                    <h4 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">Execution Plan:</h4>
                    <div className="space-y-1">
                      {message.plan.map((task: any, index: number) => (
                        <div key={task.id || index} className="text-xs text-blue-800 dark:text-blue-400">
                          {index + 1}. {task.description} ({task.tool})
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {message.execution_results && message.execution_results.length > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-700">
                    <h4 className="text-sm font-medium text-green-900 dark:text-green-300 mb-2">Execution Results:</h4>
                    <div className="space-y-1">
                      {message.execution_results.map((result: any, index: number) => (
                        <div key={result.task_id || index} className="text-xs text-green-800 dark:text-green-400">
                          Task {result.task_id}: {result.status}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <Bot className="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-600 dark:text-gray-300" />
                  <span className="text-sm text-gray-600 dark:text-gray-300">AI is thinking...</span>
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
        {/* File Upload Area */}
        <div 
          className={`mb-3 border-2 border-dashed rounded-lg p-4 transition-colors ${
            dragActive 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-gray-300 dark:border-gray-600'
          } ${selectedFiles.length > 0 ? 'bg-gray-50 dark:bg-gray-700' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.doc,.docx"
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
          />
          
          {selectedFiles.length > 0 ? (
            <div className="space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">Selected files:</p>
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between bg-white dark:bg-gray-800 p-2 rounded border">
                  <span className="text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-500 hover:text-red-700 p-1"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Drag and drop files here, or{" "}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  click to select
                </button>
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Supports PDF, TXT, DOC, DOCX files
              </p>
            </div>
          )}
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about your studies..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            disabled={loading}
          >
            <Paperclip className="h-4 w-4" />
          </button>
          <button
            type="submit"
            disabled={(!input.trim() && selectedFiles.length === 0) || loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md transition-colors flex items-center space-x-2"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </form>
    </div>
  )
}