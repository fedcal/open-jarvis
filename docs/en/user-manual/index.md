# User manual

Welcome to the **Jarvis user manual**: a progressive guide to **install**, **configure** and **use** your personal AI assistant.

!!! info "Living document"
    This manual is a *living document*: it is updated with every release as new features land. The [Development phases](../roadmap/phases.md) page lists what is already available and what is coming.

## Manual structure

<div class="grid cards" markdown>

- :material-download:{ .lg .middle } **[Installation](installation.md)**

    ---

    Everything you need to bring up your first Jarvis node: hardware/software requirements, Docker, first boot.

- :material-cog:{ .lg .middle } **[Configuration](configuration.md)**

    ---

    Environment variables, OAuth, device pairing, LLM model choice, secrets vault.

- :material-rocket-launch:{ .lg .middle } **[Daily usage](usage.md)**

    ---

    How to talk to Jarvis, how to move between devices, how to use health, finance, news, RAG features.

- :material-tools:{ .lg .middle } **[Troubleshooting](troubleshooting.md)**

    ---

    Most common errors, logs to read, diagnostic commands, how to restore the instance.

- :material-help-circle:{ .lg .middle } **[FAQ](faq.md)**

    ---

    Quick answers to the most frequent questions about privacy, costs, supported devices.

</div>

## What you should know before starting

- 🐳 **Docker** is the easiest way to run Jarvis. Throughout this manual we assume Docker is installed.
- 🔐 Jarvis is **self-hosted**: your data stays on your hardware. You are the administrator.
- 🌍 Runs on Linux, macOS and Windows (via WSL2 for Windows).
- 🧪 It is in **MVP phase**: some described features are on the roadmap. See [Phases](../roadmap/phases.md).

## Typical use cases

- **Solo developer** wanting a cross-IDE coding assistant → see [Developer](../features/developer.md)
- **Health-tech user** with Oura/Whoop wanting longitudinal insights → see [Health](../features/health.md)
- **Self-managed investor** wanting a financial dashboard and briefings → see [Finance](../features/finance.md)
- **Maker / 3D printing enthusiast** with a connected printer → see [Maker](../features/maker.md)
- **Knowledge worker** with lots of Obsidian/Notion notes → see [RAG](../features/rag.md)

> Ready? Start from [Installation →](installation.md)
