import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  IonContent, IonHeader, IonToolbar, IonTitle, IonFooter,
  IonInput, IonButton, IonItem
} from '@ionic/angular/standalone';

import { AuthService } from '../core/auth.service';
import { ChatService } from '../core/chat.service';

interface Bubble {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'oj-chat',
  standalone: true,
  imports: [
    FormsModule,
    IonContent, IonHeader, IonToolbar, IonTitle, IonFooter,
    IonInput, IonButton, IonItem
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ion-header><ion-toolbar><ion-title>Chat</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      @for (b of bubbles(); track b.id) {
        <div [class.user]="b.role === 'user'" class="bubble"
             [style.background]="b.role === 'user' ? 'var(--ion-color-primary)' : 'var(--ion-color-light)'"
             [style.color]="b.role === 'user' ? 'var(--ion-color-primary-contrast)' : 'var(--ion-color-light-contrast)'">
          <pre style="white-space: pre-wrap; margin: 0; font-family: inherit">{{ b.content || '…' }}</pre>
        </div>
      }
      @if (bubbles().length === 0) {
        <p class="ion-text-center ion-padding">Inizia una conversazione.</p>
      }
    </ion-content>
    <ion-footer>
      <ion-toolbar>
        <ion-item lines="none">
          <ion-input [(ngModel)]="draft" name="draft" placeholder="Scrivi…" [disabled]="streaming()" />
          <ion-button slot="end" (click)="send()" [disabled]="streaming() || !draft.trim()">Invia</ion-button>
        </ion-item>
      </ion-toolbar>
    </ion-footer>
  `,
  styles: [`
    .bubble {
      display: inline-block;
      max-width: 80%;
      margin: 0.25rem 0;
      padding: 0.5rem 0.75rem;
      border-radius: 1rem;
    }
    .user { float: right; clear: both; }
  `]
})
export class ChatPage {
  private readonly chat = inject(ChatService);
  private readonly auth = inject(AuthService);

  draft = '';
  bubbles = signal<Bubble[]>([]);
  streaming = signal(false);
  private readonly sessionId = crypto.randomUUID();
  private readonly deviceId = crypto.randomUUID();
  readonly userId = computed(() => this.auth.user()?.id ?? '');

  async send(): Promise<void> {
    const text = this.draft.trim();
    if (!text) return;

    const userBubble: Bubble = { id: crypto.randomUUID(), role: 'user', content: text };
    const aiBubble: Bubble = { id: crypto.randomUUID(), role: 'assistant', content: '' };
    this.bubbles.update((arr) => [...arr, userBubble, aiBubble]);
    this.draft = '';
    this.streaming.set(true);

    try {
      for await (const ev of this.chat.stream({
        session_id: this.sessionId,
        device_id: this.deviceId,
        user_id: this.userId(),
        modality: 'text',
        message: text,
        language: 'it'
      })) {
        if (ev.type === 'chunk' && ev.content) {
          this.bubbles.update((arr) =>
            arr.map((b) => (b.id === aiBubble.id ? { ...b, content: b.content + ev.content } : b))
          );
        }
      }
    } catch {
      this.bubbles.update((arr) =>
        arr.map((b) => (b.id === aiBubble.id ? { ...b, content: '⚠️ errore' } : b))
      );
    } finally {
      this.streaming.set(false);
    }
  }
}
