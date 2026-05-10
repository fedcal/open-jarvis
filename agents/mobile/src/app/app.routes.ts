import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/login.page').then((m) => m.LoginPage)
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/tabs.page').then((m) => m.TabsPage),
    children: [
      {
        path: 'chat',
        loadComponent: () => import('./pages/chat.page').then((m) => m.ChatPage)
      },
      {
        path: 'memory',
        loadComponent: () => import('./pages/memory.page').then((m) => m.MemoryPage)
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./pages/settings.page').then((m) => m.SettingsPage)
      },
      { path: '', redirectTo: 'chat', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: '' }
];
