import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../core/auth.service';
import { ChatService } from '../../core/chat.service';
import { LlmService } from '../../core/llm.service';
import { ChatTurn } from '../../core/api.types';

interface Bubble {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  pending?: boolean;
}

@Component({
  selector: 'oj-chat',
  standalone: true,
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col">
      <header class="mb-4 flex items-center justify-between gap-3">
        <h1 class="text-2xl font-semibold">Chat</h1>
        <div class="text-xs text-slate-500">
          Backend:
          <span class="font-medium text-slate-700 dark:text-slate-200">
            {{ llm.preferredBackend() ?? 'auto (LOCAL_FIRST)' }}
          </span>
        </div>
      </header>

      <div class="oj-card flex-1 overflow-y-auto p-4 space-y-4" #scroller>
        @if (bubbles().length === 0) {
          <div class="flex h-full items-center justify-center text-center text-sm text-slate-500">
            Inizia una conversazione: Jarvis ricorderà ciò che gli racconti.
          </div>
        }
        @for (bubble of bubbles(); track bubble.id) {
          <div class="flex" [class.justify-end]="bubble.role === 'user'">
            <div
              class="max-w-[80%] rounded-2xl px-4 py-2 text-sm leading-relaxed"
              [class.bg-jarvis-600]="bubble.role === 'user'"
              [class.text-white]="bubble.role === 'user'"
              [class.bg-slate-100]="bubble.role !== 'user'"
              [class.dark:bg-slate-800]="bubble.role !== 'user'"
            >
              @if (bubble.content) {
                <span style="white-space: pre-wrap">{{ bubble.content }}</span>
              } @else {
                <span class="inline-flex gap-1">
                  <span class="h-2 w-2 animate-bounce rounded-full bg-current"></span>
                  <span class="h-2 w-2 animate-bounce rounded-full bg-current" style="animation-delay: 0.15s"></span>
                  <span class="h-2 w-2 animate-bounce rounded-full bg-current" style="animation-delay: 0.3s"></span>
                </span>
              }
            </div>
          </div>
        }
      </div>

      <form
        (submit)="$event.preventDefault(); send()"
        class="mt-4 flex gap-2 oj-card p-2"
      >
        <input
          class="flex-1 bg-transparent px-2 outline-none"
          placeholder="Scrivi a Jarvis…"
          [(ngModel)]="draft"
          name="draft"
          [disabled]="streaming()"
          autocomplete="off"
          autofocus
        />
        <button class="oj-btn-primary" type="submit" [disabled]="streaming() || !draft.trim()">
          {{ streaming() ? '…' : 'Invia' }}
        </button>
      </form>

      @if (errorMessage()) {
        <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ errorMessage() }}</p>
      }
    </div>
  `
})
export class ChatPage {
  private readonly chat = inject(ChatService);
  private readonly auth = inject(AuthService);
  protected readonly llm = inject(LlmService);

  draft = '';
  bubbles = signal<Bubble[]>([]);
  streaming = signal(false);
  errorMessage = signal<string | null>(null);

  private readonly sessionId = crypto.randomUUID();
  private readonly deviceId = crypto.randomUUID();

  readonly userId = computed(() => this.auth.user()?.id ?? '');

  async send(): Promise<void> {
    const text = this.draft.trim();
    if (!text) return;
    this.errorMessage.set(null);

    const userBubble: Bubble = { id: crypto.randomUUID(), role: 'user', content: text };
    const assistantBubble: Bubble = { id: crypto.randomUUID(), role: 'assistant', content: '', pending: true };
    this.bubbles.update((arr) => [...arr, userBubble, assistantBubble]);
    this.draft = '';
    this.streaming.set(true);

    const turn: Omit<ChatTurn, 'turn_id'> = {
      session_id: this.sessionId,
      device_id: this.deviceId,
      user_id: this.userId(),
      modality: 'text',
      message: text,
      language: 'it'
    };

    try {
      for await (const ev of this.chat.stream(turn)) {
        if (ev.type === 'chunk' && ev.content) {
          this.appendToAssistant(assistantBubble.id, ev.content);
        } else if (ev.type === 'end') {
          this.markComplete(assistantBubble.id);
        } else if (ev.type === 'error') {
          this.errorMessage.set('Errore nello stream del modello.');
          this.markComplete(assistantBubble.id);
        }
      }
    } catch (err: unknown) {
      this.errorMessage.set(this.parseError(err));
      this.markComplete(assistantBubble.id);
    } finally {
      this.streaming.set(false);
    }
  }

  private appendToAssistant(id: string, delta: string): void {
    this.bubbles.update((arr) =>
      arr.map((b) => (b.id === id ? { ...b, content: b.content + delta, pending: false } : b))
    );
  }

  private markComplete(id: string): void {
    this.bubbles.update((arr) =>
      arr.map((b) => (b.id === id ? { ...b, pending: false } : b))
    );
  }

  private parseError(err: unknown): string {
    if (err instanceof Error) return err.message;
    return 'Errore di rete.';
  }
}
