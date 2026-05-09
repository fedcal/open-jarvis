---
title: "Installazione server VPS"
description: "Guida completa al deploy del server Open-Jarvis su VPS cloud (Hetzner, OVH, AWS, DigitalOcean) con Docker, Caddy TLS, WireGuard e hardening sicurezza."
---

# Installazione server (VPS cloud)

Il server Jarvis è il cuore del sistema: vive su una VPS sempre raggiungibile e coordina tutti i dispositivi personali via WireGuard.

## Provider VPS consigliati

| Provider | Specifica minima | Costo mese | Note |
|---|---|---|---|
| **Hetzner CCX13** | 2 vCPU AMD, 8 GB RAM, 80 GB NVMe | ~14 € | Migliore rapporto qualità/prezzo EU |
| **Hetzner CX31** | 2 vCPU, 8 GB, 80 GB | ~10 € | Più economico, Intel/AMD shared |
| **OVH VPS Value** | 2 vCPU, 4 GB | ~6 € | Datacenter EU |
| **DigitalOcean** | 2 vCPU, 8 GB | $48 | Buona docs, region globali |
| **Hetzner dedicato AX42** | 6 core, 64 GB | ~40 € | GPU compatibile, LLM locale |

**Requisiti minimi:** 4 GB RAM (8 GB raccomandati con Ollama locale), 2 vCPU, 40 GB SSD, IPv4 + IPv6.

## 1. Setup OS base (Ubuntu 24.04 LTS)

```bash
# Update + tools essenziali
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw fail2ban auditd unattended-upgrades \
                    apt-transport-https ca-certificates gnupg lsb-release

# Crea utente non-root
sudo adduser jarvis --disabled-password --gecos ""
sudo usermod -aG sudo jarvis
sudo mkdir -p /home/jarvis/.ssh
sudo cp ~/.ssh/authorized_keys /home/jarvis/.ssh/
sudo chown -R jarvis:jarvis /home/jarvis/.ssh
sudo chmod 700 /home/jarvis/.ssh
sudo chmod 600 /home/jarvis/.ssh/authorized_keys
```

## 2. SSH hardening

```bash
sudo nano /etc/ssh/sshd_config
```

Imposta:

```ini
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers jarvis
MaxAuthTries 3
```

```bash
sudo systemctl restart sshd
# Test in altra sessione: ssh -p 2222 jarvis@<vps-ip>
```

Aggiungi `[sshd]` a fail2ban (vedi [Architettura sicurezza](../../security/architecture.md)).

## 3. Firewall UFW

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment "SSH"
sudo ufw allow 443/tcp comment "HTTPS"
sudo ufw allow 51820/udp comment "WireGuard"
sudo ufw enable
```

## 4. Docker + Compose

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker jarvis
newgrp docker
docker --version
docker compose version
```

## 5. Clone e configurazione Jarvis

```bash
cd /opt
sudo git clone https://github.com/fedcal/open-jarvis.git
sudo chown -R jarvis:jarvis open-jarvis
cd open-jarvis
cp .env.example .env
nano .env
```

Configura **almeno**:

```env
JARVIS_ENVIRONMENT=production
JARVIS_DOMAIN=jarvis.tuodominio.com
JARVIS_PUBLIC_URL=https://jarvis.tuodominio.com
JARVIS_SERVER_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://jarvis:STRONG_PASSWORD@postgres:5432/jarvis
```

## 6. Caddy reverse proxy con TLS automatico

```bash
sudo apt install -y caddy
sudo nano /etc/caddy/Caddyfile
```

```caddyfile
jarvis.tuodominio.com {
  tls {
    protocols tls1.3
  }
  header {
    Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Content-Security-Policy "default-src 'self'"
    X-Frame-Options "DENY"
    -Server
  }
  reverse_proxy /api/* localhost:8080
  reverse_proxy /* localhost:3000
}
```

```bash
sudo systemctl restart caddy
# Test certificato: curl -I https://jarvis.tuodominio.com
```

## 7. WireGuard VPN

```bash
sudo apt install -y wireguard
cd /etc/wireguard
sudo wg genkey | sudo tee private.key | sudo wg pubkey | sudo tee public.key
sudo nano /etc/wireguard/wg0.conf
```

Configurazione hub: vedi [Architettura sicurezza § 2.1](../../security/architecture.md).

```bash
sudo systemctl enable --now wg-quick@wg0
sudo wg show
```

## 8. Avvio Jarvis

```bash
cd /opt/open-jarvis
docker compose up -d
docker compose ps
docker compose logs -f --tail 100
```

Verifica health:

```bash
curl https://jarvis.tuodominio.com/health
```

Apri il browser su <https://jarvis.tuodominio.com> e crea il primo account (sarà l'**Owner**).

## 9. Backup automatico

```bash
sudo nano /etc/cron.d/jarvis-backup
```

```cron
0 3 * * * jarvis cd /opt/open-jarvis && docker compose exec -T postgres pg_dump -U jarvis jarvis | age --recipient $(cat ~/.config/jarvis/backup.pub) > /backups/jarvis-$(date +\%Y\%m\%d).sql.age
```

## 10. Aggiornamenti

```bash
cd /opt/open-jarvis
git pull
docker compose pull
docker compose up -d
docker compose exec server jarvis db migrate
```

## Troubleshooting

Vedi la pagina [Risoluzione problemi](../troubleshooting.md).
