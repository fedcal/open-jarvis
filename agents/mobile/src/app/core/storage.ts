/**
 * Thin wrapper over Capacitor Preferences that falls back to
 * `localStorage` when running on the web (eg. ng serve).
 */
import { Preferences } from '@capacitor/preferences';

export class Storage {
  static async get(key: string): Promise<string | null> {
    try {
      const { value } = await Preferences.get({ key });
      return value ?? null;
    } catch {
      return localStorage.getItem(key);
    }
  }

  static async set(key: string, value: string): Promise<void> {
    try {
      await Preferences.set({ key, value });
    } catch {
      localStorage.setItem(key, value);
    }
  }

  static async remove(key: string): Promise<void> {
    try {
      await Preferences.remove({ key });
    } catch {
      localStorage.removeItem(key);
    }
  }
}
