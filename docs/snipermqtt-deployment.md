# snipermqtt — Deployment Plan

**Host:** snipermox.uzc (192.168.0.2) — Proxmox 9.1.5
**LXC Name:** snipermqtt.uzc
**OS:** Debian 12 (Bookworm)
**Storage:** local2 (all — template, rootdir, photos)
**Network:** vmbr0 (LAN 192.168.0.x)
**Static IP:** 192.168.0.79
**DNS:** snipermqtt.uzc (registered in Pi-hole)
**MAC:** pending — auto-generated on LXC creation, then reserved in pfSense

---

## Proxmox Rules (non-negotiable)

- NO rebooting Proxmox host
- NO touching existing VMs or LXCs (100–111, 200)
- NO modifying network bridges or Proxmox network config
- Updates allowed inside the new LXC only
- If a reboot is required (kernel update etc.) → ask Leo first

---

## LXC Specifications

| Parameter | Value |
|---|---|
| VMID | 112 |
| Hostname | snipermqtt |
| Template | debian-12-standard_12.x_amd64.tar.zst (download to local2) |
| Storage | local2 |
| Disk | 20GB |
| RAM | 1024 MB |
| Swap | 512 MB |
| CPU | 2 cores |
| Network | vmbr0, static 192.168.0.79/24, gw 192.168.0.254 |
| DNS | 192.168.0.240 (sniperhole Pi-hole) |
| Unprivileged | yes |
| Start on boot | yes |

---

## Services to Install

### 1. Mosquitto (MQTT broker)
- Version: latest from Debian 12 repos (`apt install mosquitto`)
- Port: 1883 (plaintext, temporary) → 8883 (MQTTS, Phase 3 security)
- Config: `/etc/mosquitto/mosquitto.conf`
- Auth: one user per device (station485, cyd_master, cyd_kids, timercam, telegraf_bridge, telegram_bot)
- ACL file: per-topic permissions per user (see `docs/security.md` §6.2)
- Logs: `/var/log/mosquitto/mosquitto.log`

### 2. InfluxDB 2.x
- Install method: official InfluxData apt repo for Debian 12
- Port: 8086
- Org: `sniperstation`
- Bucket: `sniperstation`
- Tokens: write-only (Telegraf), read-only (Grafana)

### 3. Grafana
- Install method: official Grafana Labs apt repo
- Port: 3000 (behind nginx reverse proxy on 443)
- Datasource: InfluxDB (read-only token)
- Admin: rename from default, strong password, 2FA

### 4. Telegraf (MQTT → InfluxDB bridge)
- Install method: official InfluxData apt repo
- Role: subscribe to `sniperstation/#` on Mosquitto, write to InfluxDB
- Config: `/etc/telegraf/telegraf.conf`

### 5. Telegram Bot (with natural language + reports)
- Runtime: Python 3 (system)
- Location: `/opt/sniperstation/telegram_bot/`
- Service: systemd unit, loads secrets from `/etc/sniperstation/secrets.env`
- Auth: restricted to authorized chat_id only
- **Natural language:** Claude API (claude-opus-4-6) — queries InfluxDB and responds conversationally
  - Examples: "¿Cómo están las matas?", "¿Cuándo fue el último riego?", "¿Qué temperatura hay afuera?"
  - Same agentic pattern as SniperFIN
- **Email reports via Resend API:**
  - Daily x3: temperature (all rooms) + humidity + soil status
  - Weekly x1: irrigation summary, trends, anomalies
  - Monthly x1: full historical stats
  - Recipient: leonuz@hotmail.com

### 6. nginx
- Role: reverse proxy for Grafana (HTTPS) + HTTP endpoint for TimerCam X photos
- Ports: 80 (redirect to 443), 443 (Grafana + /upload endpoint)
- TLS: certificates from pfSense CA
- Rate limiting: 10 req/min on /upload
- Photo storage: `/var/sniperstation/photos/`

---

## TLS / Certificates

- CA: pfSense internal CA (already exists)
- Cert files location in LXC: `/etc/sniperstation/certs/` (chmod 700)
- Temp staging on Proxmox host: `/root/sniperstation-certs/` (chmod 700) — never in git
- Used by: nginx (HTTPS), Mosquitto (MQTTS port 8883)

---

## Secrets

All secrets stored in `/etc/sniperstation/secrets.env` — `chmod 600`, loaded via systemd `EnvironmentFile`.

| Secret | Used by |
|---|---|
| MQTT passwords (per device) | Each ESP32 firmware + services |
| InfluxDB write token | Telegraf |
| InfluxDB read token | Grafana |
| Telegram bot token | Bot |
| Telegram chat_id | Bot |
| Claude API key | Bot (natural language) |
| Resend API key | Bot (email reports) |
| TimerCam API key | Bot + nginx /upload |

---

## Directory Structure (inside LXC)

```
/etc/mosquitto/
├── mosquitto.conf
├── passwd
└── acl

/etc/sniperstation/
├── secrets.env          # chmod 600 — all service secrets
└── certs/               # chmod 700 — TLS certs from pfSense CA

/etc/telegraf/
└── telegraf.conf

/opt/sniperstation/
└── telegram_bot/
    ├── bot.py
    ├── agent.py          # LLM loop (Claude API)
    ├── tools.py          # InfluxDB query tools
    ├── reports.py        # Daily/weekly/monthly email reports (Resend)
    └── requirements.txt

/var/sniperstation/
└── photos/
    ├── sucufer/          # YYYY-MM-DD_HH.jpg
    └── sucurod/

/etc/nginx/sites-available/
├── grafana.conf
└── timercam.conf
```

---

## Installation Order

1. Download Debian 12 template to local2
2. Create LXC (pct create) → get auto-generated MAC
3. Register MAC in pfSense (IP 192.168.0.79) + DNS in Pi-hole (snipermqtt.uzc)
4. Start LXC, initial setup (locale, timezone America/New_York, apt update/upgrade)
5. Install Mosquitto → configure auth + ACL
6. Install InfluxDB 2.x → create org, bucket, tokens
7. Install Telegraf → configure MQTT input + InfluxDB output
8. Install Grafana → configure datasource, change admin password
9. Install nginx → configure reverse proxy + /upload endpoint + TLS certs from pfSense CA
10. Deploy Telegram bot → systemd service (natural language + reports)
11. Create photo directories with correct permissions
12. Apply security hardening (fail2ban, file permissions, secrets.env)
13. Smoke test: publish test MQTT message → verify in InfluxDB → verify in Grafana → verify Telegram

---

## Security Checklist (Phase 3 — from ROADMAP)

- [ ] `allow_anonymous false` in Mosquitto
- [ ] One MQTT user per device with ACL
- [ ] InfluxDB tokens with minimal permissions
- [ ] Grafana default password changed, sign-up disabled, 2FA enabled
- [ ] nginx rate limiting on /upload
- [ ] TLS on nginx (pfSense CA cert)
- [ ] `/etc/sniperstation/secrets.env` chmod 600
- [ ] `/etc/sniperstation/certs/` chmod 700
- [ ] fail2ban for Mosquitto and Grafana
- [ ] Telegram bot restricted to authorized chat_id

---

*Plan created: 2026-03-27*
*Updated: 2026-03-27 — IP 192.168.0.79, DNS snipermqtt.uzc, Claude API NL bot, Resend email reports, pfSense CA for TLS*
