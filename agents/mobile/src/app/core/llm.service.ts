import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { BackendsResponse, OllamaModelsResponse } from './api.types';
import { apiUrl } from './config';

@Injectable({ providedIn: 'root' })
export class LlmService {
  private readonly http = inject(HttpClient);

  listBackends(): Promise<BackendsResponse> {
    return firstValueFrom(this.http.get<BackendsResponse>(apiUrl('/api/v1/llm/backends')));
  }

  listOllamaModels(): Promise<OllamaModelsResponse> {
    return firstValueFrom(this.http.get<OllamaModelsResponse>(apiUrl('/api/v1/llm/ollama/models')));
  }
}
