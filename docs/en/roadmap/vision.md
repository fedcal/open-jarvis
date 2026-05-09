# Vision & future features

This page lists **all the features** we want to build into **Jarvis**, organised by domain. It is intentionally ambitious: some features are imminent (Phase 1–3), others are long-term (Phase 8+).

> See the [Development phases](phases.md) for the operational plan.

## 🧠 Persistent AI identity

- ✅ Single identity per user, federated across multiple servers
- 🎯 Shared memory (short/long/semantic) cross-device
- 🎯 Customisable "persona" (tone, register, output language)
- 🎯 Isolated multi-user (when hosting for multiple people)
- 🔮 Animated holographic avatar with lip-sync
- 🔮 "It's me talking to you" continuity even if you change server or domain

## 🗣️ Voice and dialogue

- ✅ Custom "Hey Jarvis" wake-word
- 🎯 Multilingual STT (native IT + EN, others on-demand)
- 🎯 Natural TTS with chosen voices (Piper / Coqui)
- 🎯 Natural interruption (you can cut me off while I speak)
- 🎯 Sub-vocal commands on smart glasses
- 🔮 Voice cloning for personalised voice (with ethical constraints)
- 🔮 Multi-speaker conversations (Jarvis knows who is speaking)

## 🌐 Search and knowledge

- 🎯 Agentic web search (Crawl4AI + Firecrawl + Jina + ScrapeGraphAI)
- 🎯 RAG over personal documents (Obsidian, Notion, Drive, Mail, local files)
- 🎯 Visual RAG over PDFs (ColQwen2)
- 🎯 Personalised daily briefing
- 🎯 Source citations always present
- 🔮 Personal knowledge graph (Zep / temporal KG)
- 🔮 Auto-updating facts (e.g. my CV evolves over time)
- 🔮 Federated knowledge sharing between consenting users

## 🏃 Health

- 🎯 Wearable federation: Oura, Whoop, Polar, Garmin, Withings, Fitbit
- 🎯 Real-time CGM (Dexcom)
- 🎯 FHIR R4/R5 health vault shareable with doctor
- 🎯 Coaching on sleep, training, recovery
- 🎯 Personalised biometric alerting
- 🔮 Personal genomics (dedicated consent)
- 🔮 Clinical exams (blood, imaging) integrated in the vault
- 🔮 Mental wellness (mood tracking, voice sentiment)
- 🔮 Health prediction with LLM on longitudinal data

## 💰 Finance

- 🎯 EU/UK account aggregation via PSD2 (TrueLayer / GoCardless)
- 🎯 Investment portfolio (IBKR, Alpaca)
- 🎯 Multi-chain crypto (Coinbase, Etherscan, Zerion)
- 🎯 Subscription tracker (Wallos)
- 🎯 Daily/weekly financial briefing
- 🎯 Alerts on significant moves
- 🔮 Tax assistant (capital gains calc, filings)
- 🔮 Goal-based investing (life goals + suggestions)
- 🔮 Monte Carlo scenario simulation
- 🔮 Portfolio ESG scoring

## 📰 News & briefing

- 🎯 RSS/Atom aggregation (Miniflux backend)
- 🎯 Commercial news APIs (GDELT, Currents)
- 🎯 Decentralised networks (Bluesky, Mastodon)
- 🎯 Deduplication + topic filter + personalised ranking
- 🎯 Map-reduce summarisation
- 🎯 TTS audio briefing
- 🔮 Automatic cross-source fact-check
- 🔮 Podcast → transcription → summary
- 🔮 Long-term trend tracking ("how did the debate on X evolve?")

## 💻 Developer

- 🎯 Cross-IDE coding assistant (Cline + Aider + Goose)
- 🎯 Custom MCP server for repo.search, gh.*
- 🎯 Code review from chat
- 🎯 TDD-first test generation
- 🎯 Automated daily standup
- 🔮 Architectural decision records auto-tagging
- 🔮 Semantic search over historical PRs/issues
- 🔮 Pair programming with holographic avatar
- 🔮 Coordinated cross-repo refactor

## 🏠 Smart home

- 🎯 Home Assistant bridge
- 🎯 Matter / Thread / Zigbee / Wi-Fi via HA
- 🎯 Frigate event ingestion (home computer vision)
- 🎯 Automated routines (presence-aware, time-aware, biometric-aware)
- 🔮 AI-optimised energy management (solar + storage + dynamic tariff)
- 🔮 Home security (anomaly detection)
- 🔮 Plant care (sensors + irrigation)
- 🔮 Pet care (recognition, alerts)

## 🛠️ Maker (Blender + 3D printing)

- 🎯 AI 3D generation (TRELLIS-2, Tripo, Meshy)
- 🎯 Blender editing via bpy
- 🎯 Slicer automation (PrusaSlicer / OrcaSlicer)
- 🎯 Printer control (Klipper/Moonraker, OctoPrint, Bambu, Prusa)
- 🎯 AI failure detection
- 🎯 Model library with AI tagging
- 🔮 Functional part generation from spec ("bracket holding 5kg, M5 mount")
- 🔮 Multi-printer farm orchestration
- 🔮 Community-shared Jarvis recipes

## 👓 Augmented reality and smart glasses

- 🎯 Brilliant Frame integration
- 🎯 MentraOS (Mach1, Vuzix Z100, Even Realities G1)
- 🎯 Contextual informational overlays (navigation, real-time info)
- 🎯 Sub-vocal commands (silent voice)
- 🔮 Real-time translator overlay (live AR subtitles)
- 🔮 Face memory (recognise people you've met before)
- 🔮 Spatial agenda (events floating in space)

## 🥽 Virtual reality

- 🎯 OpenXR on Quest, Index, Pico, Varjo (via Monado)
- 🎯 3D Jarvis avatar in VR
- 🔮 Infinite virtual workspace
- 🔮 3D knowledge exploration
- 🔮 Co-presence with other Jarvis (federated multiplayer)

## ✨ Holographic displays

- 🎯 Looking Glass Factory
- 🎯 Voxon Photonics
- 🎯 Holographic talking avatar with lip-sync
- 🎯 3D data visualisations (portfolio, health)
- 🔮 Proactive hologram (it calls you without being called)
- 🔮 Multi-display orchestration

## 📱 Mobile

- 🎯 Native iOS app (App Intents, Live Activities, Widget)
- 🎯 Native Android app (Tasker MCP, Termux bridge, Wear OS)
- 🎯 KDE Connect bidirectional bridge
- 🔮 Android XR support
- 🔮 iOS Vision Pro support
- 🔮 Community-driven Shortcut Marketplace

## 🤖 Specialised agents

- 🎯 Desktop, Mobile, Watch, Browser, Voice agents
- 🎯 Glasses, VR, Holo, Medical, Scraping agents
- 🔮 Travel agent (booking, route planning, packing)
- 🔮 Cooking agent (recipes, shopping list, coaching)
- 🔮 Garden agent (irrigation, planting, harvest)
- 🔮 Music agent (contextual playlists, discovery)
- 🔮 Pet agent (pet care)
- 🔮 Education agent (courses, reviews, flash cards)
- 🔮 Therapist agent (with strict ethical constraints)

## 🔌 Plugin marketplace

- 🎯 Plugin system with YAML manifest
- 🎯 Scaffold `plugins/_template/`
- 🔮 Public marketplace with reviews and ratings
- 🔮 Paid plugins (with optional revenue share)
- 🔮 Verified plugins (security audit)

## 🌍 Federation and multi-instance

- 🔮 OIDC Federation between Jarvis instances of friends/family
- 🔮 Trust delegation ("my dad can ask my mum's Jarvis limited things")
- 🔮 Opt-in knowledge sharing between instances
- 🔮 Marketplace of shared "personas"

## 🔐 Advanced security and privacy

- 🎯 At-rest data encryption
- 🎯 Separate vaults for finance/health
- 🎯 Full audit log
- 🔮 Zero-knowledge sync between devices
- 🔮 Remote revocation of a compromised device
- 🔮 "Panic" mode (fast deletion of sensitive data)
- 🔮 E2E encryption of the conversation

## 🌱 Sustainability

- 🔮 Personal carbon-footprint tracking
- 🔮 Reduction suggestions (mobility, food, energy)
- 🔮 Integration with ethical choices (green energy, ethical banks)

## 🧪 Experimental (long-term)

- 🔮 BCI integration (Neuralink, Synchron, Neurable for gaming)
- 🔮 Domestic robots (1X Neo, Figure)
- 🔮 Self-driving cars (Tesla, Mercedes, Waymo APIs)
- 🔮 Drone integration (DJI SDK)
- 🔮 AI-powered smart appliances (Samsung, LG, Bosch)

---

> **Legend:**
>
> - ✅ Available (Phase 0)
> - 🎯 Planned (Phase 1–8)
> - 🔮 Long-term vision (Phase 9+)
>
> The vision is intentionally ambitious. Not everything will be implemented. What does get implemented will often be thanks to community contributions — see [Contributing](../contributing/index.md).
