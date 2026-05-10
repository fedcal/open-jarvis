import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { LoginResponse, TokenPair, UserPublic } from './api.types';
import { apiUrl, loadApiBaseUrl } from './config';
import { Storage } from './storage';

const ACCESS = 'oj.access';
const REFRESH = 'oj.refresh';
const USER = 'oj.user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  readonly accessToken = signal<string | null>(null);
  readonly user = signal<UserPublic | null>(null);
  readonly isAuthenticated = computed(() => this.accessToken() !== null);

  /** Run once at startup before the router activates the guards. */
  async hydrate(): Promise<void> {
    await loadApiBaseUrl();
    const t = await Storage.get(ACCESS);
    const u = await Storage.get(USER);
    this.accessToken.set(t);
    this.user.set(u ? (JSON.parse(u) as UserPublic) : null);
  }

  async register(email: string, password: string, displayName: string): Promise<UserPublic> {
    return firstValueFrom(
      this.http.post<UserPublic>(apiUrl('/api/v1/auth/register'), {
        email, password, display_name: displayName
      })
    );
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const res = await firstValueFrom(
      this.http.post<LoginResponse>(apiUrl('/api/v1/auth/login'), {
        email, password,
        device_name: 'iPhone',
        device_platform: 'mobile_ios'
      })
    );
    if ('access_token' in res) await this.persist(res);
    return res;
  }

  async refresh(): Promise<boolean> {
    const r = await Storage.get(REFRESH);
    if (!r) return false;
    try {
      const res = await firstValueFrom(
        this.http.post<TokenPair>(apiUrl('/api/v1/auth/refresh'), { refresh_token: r })
      );
      await this.persist(res);
      return true;
    } catch {
      await this.logout(false);
      return false;
    }
  }

  async logout(redirect = true): Promise<void> {
    if (this.accessToken()) {
      try { await firstValueFrom(this.http.post(apiUrl('/api/v1/auth/logout'), {})); }
      catch { /* best-effort */ }
    }
    await Storage.remove(ACCESS);
    await Storage.remove(REFRESH);
    await Storage.remove(USER);
    this.accessToken.set(null);
    this.user.set(null);
    if (redirect) this.router.navigateByUrl('/login');
  }

  private async persist(pair: TokenPair): Promise<void> {
    await Storage.set(ACCESS, pair.access_token);
    await Storage.set(REFRESH, pair.refresh_token);
    await Storage.set(USER, JSON.stringify(pair.user));
    this.accessToken.set(pair.access_token);
    this.user.set(pair.user);
  }
}
