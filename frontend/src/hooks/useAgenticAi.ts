import { useState, useCallback } from "react"

interface AgenticResponse {
  response: string
  plan?: Array<{
    id: string
    description: string
    tool: string
    priority: number
    dependencies: string[]
  }>
  execution_results?: Array<{
    task_id: string
    result: any
    status: string
  }>
  memory_context_used?: boolean
  timestamp?: string
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  plan?: any
  execution_results?: any
}

export const useAgenticAI = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (message: string) => {
    setLoading(true)
    setError(null)

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: message,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])

    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:5000"
      const response = await fetch(`${baseUrl}/api/agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: AgenticResponse = await response.json()

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
        plan: data.plan,
        execution_results: data.execution_results,
      }

      setMessages((prev) => [...prev, assistantMessage])
      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message"
      setError(errorMessage)

      // Add error message
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${errorMessage}`,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMsg])
      throw err
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
