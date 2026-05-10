import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  TokenPair,
  UserPublic
} from './api.types';
import { apiUrl } from './config';

const ACCESS_KEY = 'oj.access';
const REFRESH_KEY = 'oj.refresh';
const USER_KEY = 'oj.user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  readonly user = signal<UserPublic | null>(this.readUser());
  readonly accessToken = signal<string | null>(localStorage.getItem(ACCESS_KEY));
  readonly isAuthenticated = computed(() => this.accessToken() !== null);

  async register(payload: RegisterRequest): Promise<UserPublic> {
    return firstValueFrom(
      this.http.post<UserPublic>(apiUrl('/api/v1/auth/register'), payload)
    );
  }

  async login(payload: LoginRequest): Promise<LoginResponse> {
    const response = await firstValueFrom(
      this.http.post<LoginResponse>(apiUrl('/api/v1/auth/login'), payload)
    );
    if ('access_token' in response) {
      this.persistTokens(response);
    }
    return response;
  }

  async refresh(): Promise<boolean> {
    const refresh = localStorage.getItem(REFRESH_KEY);
    if (!refresh) return false;
    try {
      const response = await firstValueFrom(
        this.http.post<TokenPair>(apiUrl('/api/v1/auth/refresh'), {
          refresh_token: refresh
        })
      );
      this.persistTokens(response);
      return true;
    } catch {
      this.logout();
      return false;
    }
  }

  async logout(redirect = true): Promise<void> {
    if (this.accessToken()) {
      try {
        await firstValueFrom(this.http.post(apiUrl('/api/v1/auth/logout'), {}));
      } catch {
        // best-effort
      }
    }
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    this.accessToken.set(null);
    this.user.set(null);
    if (redirect) {
      this.router.navigateByUrl('/login');
    }
  }

  private persistTokens(pair: TokenPair): void {
    localStorage.setItem(ACCESS_KEY, pair.access_token);
    localStorage.setItem(REFRESH_KEY, pair.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(pair.user));
    this.accessToken.set(pair.access_token);
    this.user.set(pair.user);
  }

  private readUser(): UserPublic | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as UserPublic;
    } catch {
      return null;
    }
  }
}
