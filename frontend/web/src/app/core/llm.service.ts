import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { BackendsResponse, OllamaModelsResponse } from './api.types';
import { apiUrl } from './config';

const PREF_BACKEND_KEY = 'oj.preferred_backend';

@Injectable({ providedIn: 'root' })
export class LlmService {
  private readonly http = inject(HttpClient);

  readonly preferredBackend = signal<string | null>(localStorage.getItem(PREF_BACKEND_KEY));

  async listBackends(): Promise<BackendsResponse> {
    return firstValueFrom(this.http.get<BackendsResponse>(apiUrl('/api/v1/llm/backends')));
  }

  async listOllamaModels(): Promise<OllamaModelsResponse> {
    return firstValueFrom(
      this.http.get<OllamaModelsResponse>(apiUrl('/api/v1/llm/ollama/models'))
    );
  }

  setPreferredBackend(name: string | null): void {
    if (name) localStorage.setItem(PREF_BACKEND_KEY, name);
    else localStorage.removeItem(PREF_BACKEND_KEY);
    this.preferredBackend.set(name);
  }
}
