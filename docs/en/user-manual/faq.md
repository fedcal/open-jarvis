# FAQ

Quick answers to the most common questions.

## General

### Is Jarvis free?

Yes. The **code is MIT** and completely free, including commercial use. Any costs come only from external providers you choose (cloud LLM APIs, hosting, hardware).

### Do I need to be a developer to use it?

In **Phase 0–1** (current): yes, you need to be comfortable with the command line and Docker.
From **Phase 2** onwards: a one-click installer for end-users will be released.

### Can I use it without internet?

Partially yes:

- ✅ Memory, RAG over your docs, chat with local LLMs (Ollama) → **offline**
- ❌ News, web search, finance APIs, cloud wearable sync → **need internet**

### How much does it cost?

| Item | Cost |
|---|---|
| Jarvis software | 0 € |
| Hardware (home PC) | from 300 € (refurbished NUC) to 2,000 € (workstation with GPU) |
| Cloud LLM (optional) | from 5 €/month (light) to 50 €/month (heavy) |
| Local LLM (Ollama) | 0 € (already included) |
| Wearable APIs (Oura, Whoop) | depend on the device, the APIs are free |

## Privacy

### Does my data go to a third-party cloud?

**Only if you decide it does.** By default everything stays on hardware you manage. If you enable a cloud LLM provider (e.g. Anthropic, OpenAI), every message sent to that provider follows their privacy policies.

### Can I use Jarvis 100% locally?

Yes:

```env
JARVIS_MODEL_LARGE=ollama/qwen2.5:14b
EMBEDDING_MODEL=ollama/bge-m3
SEARCH_PROVIDER=searxng     # instead of Bing/Google
```

### Does Jarvis record audio continuously?

No. The **wake-word** is a tiny on-device model (Porcupine) that listens locally without sending anything out. Audio is sent to the server only after "Hey Jarvis" activation.

### How do I delete all my data?

From the UI: **Settings → Advanced → Delete everything**.
From CLI:

```bash
docker compose exec server jarvis user delete --me --confirm
```

## Devices

### What systems does the server run on?

Linux, macOS, Windows (via WSL2). Even on **Raspberry Pi 5 / 4 GB**, but with small local LLMs only.

### Which devices can I pair?

See the [Devices](../devices/index.md) page. In short:

- Desktop / laptop (Linux, macOS, Windows)
- Smartphone (iOS 17+, Android 10+)
- Smartwatch (Apple Watch, Wear OS, Garmin, PineTime, Bangle.js)
- Smart glasses (Brilliant Frame, MentraOS, XREAL)
- VR headsets (Meta Quest, Valve Index, Pico, Varjo)
- Holographic displays (Looking Glass, Voxon)
- Medical wearables (Oura, Whoop, Polar, Garmin, Withings, Fitbit, Dexcom)
- 3D printers (Klipper/Moonraker, OctoPrint, Bambu, Prusa)

### Can I add a device that is not on the list?

Yes, by writing a custom agent. See [Contributing](../contributing/index.md) and the example in `agents/_template/`.

## Security

### What happens if my server gets compromised?

- Secrets are in `.env` encrypted at rest (LUKS/FileVault recommended)
- User sessions use short-lived JWT (60 minutes)
- Biometric and financial data can be further encrypted with a per-user key

In case of compromise: rotate all tokens, re-issue device certificates, audit logs.

### How do I report a vulnerability?

See [SECURITY.md](https://github.com/fedcal/open-jarvis/blob/main/SECURITY.md). **Do not open public issues.**

## Roadmap & contributions

### When will feature X be ready?

See [Development phases](../roadmap/phases.md). Dates are indicative — velocity depends on contributors.

### How can I contribute?

See [Contributing](../contributing/index.md). Every contribution is welcome, even if you are not a developer: translations, bug reports, ideas, tests on real hardware.

### Can I use it in my commercial product?

Yes. The MIT licence explicitly allows it. We appreciate (but do not require) a project mention.

## Support

- 🐛 [GitHub issues](https://github.com/fedcal/open-jarvis/issues) — bugs and feature requests
- 💬 [GitHub discussions](https://github.com/fedcal/open-jarvis/discussions) — questions and ideas
- 🌐 [federicocalo.dev](https://federicocalo.dev) — the maintainer's website
