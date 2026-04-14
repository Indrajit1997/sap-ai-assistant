import { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { useChat } from '../hooks/useChat';
import { Send, Trash2, Loader2 } from 'lucide-react';

const SAP_MODULES = ['All Modules', 'S4HANA', 'SuccessFactors', 'OnBase', 'CIC', 'Alfresco'];

const EXAMPLE_QUESTIONS = [
  'What is the ACDOCA table in S/4HANA?',
  'How to configure SuccessFactors Employee Central?',
  'Explain the OnBase integration with SAP',
  'What BAPIs are used for Purchase Order creation?',
];

export function ChatWindow() {
  const { messages, isLoading, send, clear } = useChat();
  const [input, setInput] = useState('');
  const [moduleFilter, setModuleFilter] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    send(input, moduleFilter || undefined);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-[#0f172a]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-lg font-bold">
            S
          </div>
          <div>
            <h1 className="text-lg font-semibold">SAP AI Assistant</h1>
            <p className="text-xs text-gray-400">RAG-powered SAP knowledge base</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            className="bg-[#1e293b] border border-gray-600 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500"
          >
            {SAP_MODULES.map((m) => (
              <option key={m} value={m === 'All Modules' ? '' : m}>
                {m}
              </option>
            ))}
          </select>
          <button
            onClick={clear}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Clear chat"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center text-3xl mb-4">
              🤖
            </div>
            <h2 className="text-xl font-semibold mb-2">Ask anything about SAP</h2>
            <p className="text-gray-400 mb-6 max-w-md">
              I'm trained on SAP documentation, KB articles, and implementation knowledge.
              Upload your documents in the sidebar to expand my knowledge.
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-lg">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => { setInput(q); }}
                  className="text-left text-sm bg-[#1e293b] hover:bg-[#2d3a4f] border border-gray-700 rounded-xl px-4 py-3 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              role={msg.role}
              content={msg.content}
              sources={msg.sources}
              isStreaming={msg.isStreaming}
            />
          ))
        )}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-400 mb-4">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Searching knowledge base...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-700 bg-[#0f172a]">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about SAP S/4HANA, SuccessFactors, Hyland integrations..."
            rows={1}
            className="flex-1 bg-[#1e293b] border border-gray-600 rounded-xl px-4 py-3 resize-none focus:outline-none focus:border-blue-500 placeholder:text-gray-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl px-4 py-3 transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
