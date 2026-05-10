import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { NgClass } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../core/auth.service';
import { ThemeService } from '../core/theme.service';

interface NavItem {
  label: string;
  icon: string;
  path: string;
}

@Component({
  selector: 'oj-shell',
  standalone: true,
  imports: [NgClass, RouterLink, RouterLinkActive, RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="flex min-h-screen">
      <!-- Sidebar (hidden on small screens) -->
      <aside
        [ngClass]="{ 'translate-x-0': mobileOpen(), '-translate-x-full': !mobileOpen() }"
        class="fixed inset-y-0 left-0 z-30 w-64 transform border-r border-slate-200 bg-white p-4
               transition-transform dark:border-slate-800 dark:bg-slate-900
               md:static md:translate-x-0 md:flex md:flex-col"
      >
        <div class="mb-8 flex items-center gap-2">
          <div class="h-8 w-8 rounded-lg bg-jarvis-600 flex items-center justify-center text-white font-bold">J</div>
          <span class="text-lg font-semibold">Open-Jarvis</span>
        </div>

        <nav class="flex flex-col gap-1">
          @for (item of navItems; track item.path) {
            <a
              [routerLink]="item.path"
              routerLinkActive="bg-jarvis-50 text-jarvis-700 dark:bg-jarvis-950 dark:text-jarvis-200"
              [routerLinkActiveOptions]="{ exact: item.path === '/' }"
              (click)="mobileOpen.set(false)"
              class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium
                     text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <span class="text-lg">{{ item.icon }}</span>
              {{ item.label }}
            </a>
          }
        </nav>

        <div class="mt-auto pt-4 border-t border-slate-200 dark:border-slate-800">
          <div class="mb-3 text-xs text-slate-500">
            <div class="font-medium text-slate-700 dark:text-slate-200">{{ user()?.display_name }}</div>
            <div class="truncate">{{ user()?.email }}</div>
          </div>
          <button class="oj-btn-ghost w-full justify-start" type="button" (click)="cycleTheme()">
            <span>{{ themeIcon() }}</span> Tema: {{ themeLabel() }}
          </button>
          <button class="oj-btn-ghost w-full justify-start text-red-600 dark:text-red-400" type="button" (click)="logout()">
            <span>↩</span> Esci
          </button>
        </div>
      </aside>

      <!-- Main column -->
      <div class="flex flex-1 flex-col">
        <header class="flex items-center gap-2 border-b border-slate-200 bg-white px-4 py-3
                       dark:border-slate-800 dark:bg-slate-900 md:hidden">
          <button class="oj-btn-ghost" (click)="mobileOpen.set(!mobileOpen())" aria-label="Apri menu">☰</button>
          <span class="text-lg font-semibold">Open-Jarvis</span>
        </header>
        <main class="flex-1 p-4 md:p-8">
          <router-outlet />
        </main>
      </div>
    </div>
  `
})
export class ShellComponent {
  private readonly auth = inject(AuthService);
  private readonly themeSvc = inject(ThemeService);

  readonly user = this.auth.user;
  readonly mobileOpen = signal(false);

  readonly navItems: NavItem[] = [
    { label: 'Chat', icon: '💬', path: '/' },
    { label: 'Memoria', icon: '🧠', path: '/memory' },
    { label: 'Dispositivi', icon: '📱', path: '/devices' },
    { label: 'Impostazioni', icon: '⚙️', path: '/settings' }
  ];

  readonly themeIcon = computed(() => {
    switch (this.themeSvc.theme()) {
      case 'dark': return '🌙';
      case 'light': return '☀️';
      default: return '🖥';
    }
  });

  readonly themeLabel = computed(() => {
    switch (this.themeSvc.theme()) {
      case 'dark': return 'scuro';
      case 'light': return 'chiaro';
      default: return 'sistema';
    }
  });

  cycleTheme(): void {
    const order = ['system', 'light', 'dark'] as const;
    const next = order[(order.indexOf(this.themeSvc.theme()) + 1) % order.length];
    this.themeSvc.set(next);
  }

  logout(): void {
    this.auth.logout();
  }
}
