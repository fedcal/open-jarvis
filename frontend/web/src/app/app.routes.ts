import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () =>
      import('./features/auth/login.page').then((m) => m.LoginPage)
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell.component').then((m) => m.ShellComponent),
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('./features/chat/chat.page').then((m) => m.ChatPage)
      },
      {
        path: 'memory',
        loadComponent: () =>
          import('./features/memory/memory.page').then((m) => m.MemoryPage)
      },
      {
        path: 'devices',
        loadComponent: () =>
          import('./features/devices/devices.page').then((m) => m.DevicesPage)
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./features/settings/settings.page').then((m) => m.SettingsPage)
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
