import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';

import { LlmService } from '../../core/llm.service';
import { BackendInfo, OllamaModel } from '../../core/api.types';
import { getApiBaseUrl, setApiBaseUrl } from '../../core/config';

@Component({
  selector: 'oj-settings',
  standalone: true,
  imports: [FormsModule, DecimalPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="mx-auto max-w-3xl space-y-6">
      <h1 class="text-2xl font-semibold">Impostazioni</h1>

      <!-- Server -->
      <section class="oj-card p-6">
        <h2 class="mb-4 text-lg font-semibold">Server</h2>
        <label class="oj-label" for="apiUrl">URL del server</label>
        <input id="apiUrl" class="oj-input font-mono text-sm" [(ngModel)]="apiUrl" name="apiUrl" />
        <div class="mt-2 flex gap-2">
          <button class="oj-btn-primary" type="button" (click)="saveApiUrl()">Salva</button>
          <button class="oj-btn-ghost" type="button" (click)="resetApiUrl()">Stessa origin</button>
        </div>
        <p class="mt-2 text-xs text-slate-500">
          Esempi: <code>http://192.168.1.42:8090</code>, <code>https://jarvis.local</code>,
          <code>https://jarvis.example.com</code>.
        </p>
      </section>

      <!-- LLM Backends -->
      <section class="oj-card p-6">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold">Modelli LLM</h2>
          <button class="oj-btn-ghost" type="button" (click)="reload()">Aggiorna</button>
        </div>

        <p class="mb-4 text-sm text-slate-500">
          Scegli quale backend usare per la chat. <strong>Auto</strong> rispetta la policy
          <code>LOCAL_FIRST</code> del server.
        </p>

        <ul class="mb-6 space-y-2">
          <li>
            <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-700">
              <input type="radio" name="backend" [checked]="!llm.preferredBackend()" (change)="select(null)" />
              <div class="flex-1">
                <div class="font-medium">Auto (LOCAL_FIRST)</div>
                <div class="text-xs text-slate-500">Predefinito server: {{ defaultBackend() }}</div>
              </div>
            </label>
          </li>
          @for (b of backends(); track b.name) {
            <li>
              <label class="flex cursor-pointer items-center gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                <input type="radio" name="backend" [checked]="llm.preferredBackend() === b.name" (change)="select(b.name)" />
                <div class="flex-1">
                  <div class="font-medium">
                    {{ b.name }}
                    @if (b.is_local) {
                      <span class="ml-2 rounded bg-emerald-100 px-1.5 py-0.5 text-xs text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">locale</span>
                    } @else {
                      <span class="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300">cloud</span>
                    }
                  </div>
                  <div class="text-xs text-slate-500">model: <code>{{ b.model }}</code></div>
                </div>
              </label>
            </li>
          }
        </ul>

        <!-- Ollama models detail -->
        <h3 class="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
          Modelli Ollama installati
        </h3>
        @if (ollamaError()) {
          <p class="rounded-md bg-amber-50 p-2 text-sm text-amber-700 dark:bg-amber-950 dark:text-amber-200">
            Ollama non raggiungibile su <code>{{ ollamaBaseUrl() }}</code>.
            Avvia il daemon con <code>ollama serve</code> e poi <code>ollama pull llama3.2:3b</code>.
          </p>
        } @else if (ollamaModels().length === 0) {
          <p class="text-sm text-slate-500">Nessun modello scaricato.</p>
        } @else {
          <ul class="space-y-1">
            @for (m of ollamaModels(); track m.name) {
              <li class="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-sm dark:border-slate-700">
                <code>{{ m.name }}</code>
                <span class="text-xs text-slate-500">
                  {{ m.parameter_size ?? '?' }} · {{ (m.size / 1024 / 1024) | number:'1.0-0' }} MB
                </span>
              </li>
            }
          </ul>
        }

        <details class="mt-4 text-xs text-slate-500">
          <summary class="cursor-pointer">Come scaricare nuovi modelli Ollama</summary>
          <pre class="mt-2 rounded bg-slate-100 p-3 dark:bg-slate-800"><code>ollama serve            # daemon
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama list             # vedi i modelli installati</code></pre>
        </details>
      </section>
    </div>
  `
})
export class SettingsPage implements OnInit {
  protected readonly llm = inject(LlmService);

  apiUrl = getApiBaseUrl();
  backends = signal<BackendInfo[]>([]);
  defaultBackend = signal<string>('?');
  ollamaModels = signal<OllamaModel[]>([]);
  ollamaError = signal<string | null>(null);
  ollamaBaseUrl = signal<string>('?');

  async ngOnInit(): Promise<void> {
    await this.reload();
  }

  async reload(): Promise<void> {
    try {
      const b = await this.llm.listBackends();
      this.backends.set(b.backends);
      this.defaultBackend.set(b.default);
    } catch {
      // ignore (auth interceptor handles 401)
    }
    try {
      const o = await this.llm.listOllamaModels();
      this.ollamaBaseUrl.set(o.base_url);
      if (!o.reachable) {
        this.ollamaError.set(o.error ?? 'unreachable');
        this.ollamaModels.set([]);
      } else {
        this.ollamaError.set(null);
        this.ollamaModels.set(o.models);
      }
    } catch {
      this.ollamaError.set('errore richiesta');
    }
  }

  saveApiUrl(): void {
    setApiBaseUrl(this.apiUrl);
    location.reload();
  }

  resetApiUrl(): void {
    setApiBaseUrl('');
    this.apiUrl = '';
    location.reload();
  }

  select(name: string | null): void {
    this.llm.setPreferredBackend(name);
  }
}
