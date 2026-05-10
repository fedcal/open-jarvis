import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { MemoryItemPublic, MemorySearchResponse } from './api.types';
import { apiUrl } from './config';

@Injectable({ providedIn: 'root' })
export class MemoryService {
  private readonly http = inject(HttpClient);

  list(limit = 50): Promise<MemoryItemPublic[]> {
    return firstValueFrom(
      this.http.get<MemoryItemPublic[]>(apiUrl(`/api/v1/memory/list?limit=${limit}`))
    );
  }

  record(content: string, kind = 'note'): Promise<MemoryItemPublic> {
    return firstValueFrom(
      this.http.post<MemoryItemPublic>(apiUrl('/api/v1/memory/record'), { content, kind })
    );
  }

  search(query: string, top_k = 5): Promise<MemorySearchResponse> {
    return firstValueFrom(
      this.http.post<MemorySearchResponse>(apiUrl('/api/v1/memory/search'), { query, top_k })
    );
  }

  forget(id: string): Promise<void> {
    return firstValueFrom(this.http.delete<void>(apiUrl(`/api/v1/memory/${id}`)));
  }
}
