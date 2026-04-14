import { useEffect, useState } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { DocumentUpload } from './components/DocumentUpload';
import { getHealth, type HealthResponse } from './services/api';
import { Database, Activity } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  useEffect(() => {
    const fetchHealth = () => {
      getHealth()
        .then(setHealth)
        .catch(() => setHealth(null));
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      {showSidebar && (
        <aside className="w-80 border-r border-gray-700 bg-[#0f172a] flex flex-col overflow-y-auto">
          <div className="p-4 border-b border-gray-700">
            <h2 className="font-semibold text-sm text-gray-400 uppercase tracking-wider">
              Knowledge Base
            </h2>
          </div>

          {/* Stats */}
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between bg-[#1e293b] rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm">
                <Database size={14} className="text-blue-400" />
                Documents
              </div>
              <span className="text-blue-400 font-mono">
                {health?.document_count ?? '—'}
              </span>
            </div>
            <div className="flex items-center justify-between bg-[#1e293b] rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm">
                <Activity size={14} className={health ? 'text-green-400' : 'text-red-400'} />
                Status
              </div>
              <span className={`text-sm ${health ? 'text-green-400' : 'text-red-400'}`}>
                {health ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>

          {/* Upload */}
          <div className="p-4 flex-1">
            <DocumentUpload />
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-700 text-xs text-gray-500 text-center">
            SAP AI Assistant v0.1.0 — Hackathon 2026
          </div>
        </aside>
      )}

      {/* Main */}
      <main className="flex-1">
        <ChatWindow />
      </main>
    </div>
  );
}
