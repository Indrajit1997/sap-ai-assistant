import { useState, useRef } from 'react';
import { uploadDocument } from '../services/api';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

export function DocumentUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const [module, setModule] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setResult(null);
    try {
      const res = await uploadDocument(file, module || undefined);
      setResult({ success: true, message: `Ingested ${res.chunks_created} chunks from ${file.name}` });
    } catch {
      setResult({ success: false, message: `Failed to upload ${file.name}` });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  return (
    <div className="p-4 bg-[#0f172a] border border-gray-700 rounded-xl">
      <h3 className="font-medium mb-3 flex items-center gap-2">
        <FileText size={16} /> Upload Documents
      </h3>

      <input
        type="text"
        value={module}
        onChange={(e) => setModule(e.target.value)}
        placeholder="SAP Module tag (optional)"
        className="w-full bg-[#1e293b] border border-gray-600 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:border-blue-500"
      />

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
          isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-gray-600 hover:border-gray-500'
        }`}
      >
        <Upload size={24} className="mx-auto mb-2 text-gray-400" />
        <p className="text-sm text-gray-400">
          {uploading ? 'Processing...' : 'Drop files here or click to upload'}
        </p>
        <p className="text-xs text-gray-500 mt-1">PDF, HTML, MD, TXT, DOCX</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.html,.htm,.md,.txt,.docx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUpload(file);
        }}
      />

      {result && (
        <div className={`mt-3 flex items-center gap-2 text-sm ${result.success ? 'text-green-400' : 'text-red-400'}`}>
          {result.success ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
          {result.message}
        </div>
      )}
    </div>
  );
}
