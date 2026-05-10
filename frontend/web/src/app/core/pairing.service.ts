import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { PairingInitiateResponse } from './api.types';
import { apiUrl } from './config';

@Injectable({ providedIn: 'root' })
export class PairingService {
  private readonly http = inject(HttpClient);

  initiate(): Promise<PairingInitiateResponse> {
    return firstValueFrom(
      this.http.post<PairingInitiateResponse>(apiUrl('/api/v1/pairing/initiate'), {})
    );
  }
}
