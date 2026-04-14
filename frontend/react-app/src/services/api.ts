const API_BASE = '/api/v1';

export interface Source {
  index: number;
  source: string;
  page?: number;
  module?: string;
  score: number;
  preview: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  model: string;
  usage?: { input_tokens: number; output_tokens: number };
}

export interface HealthResponse {
  status: string;
  version: string;
  vector_store: string;
  document_count: number;
}

export async function sendMessage(
  question: string,
  moduleFilter?: string,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      module_filter: moduleFilter || null,
      stream: false,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function* streamMessage(
  question: string,
  moduleFilter?: string,
): AsyncGenerator<{ type: 'token' | 'sources' | 'done' | 'error'; data: unknown }> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      module_filter: moduleFilter || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('event:')) {
        const eventType = line.slice(6).trim();
        continue;
      }
      if (line.startsWith('data:')) {
        const data = line.slice(5).trim();
        try {
          const parsed = JSON.parse(data);
          if (parsed.token !== undefined) {
            yield { type: 'token', data: parsed.token };
          } else if (parsed.sources) {
            yield { type: 'sources', data: parsed.sources };
          } else if (parsed.error) {
            yield { type: 'error', data: parsed.error };
          }
        } catch {
          // skip malformed JSON
        }
      }
    }
  }

  yield { type: 'done', data: null };
}

export async function uploadDocument(file: File, module?: string): Promise<{ chunks_created: number }> {
  const formData = new FormData();
  formData.append('file', file);

  const url = module
    ? `${API_BASE}/documents/upload?module=${encodeURIComponent(module)}`
    : `${API_BASE}/documents/upload`;

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload error: ${response.status}`);
  }

  return response.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
