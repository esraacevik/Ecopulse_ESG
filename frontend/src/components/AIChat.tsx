'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader2, Lightbulb } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { aiAPI } from '@/services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface AIChatProps {
  context?: any
}

export default function AIChat({ context }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Merhaba! ESG ve karbon emisyonları hakkında sorularınızı yanıtlayabilirim. Nasıl yardımcı olabilirim?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await aiAPI.chat(input, context)
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: err.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 shadow-xl h-[600px] flex flex-col"
    >
      <div className="flex items-center gap-3 mb-4 pb-4 border-b border-sage-200">
        <div className="p-2 bg-forest-100 rounded-lg">
          <Bot className="w-6 h-6 text-forest-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-forest-700">AI Assistant</h3>
          <p className="text-xs text-sage-500">ESG & Carbon Emissions Expert</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="p-2 bg-forest-100 rounded-lg self-start">
                  <Bot className="w-4 h-4 text-forest-600" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-forest-600 text-white'
                    : 'bg-white border border-sage-200 text-sage-700'
                }`}
              >
                {message.role === 'assistant' ? (
                  <div className="text-sm markdown-content">
                    <ReactMarkdown
                      components={{
                        strong: ({node, ...props}) => <strong className="font-semibold text-forest-700" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                        li: ({node, ...props}) => <li className="ml-2" {...props} />,
                        h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-2 text-forest-700" {...props} />,
                        h2: ({node, ...props}) => <h2 className="text-base font-bold mb-2 text-forest-700" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-sm font-bold mb-1 text-forest-700" {...props} />,
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                )}
                <p className={`text-xs mt-2 ${
                  message.role === 'user' ? 'text-forest-100' : 'text-sage-400'
                }`}>
                  {typeof window !== 'undefined' ? message.timestamp.toLocaleTimeString() : ''}
                </p>
              </div>
              {message.role === 'user' && (
                <div className="p-2 bg-forest-100 rounded-lg self-start">
                  <User className="w-4 h-4 text-forest-600" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="p-2 bg-forest-100 rounded-lg">
              <Bot className="w-4 h-4 text-forest-600" />
            </div>
            <div className="bg-white border border-sage-200 rounded-lg p-4">
              <Loader2 className="w-5 h-5 animate-spin text-forest-600" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Example Questions */}
      {messages.length <= 1 && (
        <div className="mb-4 p-4 bg-forest-50 rounded-lg border border-forest-100">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-4 h-4 text-forest-600" />
            <span className="text-sm font-medium text-forest-700">Örnek Sorular</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              'Scope 1 emisyonları nedir?',
              'GRI 305 standardı nedir?',
              'Net Zero hedefi nedir?',
              'Carbon offsetting nedir?',
              'GHG Protocol nedir?',
              'CDP nedir?'
            ].map((question) => (
              <button
                key={question}
                onClick={() => {
                  setInput(question)
                }}
                className="px-3 py-1.5 text-xs bg-white hover:bg-forest-100 text-sage-700 hover:text-forest-700 rounded-full border border-sage-200 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2 pt-4 border-t border-sage-200">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="ESG, karbon emisyonları, Scope 1/2/3 hakkında sorun..."
          className="flex-1 px-4 py-3 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </motion.div>
  )
}

