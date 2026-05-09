# Infra · Infrastructure as Code

🇮🇹 Tutto il necessario per deployare Jarvis in self-hosting o su cloud pubblico.
🇬🇧 Everything needed to deploy Jarvis self-hosted or on public cloud.

## Layout

```text
infra/
├── docker/        # Dockerfile per ciascun servizio + docker-compose
├── kubernetes/    # Manifesti K8s · Helm chart
├── terraform/     # Moduli IaC per AWS · GCP · Azure
├── monitoring/    # Prometheus · Grafana · OpenTelemetry
└── scripts/       # Bootstrap · backup · maintenance
```

## Profili di deployment · Deployment profiles

| Profilo | Target | Note |
|---|---|---|
| `local` | Docker Compose | MVP, single-host, sviluppo |
| `homelab` | K3s · Raspberry Pi 5 / NUC | Self-hosted casalingo |
| `cloud-vps` | Single VPS + Docker | Hosting economico |
| `kubernetes` | EKS · GKE · AKS · self-managed | Produzione, HA |

🇮🇹 Status: 🚧 work in progress.
🇬🇧 Status: 🚧 work in progress.
