import { useState, useCallback } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  plan?: any[]
  execution_results?: any[]
}

interface UseAgenticAIReturn {
  messages: Message[]
  loading: boolean
  error: string | null
  sendMessage: (message: string) => Promise<void>
  clearMessages: () => void
}

export const useAgenticAI = (): UseAgenticAIReturn => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (message: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: message,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setError(null)

    try {
      const response = await fetch("http://localhost:5000/api/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response || "I'm here to help with your studies!",
        timestamp: new Date(),
        plan: data.plan,
        execution_results: data.execution_results,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      console.error("API Error:", err)

      // Provide a helpful mock response when backend is not available
      const mockResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I understand you want help with: "${message}"\n\nI'm currently in demo mode. Here's how I can help you:\n\n• Generate flashcards from your study materials\n• Create personalized study plans\n• Generate practice exams and quizzes\n• Answer questions about your course content\n• Track your learning progress\n\nTo get started, try uploading some course materials or ask me to create a study plan for a specific topic!`,
        timestamp: new Date(),
        plan: [
          { id: 1, description: "Analyze user request", tool: "text_analyzer" },
          { id: 2, description: "Generate appropriate response", tool: "response_generator" },
        ],
        execution_results: [
          { task_id: 1, status: "completed" },
          { task_id: 2, status: "completed" },
        ],
      }

      setMessages((prev) => [...prev, mockResponse])
      setError("Backend not available - using demo mode")
    } finally {
      setLoading(false)
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearMessages,
  }
}
