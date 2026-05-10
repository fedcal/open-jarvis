import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { getApiBaseUrl, setApiBaseUrl } from '../../core/config';

type Mode = 'login' | 'register';

@Component({
  selector: 'oj-login',
  standalone: true,
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="min-h-screen flex items-center justify-center p-4">
      <div class="oj-card w-full max-w-md p-8">
        <div class="mb-6 flex items-center gap-3">
          <div class="h-10 w-10 rounded-lg bg-jarvis-600 flex items-center justify-center text-white font-bold text-xl">J</div>
          <div>
            <h1 class="text-xl font-semibold">Open-Jarvis</h1>
            <p class="text-xs text-slate-500">Il tuo assistente AI personale</p>
          </div>
        </div>

        <div class="mb-4 flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
          <button
            type="button"
            class="flex-1 rounded-md px-3 py-1.5 text-sm font-medium"
            [class.bg-white]="mode() === 'login'"
            [class.dark:bg-slate-900]="mode() === 'login'"
            [class.shadow-sm]="mode() === 'login'"
            (click)="mode.set('login')"
          >Accedi</button>
          <button
            type="button"
            class="flex-1 rounded-md px-3 py-1.5 text-sm font-medium"
            [class.bg-white]="mode() === 'register'"
            [class.dark:bg-slate-900]="mode() === 'register'"
            [class.shadow-sm]="mode() === 'register'"
            (click)="mode.set('register')"
          >Registrati</button>
        </div>

        <form (submit)="$event.preventDefault(); submit()" class="space-y-4">
          <div>
            <label class="oj-label" for="api">Server URL</label>
            <input
              id="api"
              class="oj-input font-mono text-xs"
              [(ngModel)]="apiBaseUrl"
              name="apiBaseUrl"
              placeholder="http://localhost:8090"
              autocomplete="off"
            />
            <p class="mt-1 text-xs text-slate-500">
              Lascia vuoto per usare lo stesso host della pagina.
            </p>
          </div>

          @if (mode() === 'register') {
            <div>
              <label class="oj-label" for="name">Nome</label>
              <input id="name" class="oj-input" [(ngModel)]="displayName" name="displayName" required minlength="2" />
            </div>
          }

          <div>
            <label class="oj-label" for="email">Email</label>
            <input id="email" type="email" class="oj-input" [(ngModel)]="email" name="email" required />
          </div>

          <div>
            <label class="oj-label" for="password">Password</label>
            <input
              id="password"
              type="password"
              class="oj-input"
              [(ngModel)]="password"
              name="password"
              required
              minlength="12"
            />
            @if (mode() === 'register') {
              <p class="mt-1 text-xs text-slate-500">Minimo 12 caratteri.</p>
            }
          </div>

          @if (errorMessage()) {
            <p class="rounded-md bg-red-50 p-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
              {{ errorMessage() }}
            </p>
          }

          <button type="submit" class="oj-btn-primary w-full" [disabled]="loading()">
            {{ loading() ? 'Attendere…' : (mode() === 'login' ? 'Accedi' : 'Registrati e accedi') }}
          </button>
        </form>
      </div>
    </div>
  `
})
export class LoginPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  mode = signal<Mode>('login');
  apiBaseUrl = getApiBaseUrl();
  email = '';
  password = '';
  displayName = '';
  loading = signal(false);
  errorMessage = signal<string | null>(null);

  async submit(): Promise<void> {
    this.errorMessage.set(null);
    this.loading.set(true);
    setApiBaseUrl(this.apiBaseUrl);
    try {
      if (this.mode() === 'register') {
        await this.auth.register({
          email: this.email,
          password: this.password,
          display_name: this.displayName
        });
      }
      const result = await this.auth.login({ email: this.email, password: this.password });
      if ('mfa_required' in result) {
        this.errorMessage.set('MFA richiesto: il flow MFA arriverà nella prossima release UI.');
        return;
      }
      this.router.navigateByUrl('/');
    } catch (err: unknown) {
      this.errorMessage.set(this.parseError(err));
    } finally {
      this.loading.set(false);
    }
  }

  private parseError(err: unknown): string {
    if (err && typeof err === 'object' && 'error' in err) {
      const body = (err as { error?: { detail?: unknown } }).error;
      if (body && typeof body === 'object' && 'detail' in body) {
        const d = (body as { detail: unknown }).detail;
        if (typeof d === 'string') return d;
        if (Array.isArray(d) && d.length > 0 && typeof d[0] === 'object') {
          return d.map((e: { msg?: string }) => e.msg ?? '').filter(Boolean).join(' · ');
        }
      }
      if ('status' in err) return `HTTP ${(err as { status: number }).status}`;
    }
    return 'Errore inatteso. Verifica server URL e credenziali.';
  }
}
