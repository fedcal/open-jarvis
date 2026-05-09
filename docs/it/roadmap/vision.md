# Vision & funzionalità future

Questa pagina elenca **tutte le funzionalità** che vogliamo costruire in **Jarvis**, organizzate per dominio. È volutamente ambiziosa: alcune funzioni sono prossime (Fase 1–3), altre sono di lungo termine (Fase 8+).

> Vedi le [Fasi di sviluppo](phases.md) per il piano operativo.

## 🧠 Identità AI persistente

- ✅ Identità unica per utente, federata su più server
- 🎯 Memoria condivisa (short/long/semantic) cross-device
- 🎯 "Persona" personalizzabile (tono, registro, lingua di output)
- 🎯 Multi-utente isolato (in caso di hosting per più persone)
- 🔮 Avatar olografico animato con lip-sync
- 🔮 Continuità "io che parlo con te" anche se cambi server o il tuo dominio

## 🗣️ Voce e dialogo

- ✅ Wake-word custom "Hey Jarvis"
- 🎯 STT multilingue (IT + EN nativo, altre via on-demand)
- 🎯 TTS naturale con voci scelte (Piper / Coqui)
- 🎯 Interruzione naturale (puoi tagliarmi mentre parlo)
- 🎯 Sub-vocal commands su occhiali smart
- 🔮 Cloning vocale per voce personalizzata (con vincoli etici)
- 🔮 Conversazioni multi-speaker (Jarvis sa chi sta parlando)

## 🌐 Ricerca e knowledge

- 🎯 Web search agentico (Crawl4AI + Firecrawl + Jina + ScrapeGraphAI)
- 🎯 RAG su documenti personali (Obsidian, Notion, Drive, Mail, file locali)
- 🎯 Visual RAG su PDF (ColQwen2)
- 🎯 Daily briefing personalizzato
- 🎯 Citazione delle fonti sempre presente
- 🔮 Knowledge graph personale (Zep / temporal KG)
- 🔮 Auto-aggiornamento di facts (es. il mio CV evolve nel tempo)
- 🔮 Federated knowledge sharing tra utenti consenzienti

## 🏃 Salute (Health)

- 🎯 Federazione wearable: Oura, Whoop, Polar, Garmin, Withings, Fitbit
- 🎯 CGM real-time (Dexcom)
- 🎯 Health vault FHIR R4/R5 condivisibile con medico
- 🎯 Coaching su sleep, training, recovery
- 🎯 Alerting biometrico personalizzato
- 🔮 Genomica personale (consenso dedicato)
- 🔮 Esami clinici (sangue, imaging) integrati nel vault
- 🔮 Mental wellness (mood tracking, sentiment voce)
- 🔮 Predizione salute con LLM su dati longitudinali

## 💰 Finanza

- 🎯 Aggregazione conti EU/UK via PSD2 (TrueLayer / GoCardless)
- 🎯 Portafoglio investimenti (IBKR, Alpaca)
- 🎯 Crypto multi-chain (Coinbase, Etherscan, Zerion)
- 🎯 Tracker subscription (Wallos)
- 🎯 Daily/weekly briefing finanziario
- 🎯 Alerting su movimenti significativi
- 🔮 Tax assistant (calcolo plusvalenze, dichiarazioni)
- 🔮 Goal-based investing (obiettivi vita + suggerimenti)
- 🔮 Scenario simulation Monte Carlo
- 🔮 ESG scoring del proprio portafoglio

## 📰 News & briefing

- 🎯 Aggregazione RSS/Atom (Miniflux backend)
- 🎯 News API commerciali (GDELT, Currents)
- 🎯 Reti decentralizzate (Bluesky, Mastodon)
- 🎯 Deduplication + topic filter + ranking personalizzato
- 🎯 Map-reduce summarisation
- 🎯 Audio briefing TTS
- 🔮 Fact-check cross-source automatico
- 🔮 Podcast → trascrizione → riassunto
- 🔮 Long-term trend tracking ("come è cambiato il dibattito su X?")

## 💻 Sviluppatore

- 🎯 Coding assistant cross-IDE (Cline + Aider + Goose)
- 🎯 MCP server custom per repo.search, gh.*
- 🎯 Code review da chat
- 🎯 Test generation TDD-first
- 🎯 Daily standup automatico
- 🔮 Architectural decision records auto-tagging
- 🔮 Ricerca semantica su PR/issue storiche
- 🔮 Pair programming con avatar olografico
- 🔮 Refactor inter-repo coordinato

## 🏠 Smart home

- 🎯 Bridge Home Assistant
- 🎯 Matter / Thread / Zigbee / Wi-Fi via HA
- 🎯 Frigate event ingestion (computer vision casalinga)
- 🎯 Routine automatiche (presence-aware, time-aware, biometric-aware)
- 🔮 Energy management con ottimizzazione AI (solare + storage + tariffa dinamica)
- 🔮 Sicurezza domestica (anomaly detection)
- 🔮 Cura piante (sensori + irrigazione)
- 🔮 Cura animali domestici (riconoscimento, alert)

## 🛠️ Maker (Blender + 3D printing)

- 🎯 Generazione 3D AI (TRELLIS-2, Tripo, Meshy)
- 🎯 Editing Blender via bpy
- 🎯 Slicer automation (PrusaSlicer / OrcaSlicer)
- 🎯 Controllo stampante (Klipper/Moonraker, OctoPrint, Bambu, Prusa)
- 🎯 Failure detection AI
- 🎯 Libreria modelli con AI tagging
- 🔮 Generazione di parti funzionali da specifica ("staffa che regge 5kg, M5 fissaggio")
- 🔮 Multi-printer farm orchestration
- 🔮 Recipe condivise dalla community Jarvis

## 👓 Realtà aumentata e occhiali smart

- 🎯 Brilliant Frame integration
- 🎯 MentraOS (Mach1, Vuzix Z100, Even Realities G1)
- 🎯 Overlay informativi contestuali (navigazione, info real-time)
- 🎯 Sub-vocal commands (silent voice)
- 🔮 Realtime translator overlay (sottotitoli AR live)
- 🔮 Face memory (riconoscere persone già incontrate)
- 🔮 Spatial agenda (eventi flottanti nello spazio)

## 🥽 Realtà virtuale

- 🎯 OpenXR su Quest, Index, Pico, Varjo (via Monado)
- 🎯 Avatar Jarvis 3D in VR
- 🔮 Workspace virtuale infinito
- 🔮 Esplorazione di knowledge in 3D
- 🔮 Co-presenza con altri Jarvis (federated multiplayer)

## ✨ Display olografici

- 🎯 Looking Glass Factory
- 🎯 Voxon Photonics
- 🎯 Avatar olografico parlante con lip-sync
- 🎯 Visualizzazioni dati 3D (portfolio, salute)
- 🔮 Ologramma proattivo (ti chiama lui senza essere chiamato)
- 🔮 Multi-display orchestration

## 📱 Mobile

- 🎯 App nativa iOS (App Intents, Live Activities, Widget)
- 🎯 App nativa Android (Tasker MCP, Termux bridge, Wear OS)
- 🎯 KDE Connect bridge bidirezionale
- 🔮 Android XR support
- 🔮 iOS Vision Pro support
- 🔮 Shortcut Marketplace community-driven

## 🤖 Agenti specializzati

- 🎯 Desktop, Mobile, Watch, Browser, Voice agents
- 🎯 Glasses, VR, Holo, Medical, Scraping agents
- 🔮 Travel agent (booking, route planning, packing)
- 🔮 Cooking agent (ricette, lista spesa, coaching)
- 🔮 Garden agent (irrigazione, semine, raccolto)
- 🔮 Music agent (playlist contestuali, scoperte)
- 🔮 Pet agent (cura animali domestici)
- 🔮 Education agent (corsi, ripassi, flash card)
- 🔮 Therapist agent (con vincoli etici stringenti)

## 🔌 Plugin marketplace

- 🎯 Sistema plugin con manifest YAML
- 🎯 Scaffold `plugins/_template/`
- 🔮 Marketplace pubblico con review e rating
- 🔮 Plugin a pagamento (con revenue share opzionale)
- 🔮 Plugin verificati (security audit)

## 🌍 Federazione e multi-instance

- 🔮 OIDC Federation tra istanze Jarvis di amici/famiglia
- 🔮 Trust delegation ("mio padre può chiedere a Jarvis di mia madre cose limitate")
- 🔮 Knowledge sharing opt-in tra istanze
- 🔮 Marketplace di "personas" condivise

## 🔐 Sicurezza e privacy avanzate

- 🎯 Cifratura at-rest dei dati
- 🎯 Vault separati per finance/health
- 🎯 Audit log completo
- 🔮 Zero-knowledge sync tra device
- 🔮 Revoca remota di un device compromesso
- 🔮 Modalità "panico" (cancellazione veloce di dati sensibili)
- 🔮 E2E encryption della conversazione

## 🌱 Sostenibilità

- 🔮 Tracking del proprio carbon footprint personale
- 🔮 Suggerimenti di riduzione (mobilità, alimentazione, energia)
- 🔮 Integrazione con scelte etiche (energia verde, banche etiche)

## 🧪 Sperimentale (lungo termine)

- 🔮 BCI integration (Neuralink, Synchron, Neurable per gaming)
- 🔮 Robot domestici (1X Neo, Figure)
- 🔮 Auto a guida autonoma (Tesla, Mercedes, Waymo API)
- 🔮 Drone integration (DJI SDK)
- 🔮 Smart appliances con AI (Samsung, LG, Bosch)

---

> **Legenda:**
>
> - ✅ Disponibile (Fase 0)
> - 🎯 Pianificato (Fase 1–8)
> - 🔮 Vision long-term (Fase 9+)
>
> La vision è ambiziosa di proposito. Non tutto verrà implementato. Quello che verrà implementato sarà spesso grazie a contributi della community — vedi [Contribuire](../contributing/index.md).
