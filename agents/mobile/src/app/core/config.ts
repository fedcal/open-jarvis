/**
 * On mobile the API URL is *always* a remote address (never same-origin),
 * because the app is served from the device. The Login page asks for it
 * the first time, then it's cached in Capacitor Preferences.
 */
import { Storage } from './storage';

const KEY = 'oj.api_base_url';

let cached: string | null = null;

export async function loadApiBaseUrl(): Promise<string> {
  if (cached !== null) return cached;
  const v = (await Storage.get(KEY)) ?? '';
  cached = v;
  return v;
}

export async function setApiBaseUrl(url: string): Promise<void> {
  cached = url;
  if (!url) {
    await Storage.remove(KEY);
    return;
  }
  await Storage.set(KEY, stripTrailingSlash(url));
}

export function getApiBaseUrlSync(): string {
  return cached ?? '';
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrlSync();
  return base + (path.startsWith('/') ? path : `/${path}`);
}

function stripTrailingSlash(s: string): string {
  return s.endsWith('/') ? s.slice(0, -1) : s;
}
