/**
 * Runtime config. The web app may run on:
 *  - localhost:4200 (ng serve, pointing at the API on :8080 or :8090)
 *  - same-origin behind a reverse proxy (Caddy/Nginx) — empty base URL
 *  - inside Tauri / Capacitor — the API URL is injected at build time
 *
 * Order of precedence:
 *  1. window.__OJ_API_BASE_URL__ (set by Tauri / Capacitor / index.html)
 *  2. localStorage('oj.api_base_url') — set in the Login page
 *  3. import.meta env (NG_APP_API_URL replacement done at build time)
 *  4. same-origin (empty string, browser uses current page origin)
 */
declare global {
  interface Window {
    __OJ_API_BASE_URL__?: string;
  }
}

const STORAGE_KEY = 'oj.api_base_url';

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    if (window.__OJ_API_BASE_URL__) return stripTrailingSlash(window.__OJ_API_BASE_URL__);
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stripTrailingSlash(stored);
  }
  return '';
}

export function setApiBaseUrl(url: string): void {
  if (typeof window === 'undefined') return;
  if (!url) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  localStorage.setItem(STORAGE_KEY, stripTrailingSlash(url));
}

function stripTrailingSlash(s: string): string {
  return s.endsWith('/') ? s.slice(0, -1) : s;
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  return base + (path.startsWith('/') ? path : `/${path}`);
}
