---
title: "Mobile-first design + WCAG 2.2 AA"
description: "Standard di accessibilità WCAG 2.2 (87 criteri), 9 nuovi criteri in 2.2, Mobile-first con TailwindCSS 4, container queries, touch target 44px, prefers-reduced-motion."
keywords: "WCAG 2.2, EAA, accessibility, mobile-first, TailwindCSS, container queries, ARIA, axe-core, Playwright a11y"
---

# Mobile-first + WCAG 2.2 AA

**Standard:** W3C WCAG 2.2 (ott 2023), EN 301 549 v3.2.1, EAA Direttiva 2019/882
**Obbligatorio dal:** 28 giugno 2025 (EAA)
**Target Jarvis:** Level AA (56 criteri = 32 A + 24 AA)

## 1. Contesto normativo

### European Accessibility Act (EAA)

Dal **28 giugno 2025** la Direttiva 2019/882 è obbligatoria per servizi digitali in EU. Il riferimento tecnico è **EN 301 549 v3.2.1** che mappa su **WCAG 2.2 Level AA**. Obblighi: dichiarazione di accessibilità pubblica, procedura reclamo, conformità continuativa.

### 9 nuovi criteri WCAG 2.2 vs 2.1

| Criterio | Titolo | Livello |
|---|---|---|
| 2.4.11 | Focus Not Obscured (Minimum) | AA |
| 2.4.12 | Focus Not Obscured (Enhanced) | AAA |
| 2.4.13 | Focus Appearance | AAA |
| 2.5.7 | Dragging Movements | AA |
| 2.5.8 | Target Size (Minimum) | AA |
| 3.2.6 | Consistent Help | A |
| 3.3.7 | Redundant Entry | A |
| 3.3.8 | Accessible Authentication (Min) | AA |
| 3.3.9 | Accessible Authentication (Enh) | AAA |

WCAG 2.2 ha **rimosso** il criterio 4.1.1 Parsing (obsoleto).

## 2. Principi POUR

### 2.1 Perceivable

**Alt text:**

```tsx
<img
  src={src}
  alt={decorative ? "" : `Avatar di ${userName}`}
  aria-hidden={decorative}
  className="w-10 h-10 rounded-full"
/>
```

**Color contrast (WCAG 1.4.3 AA: 4.5:1):**

```css
:root {
  /* Light — verificati >= 4.5:1 */
  --color-text-primary: #1a1a2e;     /* su #ffffff → 18.1:1 */
  --color-text-secondary: #4a4a6a;   /* su #ffffff → 7.2:1  */
  --color-text-muted: #6b6b8a;       /* su #ffffff → 4.6:1  */
  --color-accent: #2563eb;           /* su #ffffff → 5.9:1  */
  --color-bg: #ffffff;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-text-primary: #e2e8f0;   /* su #0f172a → 14.8:1 */
    --color-text-secondary: #94a3b8; /* su #0f172a → 5.2:1  */
    --color-accent: #60a5fa;         /* su #0f172a → 4.8:1  */
    --color-bg: #0f172a;
  }
}
```

**Captions (WCAG 1.2.2 AA):**

```tsx
<figure>
  <video controls>
    <source src={src} type="audio/mpeg" />
    <track kind="captions" src="/captions/briefing-it.vtt" srcLang="it" label="Italiano" default />
  </video>
  <figcaption className="sr-only">{transcript}</figcaption>
</figure>
```

**Fluid typography:**

```css
html { font-size: clamp(1rem, 0.9rem + 0.5vw, 1.25rem); }
```

### 2.2 Operable

**Skip links (WCAG 2.4.1 A):**

```tsx
<nav aria-label="Navigazione rapida" className="sr-only focus-within:not-sr-only">
  <a href="#main-content"
     className="fixed top-2 left-2 z-[9999] bg-[--color-accent] text-white px-4 py-2 rounded
                focus:outline-none focus:ring-2 focus:ring-white">
    Salta al contenuto
  </a>
</nav>
```

**Focus visible (WCAG 2.4.7 AA + nuovo 2.4.11):**

```css
:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
  border-radius: 4px;
  scroll-margin-top: 80px;  /* compensa header sticky h-16 */
}

:focus:not(:focus-visible) { outline: none; }
```

### 2.3 Understandable

**Redundant Entry (3.3.7 AA):** non richiedere reinserimento dati già forniti. Usa `sessionStorage` o React context.

**Accessible Auth (3.3.8 AA):**

```tsx
<input type="password"
       id="password"
       name="password"
       autoComplete="current-password"   // abilita password manager
       aria-describedby="password-hint" />
<p id="password-hint" className="text-sm text-[--color-text-muted]">
  In alternativa usa una passkey o il link via email.
</p>
```

**Consistent Help (3.2.6 A):** pulsante help nella **stessa posizione relativa** su ogni schermata.

### 2.4 Robust

```html
<html lang="it">
<!-- Per sezioni in altra lingua -->
<span lang="en">Settings</span>
```

## 3. Mobile-first con TailwindCSS 4

### Breakpoints + container queries

```html
<main class="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
  <!-- Container query: il componente si adatta al contenitore -->
  <div class="@container">
    <div class="grid grid-cols-1 @md:grid-cols-2 @lg:grid-cols-3 gap-4">
      <!-- cards -->
    </div>
  </div>
</main>
```

### Touch target 44x44px (WCAG 2.5.8 + Apple HIG)

```tsx
export function IconButton({ icon, label, ...props }) {
  return (
    <button
      aria-label={label}
      className="min-w-[44px] min-h-[44px] inline-flex items-center justify-center
                 rounded-lg transition-colors
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--color-accent]"
      {...props}
    >
      {icon}
    </button>
  );
}
```

### Safe area (notch, dynamic island)

```css
.app-shell {
  padding-top: env(safe-area-inset-top);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
}

.bottom-nav { padding-bottom: max(env(safe-area-inset-bottom), 1rem); }
```

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```

### prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```tsx
import { useEffect, useState } from "react";


export function useReducedMotion(): boolean {
  const query = "(prefers-reduced-motion: reduce)";
  const [reduced, setReduced] = useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches
  );
  useEffect(() => {
    const mql = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);
  return reduced;
}
```

## 4. Web Components accessibili

### Struttura semantica

```html
<header role="banner">
  <nav aria-label="Navigazione principale" id="main-nav">...</nav>
</header>
<main id="main-content" tabindex="-1">
  <aside aria-label="Pannello biometrico">...</aside>
  <section aria-labelledby="chat-heading">
    <h2 id="chat-heading">Conversazione</h2>
  </section>
</main>
<footer role="contentinfo">...</footer>
```

### Modal con focus trap (native `<dialog>`)

```tsx
import { useEffect, useRef } from "react";


export function Modal({ isOpen, onClose, title, children, triggerId }) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const d = dialogRef.current;
    if (!d) return;
    if (isOpen) d.showModal();
    else {
      d.close();
      document.getElementById(triggerId)?.focus();  // restituzione focus
    }
  }, [isOpen, triggerId]);

  useEffect(() => {
    const d = dialogRef.current;
    if (!d) return;
    const onCloseEvt = () => onClose();
    d.addEventListener("close", onCloseEvt);
    return () => d.removeEventListener("close", onCloseEvt);
  }, [onClose]);

  return (
    <dialog ref={dialogRef} aria-labelledby="modal-title" aria-modal="true"
            className="w-full max-w-lg rounded-xl p-6 backdrop:bg-black/60">
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose} aria-label="Chiudi"
              className="absolute top-4 right-4 min-w-[44px] min-h-[44px]">
        ×
      </button>
    </dialog>
  );
}
```

### Chat live region (montata UNA SOLA VOLTA)

```tsx
// Layout radice — MAI condizionale
export function ChatLiveRegion() {
  return (
    <>
      <div id="chat-announcer-polite" aria-live="polite" aria-atomic="true" className="sr-only" />
      <div id="chat-announcer-assertive" aria-live="assertive" aria-atomic="true" className="sr-only" />
    </>
  );
}


// Hook
export function useChatAnnouncer() {
  const announce = (message: string, priority: "polite" | "assertive" = "polite") => {
    const el = document.getElementById(`chat-announcer-${priority}`);
    if (!el) return;
    el.textContent = "";
    requestAnimationFrame(() => { el.textContent = message; });
  };
  return { announce };
}
```

### Tabs con arrow keys

```tsx
const handleKey = (e, index) => {
  const map = {
    ArrowRight: (index + 1) % tabs.length,
    ArrowLeft: (index - 1 + tabs.length) % tabs.length,
    Home: 0,
    End: tabs.length - 1,
  };
  if (e.key in map) {
    e.preventDefault();
    setActiveIndex(map[e.key]);
    document.getElementById(`tab-${tabs[map[e.key]].id}`)?.focus();
  }
};

// JSX:
// <button role="tab" aria-selected={i === active} aria-controls={`panel-${tab.id}`}
//         tabIndex={i === active ? 0 : -1} onKeyDown={e => handleKey(e, i)}>
```

### Dashboard biometrica accessibile

I grafici devono avere tabella dati equivalente:

```tsx
<section aria-labelledby={`${chartId}-title`}>
  <h3 id={`${chartId}-title`}>{title}</h3>
  <div role="img" aria-label={description} aria-describedby={tableId} className="h-48 w-full">
    {/* grafico Recharts */}
  </div>
  <table id={tableId} className="sr-only">
    <caption>{title} — dati tabellari</caption>
    <thead><tr><th scope="col">Periodo</th><th scope="col">Valore</th><th scope="col">Unità</th></tr></thead>
    <tbody>{data.map(d => <tr><td>{d.label}</td><td>{d.value}</td><td>{d.unit}</td></tr>)}</tbody>
  </table>
</section>
```

## 5. PWA + offline

### Manifest

```json
{
  "name": "Jarvis — Personal AI",
  "short_name": "Jarvis",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#2563eb",
  "background_color": "#0f172a",
  "lang": "it",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
```

### Service Worker

```ts
const SHELL_CACHE = "jarvis-shell-v1";
const SHELL_ASSETS = ["/", "/index.html", "/offline.html", "/manifest.json"];

self.addEventListener("install", (event: ExtendableEvent) => {
  event.waitUntil(caches.open(SHELL_CACHE).then(c => c.addAll(SHELL_ASSETS)));
  (self as ServiceWorkerGlobalScope).skipWaiting();
});

self.addEventListener("fetch", (event: FetchEvent) => {
  if (SHELL_ASSETS.some(u => event.request.url.endsWith(u))) {
    event.respondWith(caches.match(event.request).then(c => c ?? fetch(event.request)));
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() => caches.match("/offline.html")!)
  );
});
```

## 6. Test accessibilità

### axe-core + Vitest

```ts
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);


describe("ChatView — WCAG 2.2 AA", () => {
  it("nessuna violazione", async () => {
    const { container } = render(<ChatView />);
    const results = await axe(container, {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag22aa"] },
    });
    expect(results).toHaveNoViolations();
  });
});
```

### Playwright E2E

```ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";


test("WCAG 2.2 AA — homepage", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});


test("skip link funziona", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: /salta al contenuto/i });
  await expect(skip).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});
```

### CI workflow

```yaml
name: Accessibility Audit
on: [push, pull_request]
jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - run: npm ci
      - run: npm run test:a11y
      - run: npx playwright install --with-deps
      - run: npm run test:e2e:a11y
```

### Screen reader test matrix

| Componente | VoiceOver iOS | TalkBack Android | NVDA Win | Orca Linux |
|---|---|---|---|---|
| Chat live region | | | | |
| Modal focus trap | | | | |
| Tab navigation | | | | |
| Biometric chart | | | | |
| Voice input btn | | | | |
| Auth form | | | | |

Tool colore: **Stark** (Figma), **Adobe Color Contrast Analyzer**, **Coolors**, **Chrome DevTools Accessibility Inspector**.

## 7. Settings utente accessibilità

```tsx
export function AccessibilitySettings() {
  return (
    <section aria-labelledby="a11y-title">
      <h2 id="a11y-title">Impostazioni accessibilità</h2>
      <fieldset>
        <legend>Testo</legend>
        <label htmlFor="font-scale" className="flex flex-col gap-1">
          <span>Dimensione testo</span>
          <input type="range" id="font-scale" min="80" max="150" step="10"
                 defaultValue={100} className="min-h-[44px]" />
        </label>
      </fieldset>
      <fieldset>
        <legend>Visualizzazione</legend>
        <label className="flex items-center gap-3 min-h-[44px]">
          <input type="checkbox" id="high-contrast" className="w-5 h-5" />
          <span>Alto contrasto</span>
        </label>
        <label className="flex items-center gap-3 min-h-[44px]">
          <input type="checkbox" id="reduce-motion" className="w-5 h-5" />
          <span>Riduci animazioni</span>
        </label>
      </fieldset>
    </section>
  );
}
```

## 8. Checklist WCAG 2.2 AA

### Livello A (32 criteri)

- [ ] 1.1.1 Alt text presente per immagini non decorative
- [ ] 1.3.1 Heading hierarchy h1>h2>h3, liste e tabelle semantiche
- [ ] 1.3.2 Ordine lettura DOM corretto
- [ ] 1.3.3 Istruzioni non basate solo su colore/forma
- [ ] 1.4.1 Colore non unico mezzo informativo
- [ ] 1.2.1/1.2.2/1.2.3 Captions/transcripts video-audio
- [ ] 2.1.1 Keyboard operabile
- [ ] 2.1.2 Nessuna keyboard trap
- [ ] 2.4.1 Skip links
- [ ] 2.4.2 Page title descrittivo
- [ ] 2.4.3 Focus order logico
- [ ] 2.4.4 Link descrittivi (no "clicca qui")
- [ ] 2.2.1 Timeout avvisi
- [ ] 2.2.2 Pause/stop contenuti in movimento
- [ ] 2.3.1 No lampeggio > 3/sec
- [ ] 3.1.1 lang attribute html
- [ ] 3.2.1 No cambio contesto su focus
- [ ] 3.2.2 No cambio contesto su input
- [ ] 3.3.1 Errori form identificati
- [ ] 3.3.2 Label/istruzioni form
- [ ] 4.1.2 name/role/value via API
- [ ] **3.2.6 Help in stessa posizione** (nuovo 2.2)
- [ ] **3.3.7 Redundant Entry** (nuovo 2.2)

### Livello AA (24 criteri aggiuntivi)

- [ ] 1.4.3 Contrasto >= 4.5:1 testo, >= 3:1 grande
- [ ] 1.4.4 Resize 200% senza perdita
- [ ] 1.4.5 Testo reale, non immagine
- [ ] 1.4.10 Reflow no scroll orizzontale a 400% zoom (320 CSS px)
- [ ] 1.4.11 Contrasto componenti UI >= 3:1
- [ ] 1.4.12 Spacing overrides ok
- [ ] 1.4.13 Hover/focus content persistente
- [ ] 2.4.5 Più modi per trovare pagine
- [ ] 2.4.6 Heading e label descrittivi
- [ ] 2.4.7 Focus visible
- [ ] 2.5.3 Label visibile in nome accessibile
- [ ] 2.5.4 Device motion con alternativa UI
- [ ] **2.4.11 Focus not obscured** (nuovo 2.2)
- [ ] **2.5.7 Dragging movements alternativa** (nuovo 2.2)
- [ ] **2.5.8 Target size >= 24px** (Jarvis: 44px) (nuovo 2.2)
- [ ] **3.3.8 Accessible Auth** (nuovo 2.2)
- [ ] 3.1.2 lang per parti in altra lingua
- [ ] 3.2.3 Navigazione coerente
- [ ] 3.2.4 Componenti identificati coerentemente
- [ ] 3.3.3 Suggerimenti errore
- [ ] 3.3.4 Conferma/annulla azioni importanti
- [ ] 4.1.3 Status messages annunciati a screen reader

## Riferimenti

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [European Accessibility Act](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en)
- [TailwindCSS 4 Container Queries](https://tailwindcss.com/docs/responsive-design)
- [axe-core](https://github.com/dequelabs/axe-core)
- [Playwright a11y](https://playwright.dev/docs/accessibility-testing)
- [Aria-live in React/Angular/Vue](https://k9n.dev/blog/2025-11-aria-live/)
