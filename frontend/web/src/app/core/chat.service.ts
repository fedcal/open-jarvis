import { Injectable, inject } from '@angular/core';
import { AuthService } from './auth.service';
import { ChatTurn, StreamEvent } from './api.types';
import { apiUrl } from './config';

/**
 * Streaming chat client. Uses fetch + ReadableStream because the
 * SSE-over-POST pattern (server expects POST /api/v1/chat with a JSON
 * body) is not directly supported by EventSource (GET-only).
 */
@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly auth = inject(AuthService);

  async *stream(turn: Omit<ChatTurn, 'turn_id'>, signal?: AbortSignal): AsyncGenerator<StreamEvent> {
    const token = this.auth.accessToken();
    if (!token) throw new Error('not authenticated');

    const response = await fetch(apiUrl('/api/v1/chat'), {
      method: 'POST',
      signal,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        Accept: 'text/event-stream'
      },
      body: JSON.stringify(turn)
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += value;

      let boundary = buffer.indexOf('\n\n');
      while (boundary !== -1) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const event = parseSseBlock(block);
        if (event) yield event;
        boundary = buffer.indexOf('\n\n');
      }
    }
  }
}

function parseSseBlock(block: string): StreamEvent | null {
  const lines = block.split('\n');
  const data: string[] = [];
  for (const line of lines) {
    if (line.startsWith('data:')) data.push(line.slice(5).trim());
  }
  if (data.length === 0) return null;
  try {
    return JSON.parse(data.join('\n')) as StreamEvent;
  } catch {
    return null;
  }
}
