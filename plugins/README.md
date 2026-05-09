# Plugins · Sistema plugin

🇮🇹 Sistema modulare per estendere le capacità di Jarvis.
🇬🇧 Modular system to extend Jarvis capabilities.

## Categorie · Categories

- **Productivity** — email · calendar · meeting summary · note-taking
- **Smart Home** — Home Assistant · MQTT · Zigbee · luci · termostati
- **Dev Tools** — code review · repository analysis · CI/CD trigger
- **Fitness** — training · biometrica · sleep coaching
- **Finance** — banking · investimenti · budget tracking
- **Web Scraping** — pipeline RAG personalizzate

## Creare un plugin · Build a plugin

🇮🇹 Parti da `plugins/_template/` come scaffold base.
🇬🇧 Start from `plugins/_template/` as a base scaffold.

```text
my-plugin/
├── manifest.yaml      # nome, versione, capability, scope
├── handlers/          # entrypoint dei trigger
├── tools/             # tool callabili dagli agenti (MCP)
└── tests/
```

🇮🇹 Status: 🚧 work in progress — scaffolding del template in arrivo.
🇬🇧 Status: 🚧 work in progress — template scaffolding coming.
