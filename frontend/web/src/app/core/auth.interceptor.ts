import { HttpInterceptorFn, HttpErrorResponse, HttpRequest, HttpHandlerFn, HttpEvent } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, from, Observable, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.accessToken();
  const authed = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authed).pipe(
    catchError((err: HttpErrorResponse) => {
      const isAuthEndpoint = req.url.includes('/api/v1/auth/');
      if (err.status === 401 && token && !isAuthEndpoint) {
        return refreshAndRetry(auth, req, next);
      }
      return throwError(() => err);
    })
  );
};

function refreshAndRetry(
  auth: AuthService,
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  return from(auth.refresh()).pipe(
    switchMap((ok) => {
      if (!ok) {
        return throwError(() => new Error('refresh-failed'));
      }
      const fresh = auth.accessToken();
      const retried = fresh
        ? req.clone({ setHeaders: { Authorization: `Bearer ${fresh}` } })
        : req;
      return next(retried);
    })
  );
}
