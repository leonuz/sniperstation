# snipermqtt — Deployment Plan

**Host:** snipermox.uzc (192.168.0.2) — Proxmox 9.1.5
**LXC Name:** snipermqtt
**OS:** Debian 12 (Bookworm)
**Storage:** local2 (all — template, rootdir, photos)
**Network:** vmbr0 (LAN 192.168.0.x)
**Static IP:** 192.168.0.78 (pending pfSense DHCP static mapping)

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
| Network | vmbr0, static 192.168.0.78/24, gw 192.168.0.254 |
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
- ACL file: per-topic permissions per user
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

### 5. Telegram Bot
- Runtime: Python 3 (system)
- Location: `/opt/sniperstation/telegram_bot/`
- Service: systemd unit, loads secrets from `/etc/sniperstation/secrets.env`
- Auth: restricted to authorized chat_id only

### 6. nginx
- Role: reverse proxy for Grafana (HTTPS) + HTTP endpoint for TimerCam X photos
- Ports: 80 (redirect to 443), 443 (Grafana + /upload endpoint)
- Rate limiting: 10 req/min on /upload
- Photo storage: `/mnt/sniperstation/photos/`

---

## Directory Structure (inside LXC)

```
/etc/mosquitto/
├── mosquitto.conf
├── passwd
└── acl

/etc/sniperstation/
└── secrets.env          # chmod 600 — all service secrets

/etc/telegraf/
└── telegraf.conf

/opt/sniperstation/
└── telegram_bot/
    ├── bot.py
    └── requirements.txt

/var/sniperstation/
└── photos/
    ├── sucufer/         # YYYY-MM-DD_HH.jpg
    └── sucurod/

/etc/nginx/sites-available/
├── grafana.conf
└── timercam.conf
```

---

## Photo Storage (local2)

Photos from TimerCam X are stored inside the LXC at `/var/sniperstation/photos/`.
The LXC disk is on local2 — no separate mount needed for initial setup.
If photo volume grows, a dedicated local2 bind mount can be added later.

---

## Installation Order

1. Download Debian 12 template to local2
2. Create LXC (pct create)
3. Start LXC, initial setup (locale, timezone, apt update/upgrade)
4. Install Mosquitto → configure auth + ACL
5. Install InfluxDB 2.x → create org, bucket, tokens
6. Install Telegraf → configure MQTT input + InfluxDB output
7. Install Grafana → configure datasource, change admin password
8. Install nginx → configure reverse proxy + /upload endpoint
9. Deploy Telegram bot → systemd service
10. Create photo directories with correct permissions
11. Apply security hardening (fail2ban, file permissions, secrets.env)
12. Smoke test: publish test MQTT message → verify in InfluxDB → verify in Grafana

---

## Security Checklist (Phase 3 — from ROADMAP)

- [ ] `allow_anonymous false` in Mosquitto
- [ ] One MQTT user per device with ACL
- [ ] InfluxDB tokens with minimal permissions
- [ ] Grafana default password changed, sign-up disabled
- [ ] nginx rate limiting on /upload
- [ ] `/etc/sniperstation/secrets.env` chmod 600
- [ ] fail2ban for Mosquitto and Grafana
- [ ] Telegram bot restricted to authorized chat_id

---

*Plan created: 2026-03-27*
*Execute only after Leo confirms.*
