import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe, DecimalPipe } from '@angular/common';

import { MemoryService } from '../../core/memory.service';
import { MemoryHit, MemoryItemPublic } from '../../core/api.types';

@Component({
  selector: 'oj-memory',
  standalone: true,
  imports: [FormsModule, DatePipe, DecimalPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="mx-auto max-w-3xl">
      <h1 class="mb-4 text-2xl font-semibold">Memoria</h1>

      <div class="oj-card mb-6 p-4">
        <h2 class="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Aggiungi un ricordo
        </h2>
        <form (submit)="$event.preventDefault(); addMemory()" class="space-y-2">
          <textarea
            class="oj-input min-h-[6rem]"
            [(ngModel)]="newContent"
            name="newContent"
            placeholder="Es. il mio caffè preferito è americano lungo, latte freddo a parte"
          ></textarea>
          <div class="flex justify-end">
            <button class="oj-btn-primary" [disabled]="busy() || !newContent.trim()">Salva</button>
          </div>
        </form>
      </div>

      <div class="oj-card mb-6 p-4">
        <h2 class="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Cerca semantica
        </h2>
        <form (submit)="$event.preventDefault(); doSearch()" class="flex gap-2">
          <input class="oj-input" [(ngModel)]="query" name="query" placeholder="Cosa cerco…" />
          <button class="oj-btn-primary" [disabled]="!query.trim()">Cerca</button>
        </form>
        @if (hits().length > 0) {
          <ul class="mt-4 space-y-2">
            @for (h of hits(); track h.item.id) {
              <li class="rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
                <div class="mb-1 flex items-center justify-between text-xs text-slate-500">
                  <span>{{ h.item.kind }}</span>
                  <span>score: {{ h.score | number:'1.3-3' }}</span>
                </div>
                {{ h.item.content }}
              </li>
            }
          </ul>
        }
      </div>

      <div class="oj-card p-4">
        <h2 class="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Ricordi recenti
        </h2>
        @if (items().length === 0) {
          <p class="text-sm text-slate-500">Nessun ricordo ancora.</p>
        }
        <ul class="space-y-2">
          @for (item of items(); track item.id) {
            <li class="flex items-start justify-between gap-3 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
              <div class="flex-1 min-w-0">
                <div class="mb-1 text-xs text-slate-500">
                  {{ item.kind }} · {{ item.created_at | date:'short' }}
                </div>
                <div class="break-words">{{ item.content }}</div>
              </div>
              <button class="oj-btn-ghost text-red-600" type="button" (click)="forget(item)" title="Dimentica">
                ✕
              </button>
            </li>
          }
        </ul>
      </div>
    </div>
  `
})
export class MemoryPage implements OnInit {
  private readonly memory = inject(MemoryService);

  newContent = '';
  query = '';
  busy = signal(false);
  items = signal<MemoryItemPublic[]>([]);
  hits = signal<MemoryHit[]>([]);

  async ngOnInit(): Promise<void> {
    await this.refresh();
  }

  async refresh(): Promise<void> {
    try {
      this.items.set(await this.memory.list(50));
    } catch {
      // ignore
    }
  }

  async addMemory(): Promise<void> {
    const text = this.newContent.trim();
    if (!text) return;
    this.busy.set(true);
    try {
      await this.memory.record(text);
      this.newContent = '';
      await this.refresh();
    } finally {
      this.busy.set(false);
    }
  }

  async doSearch(): Promise<void> {
    const q = this.query.trim();
    if (!q) return;
    const r = await this.memory.search(q, 5);
    this.hits.set(r.hits);
  }

  async forget(item: MemoryItemPublic): Promise<void> {
    await this.memory.forget(item.id);
    await this.refresh();
  }
}
