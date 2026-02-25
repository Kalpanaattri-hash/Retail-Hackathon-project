import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, AlertCircle, Code2 } from 'lucide-react';
import { apiClient, ChatResponse } from '../api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  data?: Record<string, unknown>[];
  error?: string;
  timestamp: Date;
}

export const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Hi! I am your Sales Analytics Assistant. Ask me questions about your sales data. For example: "What were total sales last month?" or "Which region had highest revenue in Q4?"',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSQL, setShowSQL] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    setError(null);
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response: ChatResponse = await apiClient.askQuestion(input);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sql: response.generated_sql,
        data: response.data_preview,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Failed to get response from the server. Please check if the backend is running.';

      setError(errorMessage);

      const errorAssistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I encountered an error: ${errorMessage}`,
        error: errorMessage,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorAssistantMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <h1 className="text-2xl font-bold text-brand-900">Sales Analytics Assistant</h1>
        <p className="text-sm text-gray-600">Powered by Claude 3 & Amazon Bedrock</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md rounded-lg px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-brand-600 text-white'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <p className="text-sm leading-relaxed">{msg.content}</p>

                {msg.sql && (
                  <button
                    onClick={() => setShowSQL(showSQL === msg.sql ? null : msg.sql!)}
                    className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700"
                  >
                    <Code2 size={14} />
                    {showSQL === msg.sql ? 'Hide SQL' : 'Show SQL'}
                  </button>
                )}

                {showSQL === msg.sql && (
                  <pre className="mt-2 overflow-x-auto bg-gray-100 p-2 text-xs text-gray-800 rounded">
                    {msg.sql}
                  </pre>
                )}

                {msg.data && msg.data.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-semibold text-gray-600 mb-1">Data Preview:</p>
                    <div className="max-h-48 overflow-x-auto">
                      <table className="w-full text-xs text-gray-700 border-collapse">
                        <thead>
                          <tr>
                            {Object.keys(msg.data[0] || {}).map((key) => (
                              <th
                                key={key}
                                className="bg-gray-100 px-2 py-1 text-left font-semibold border border-gray-300"
                              >
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {msg.data.slice(0, 5).map((row, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              {Object.values(row).map((val, valIdx) => (
                                <td key={valIdx} className="px-2 py-1 border border-gray-300">
                                  {String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {msg.data.length > 5 && (
                        <p className="mt-1 text-xs text-gray-500">
                          ... and {msg.data.length - 5} more rows
                        </p>
                      )}
                    </div>
                  </div>
                )}

                <p className="mt-1 text-xs opacity-70">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                <Loader className="h-5 w-5 animate-spin text-brand-600" />
              </div>
            </div>
          )}

          {error && (
            <div className="flex justify-start">
              <div className="flex gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3 max-w-md">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-red-700">{error}</div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white px-6 py-4 shadow-lg">
        <form onSubmit={handleSubmit} className="mx-auto max-w-3xl flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about sales data... (e.g., Total sales last month?)"
            disabled={loading}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm placeholder-gray-500 focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 font-medium text-white hover:bg-brand-700 disabled:bg-gray-400"
          >
            {loading ? (
              <Loader size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
