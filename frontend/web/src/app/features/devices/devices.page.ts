import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';

import { PairingService } from '../../core/pairing.service';
import { PairingInitiateResponse } from '../../core/api.types';

@Component({
  selector: 'oj-devices',
  standalone: true,
  imports: [],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="mx-auto max-w-2xl">
      <h1 class="mb-4 text-2xl font-semibold">Dispositivi</h1>

      <div class="oj-card p-6">
        <h2 class="mb-2 text-lg font-semibold">Aggiungi un nuovo dispositivo</h2>
        <p class="mb-4 text-sm text-slate-500">
          Genera un codice di pairing valido 5 minuti. Sul nuovo dispositivo, apri
          l'app Open-Jarvis, premi "Pair this device" e scansiona il QR (o inserisci
          il codice di 6 cifre).
        </p>

        <button class="oj-btn-primary" type="button" (click)="generate()" [disabled]="busy()">
          {{ busy() ? 'Generazione…' : 'Genera codice di pairing' }}
        </button>

        @if (current(); as c) {
          <div class="mt-6 grid gap-6 md:grid-cols-2">
            <div class="flex flex-col items-center">
              <div class="rounded-lg bg-white p-4 ring-1 ring-slate-200 dark:ring-slate-700"
                   [innerHTML]="qrSvg()"></div>
              <p class="mt-2 text-xs text-slate-500">jarvispair://v1?…</p>
            </div>
            <div>
              <p class="mb-2 text-sm text-slate-500">Codice numerico</p>
              <p class="font-mono text-3xl tracking-widest">
                {{ c.code.slice(0,3) }} {{ c.code.slice(3) }}
              </p>
              <p class="mt-4 text-xs text-slate-500">Scade fra:</p>
              <p class="font-mono text-lg">{{ secondsLeft() }}s</p>
              <button class="oj-btn-ghost mt-4 w-full" (click)="copyToken(c)">Copia URI</button>
            </div>
          </div>
        }

        @if (error()) {
          <p class="mt-4 text-sm text-red-600 dark:text-red-400">{{ error() }}</p>
        }
      </div>
    </div>
  `
})
export class DevicesPage {
  private readonly pairing = inject(PairingService);

  busy = signal(false);
  current = signal<PairingInitiateResponse | null>(null);
  qrSvg = signal<string>('');
  secondsLeft = signal<number>(0);
  error = signal<string | null>(null);

  private timer: ReturnType<typeof setInterval> | null = null;

  async generate(): Promise<void> {
    this.error.set(null);
    this.busy.set(true);
    try {
      const r = await this.pairing.initiate();
      this.current.set(r);
      this.qrSvg.set(this.renderQr(r.qr_payload));
      this.secondsLeft.set(r.expires_in);
      this.startCountdown();
    } catch (err: unknown) {
      this.error.set(err instanceof Error ? err.message : 'Errore.');
    } finally {
      this.busy.set(false);
    }
  }

  copyToken(c: PairingInitiateResponse): void {
    if (navigator.clipboard) navigator.clipboard.writeText(c.qr_payload);
  }

  private startCountdown(): void {
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(() => {
      const next = this.secondsLeft() - 1;
      if (next <= 0) {
        if (this.timer) clearInterval(this.timer);
        this.secondsLeft.set(0);
        this.current.set(null);
      } else {
        this.secondsLeft.set(next);
      }
    }, 1000);
  }

  /**
   * Lightweight QR fallback: renders a placeholder image with the
   * payload encoded via the public goQR.me service. Fully-offline
   * QR generation will switch to the `qrcode` npm package once we
   * pin a build budget for it.
   */
  private renderQr(payload: string): string {
    const url = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(payload)}`;
    return `<img src="${url}" alt="QR pairing" width="200" height="200" />`;
  }
}
