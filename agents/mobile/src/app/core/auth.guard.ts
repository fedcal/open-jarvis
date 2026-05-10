import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isAuthenticated()) return true;
  await auth.hydrate();
  if (auth.isAuthenticated()) return true;
  router.navigateByUrl('/login');
  return false;
};

export const guestGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (!auth.isAuthenticated()) {
    await auth.hydrate();
  }
  if (!auth.isAuthenticated()) return true;
  router.navigateByUrl('/');
  return false;
};
