import ReactMarkdown from 'react-markdown';
import type { Source } from '../services/api';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  isStreaming?: boolean;
}

export function MessageBubble({ role, content, sources, isStreaming }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'flex-row-reverse' : ''}`}>
          <div
            className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
              isUser ? 'bg-blue-600' : 'bg-emerald-600'
            }`}
          >
            {isUser ? 'U' : 'AI'}
          </div>
          <span className="text-xs text-gray-400">
            {isUser ? 'You' : 'SAP Assistant'}
          </span>
        </div>

        {/* Message */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-sm'
              : 'bg-[#1e293b] text-gray-100 rounded-tl-sm border border-gray-700'
          }`}
        >
          <div className={`prose prose-invert max-w-none ${isStreaming ? 'typing-cursor' : ''}`}>
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>

        {/* Sources */}
        {sources && sources.length > 0 && (
          <SourcePanel sources={sources} />
        )}
      </div>
    </div>
  );
}

function SourcePanel({ sources }: { sources: Source[] }) {
  return (
    <details className="mt-2 group">
      <summary className="text-xs text-blue-400 cursor-pointer hover:text-blue-300 select-none">
        📚 {sources.length} source{sources.length > 1 ? 's' : ''} referenced
      </summary>
      <div className="mt-2 space-y-2">
        {sources.map((src) => (
          <div
            key={src.index}
            className="bg-[#0f172a] border border-gray-700 rounded-lg p-3 text-sm"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-blue-400">
                [Source {src.index}] {src.source.split(/[/\\]/).pop()}
              </span>
              <span className="bg-blue-600/20 text-blue-400 px-2 py-0.5 rounded-full text-xs">
                {(src.score * 100).toFixed(0)}% match
              </span>
            </div>
            {src.page && (
              <span className="text-xs text-gray-500">Page {src.page}</span>
            )}
            {src.module && (
              <span className="ml-2 text-xs bg-gray-700 px-2 py-0.5 rounded">
                {src.module}
              </span>
            )}
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">{src.preview}</p>
          </div>
        ))}
      </div>
    </details>
  );
}
