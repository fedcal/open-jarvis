import { Injectable, signal } from '@angular/core';

type Theme = 'light' | 'dark' | 'system';
const KEY = 'oj.theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<Theme>((localStorage.getItem(KEY) as Theme | null) ?? 'system');

  init(): void {
    this.apply(this.theme());
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.theme() === 'system') this.apply('system');
      });
    }
  }

  set(t: Theme): void {
    this.theme.set(t);
    localStorage.setItem(KEY, t);
    this.apply(t);
  }

  private apply(t: Theme): void {
    const root = document.documentElement;
    const dark =
      t === 'dark' ||
      (t === 'system' && window.matchMedia?.('(prefers-color-scheme: dark)').matches);
    root.classList.toggle('dark', dark);
  }
}
