# SniperStation — Security Hardening Guide

> Reference document for securing the complete SniperStation software stack.
> Applies to: M5Stack Station-485, CYD ESP32-2432S028 (x2), M5Stack TimerCam X, Proxmox LXC (Mosquitto, InfluxDB, Grafana, Telegram Bot).
> Home network — Orlando, Florida.

---

## Index

1. [Layer 1 — Physical](#1-layer-1--physical)
2. [Layer 2 — Data Link](#2-layer-2--data-link)
3. [Layer 3 — Network](#3-layer-3--network)
4. [Layer 4 — Transport](#4-layer-4--transport)
5. [Layer 5 — Session](#5-layer-5--session)
6. [Layer 7 — Application](#6-layer-7--application)
7. [Authentication and Authorization](#7-authentication-and-authorization)
8. [Encryption in Transit](#8-encryption-in-transit)
9. [Encryption at Rest](#9-encryption-at-rest)
10. [ESP32 Firmware Security](#10-esp32-firmware-security)
11. [Network Segmentation — IoT VLAN](#11-network-segmentation--iot-vlan)
12. [Secrets Management](#12-secrets-management)
13. [Security Monitoring and Alerts](#13-security-monitoring-and-alerts)
14. [Physical Security](#14-physical-security)

---

## Conventions

| Icon | Priority |
|------|----------|
| 🔴 | **HIGH** — real risk, implement before going to production |
| 🟡 | **MEDIUM** — significant posture improvement, implement within first week |
| 🟢 | **LOW** — additional hardening, good practice |

| Symbol | Difficulty |
|--------|-----------|
| ⚡ | Easy — under 30 min, no specialized prior knowledge required |
| 🔧 | Medium — requires editing configs or compiling firmware |
| 🛠️ | Hard — architectural changes, TLS certificates, NVS flash |

---

## 1. Layer 1 — Physical

### 1.1 Weatherproof lockable enclosure

**What:** The Station-485 is outdoors in Orlando. Anyone who can physically touch it can reset it, read WiFi credentials if the firmware is unprotected, or simply destroy it.

**How:**
- Use an IP65 or better enclosure with security screws (Torx or hexalobe) instead of standard Phillips.
- If budget allows: enclosure with padlock.
- Mount at a minimum height of 1.8m above ground, or in a non-obvious location.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 1.2 ESP32 reset button protection

**What:** The EN (reset) button on the Station-485 and CYDs allows a physical reset that can interrupt irrigation or clear SRAM state.

**How:**
- In the outdoor enclosure: mechanically cover or block access to the EN button with a 3D-printed plastic stopper.
- For indoor CYDs: custom 3D enclosures should expose only the screen, with no access to the EN button.

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 1.3 Sealed cable management

**What:** Cables exiting the outdoor enclosure (Grove sensors, relay, 12V) are water entry points and physical tampering vectors.

**How:**
- Use PG7 or PG9 cable glands for each cable passing through the enclosure wall.
- Seal with neutral silicone (not acetic) around the glands once installed.
- Use corrugated cable conduit between the enclosure and planters for pump cables.

**Priority:** 🔴 HIGH (Orlando heavy rain) | **Difficulty:** ⚡ Easy

---

### 1.4 Hardware theft protection

**What:** The TimerCam X is outdoors without an enclosure and could be stolen.

**How:**
- Mount the camera with screws from the inside (not accessible from outside).
- Use a Kensington-style security cable if mounting on a flat surface.
- Document the serial number of each ESP32 and M5Stack for insurance claims if applicable.

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

## 2. Layer 2 — Data Link

### 2.1 Disable WPS on the router

**What:** WPS (WiFi Protected Setup) has known vulnerabilities (Pixie Dust attack, PIN brute force) that allow obtaining the WiFi password without knowing it. If the ESP32s are on the main network, compromising WPS compromises everything.

**How:**
- Access the router panel (192.168.1.1 or similar).
- Find the "Wireless" or "Advanced Wireless Settings" section.
- Completely disable "WPS" / "Wi-Fi Protected Setup".

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 2.2 MAC filtering on the IoT VLAN

**What:** Only known devices (Station-485, 2x CYD, TimerCam X) should be able to connect to the IoT VLAN.

**How:**
- Register the MAC address of each ESP32 device (they appear in the serial log during boot or in the router as DHCP clients).
- In pfSense/OPNsense → DHCP → Static Mappings: map MAC → fixed IP for each device.
- Enable MAC filtering on the IoT VLAN access point (if the AP supports it).

```
Station-485:     MAC → 192.168.10.10
CYD master:      MAC → 192.168.10.11
CYD kids:        MAC → 192.168.10.12
TimerCam X:      MAC → 192.168.10.13
```

**Note:** MAC filtering alone is not a strong defense (MACs can be spoofed), but it raises the barrier considerably in a home environment.

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 2.3 IoT VLAN SSID not broadcast

**What:** Not broadcasting the IoT network name reduces passive exposure (war-driving, neighbor scanning).

**How:**
- On the AP: disable "Broadcast SSID" for the IoT network.
- ESP32s connect anyway: `WiFi.begin("ssid_name", "password")` with a hidden SSID works normally.
- Hidden SSID is not a strong defense, but eliminates the obvious target.

**Priority:** 🟢 LOW | **Difficulty:** ⚡ Easy

---

## 3. Layer 3 — Network

### 3.1 Separate IoT VLAN (most important network measure)

**What:** All system ESP32s must live on an isolated VLAN (e.g. VLAN 10, subnet 192.168.10.0/24). This VLAN must NOT have access to the computers/phones network (main VLAN). If an ESP32 is compromised, the attacker is confined to the IoT VLAN.

**How (pfSense/OPNsense):**

```
1. Interfaces → VLANs → Add
   - Parent: LAN interface (e.g. igb0)
   - VLAN Tag: 10
   - Description: IoT

2. Interfaces → Assignments → assign VLAN to an interface (OPT1)
   - Enable interface
   - IPv4 Configuration: Static
   - IPv4 Address: 192.168.10.1/24

3. Services → DHCP Server → OPT1 (IoT)
   - Range: 192.168.10.100 – 192.168.10.200
   - Static mappings for ESP32s (see section 2.2)

4. Firewall → Rules → IoT (OPT1):
   - ALLOW: IoT → Proxmox LXC (port 1883 MQTT, 8086 InfluxDB only if needed)
   - ALLOW: IoT → Internet (for NTP, OTA updates if applicable)
   - BLOCK: IoT → LAN (main network) — explicit block rule
   - BLOCK: IoT → LAN (any other traffic)
```

**The Proxmox LXC can be on the main LAN** with a firewall rule allowing only the necessary ports from the IoT VLAN.

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 3.2 Specific firewall rules per port and origin

**What:** VLANs alone are not enough. Rules must be minimal and explicit.

**Recommended rules (pfSense/OPNsense):**

```
# IoT → LXC (only what the system needs)
PASS  TCP/UDP  192.168.10.0/24 → LXC_IP:1883    # MQTT
PASS  TCP      192.168.10.0/24 → LXC_IP:8086    # InfluxDB (only if TimerCam needs it directly)
PASS  UDP      192.168.10.0/24 → 0.0.0.0:123    # NTP (needed for ESP32 time sync)
PASS  TCP      192.168.10.0/24 → 0.0.0.0:443    # HTTPS (for OTA updates, alternative NTP)
BLOCK any      192.168.10.0/24 → 192.168.1.0/24 # Explicit block to main network
BLOCK any      192.168.10.0/24 → any             # Default block (deny all)

# LAN → LXC (users access Grafana)
PASS  TCP      192.168.1.0/24  → LXC_IP:3000    # Grafana
PASS  TCP      192.168.1.0/24  → LXC_IP:8086    # InfluxDB (optional, admin only)
```

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 3.3 Static IP for the Proxmox LXC

**What:** The LXC must have a fixed IP so firewall rules do not rotate.

**How:**
- In Proxmox: Network → Edit → IPv4/CIDR: 192.168.1.50/24 (or whichever IP you use).
- Alternatively in pfSense: DHCP Static Mapping by LXC MAC.
- Update all references in Mosquitto configs, ESP32 firmware, and Telegram bot.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 3.4 Disable ICMP ping on IoT VLAN toward LAN

**What:** Prevents a compromised ESP32 from doing reconnaissance of the main network.

**How:**
```
pfSense → Firewall → Rules → IoT
BLOCK ICMP  192.168.10.0/24 → 192.168.1.0/24
```

**Priority:** 🟢 LOW | **Difficulty:** ⚡ Easy

---

## 4. Layer 4 — Transport

### 4.1 TLS for MQTT (MQTTS on port 8883)

**What:** By default, Mosquitto on port 1883 transmits everything in plain text. MQTT credentials, sensor data, and pump commands are visible on the WiFi network with any sniffer.

**How — Generate CA and certificates:**

```bash
# On the LXC — create certs directory
mkdir -p /etc/mosquitto/certs && cd /etc/mosquitto/certs

# 1. Create private CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=SniperStation-CA/O=Home/C=US"

# 2. Certificate for Mosquitto broker
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/CN=192.168.1.50/O=SniperStation/C=US"
openssl x509 -req -days 3650 -in server.csr -CA ca.crt \
  -CAkey ca.key -CAcreateserial -out server.crt

# 3. Permissions
chmod 640 server.key ca.key
chown mosquitto:mosquitto server.key ca.key server.crt ca.crt
```

**Mosquitto config (`/etc/mosquitto/mosquitto.conf`):**
```
listener 8883
cafile   /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile  /etc/mosquitto/certs/server.key
tls_version tlsv1.2
require_certificate false   # ESP32s use username/password auth
allow_anonymous false
password_file /etc/mosquitto/passwd
```

**In ESP32 firmware (Arduino):**
```cpp
// Include the CA certificate in the code
// ca.crt → convert to array with: xxd -i ca.crt > ca_cert.h
#include "ca_cert.h"
WiFiClientSecure espClient;
espClient.setCACert(ca_cert);  // Verifies the broker
PubSubClient mqttClient(espClient);
mqttClient.setServer("192.168.1.50", 8883);
```

**Important note:** ESP32s have RAM limitations for TLS. Use `espClient.setInsecure()` during development and switch to `setCACert()` in production. If memory is an issue, use `espClient.setInsecure()` only if the network is completely isolated in a VLAN with strong firewall.

**Priority:** 🔴 HIGH | **Difficulty:** 🛠️ Hard

---

### 4.2 HTTPS for photo endpoint (TimerCam X)

**What:** TimerCam X does HTTP POST to upload photos. In plain text, anyone on the network can intercept the photos.

**How:**
- Create an HTTPS endpoint with nginx as a reverse proxy + self-signed certificate (or Let's Encrypt if the LXC has a domain).
- TimerCam X (ESP32 with M5Stack firmware) supports `WiFiClientSecure` for HTTPS.

**nginx config on LXC:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/sniperstation/server.crt;
    ssl_certificate_key /etc/ssl/sniperstation/server.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location /upload {
        proxy_pass http://127.0.0.1:5000/upload;
        client_max_body_size 10M;
    }
}
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 4.3 InfluxDB over HTTPS

**What:** If Grafana or any client accesses InfluxDB, it must do so over HTTPS (port 8086 with TLS).

**How (InfluxDB 2.x):**
```bash
# InfluxDB 2.x supports native TLS
# /etc/influxdb/config.toml:
[tls]
  cert = "/etc/influxdb/certs/server.crt"
  key  = "/etc/influxdb/certs/server.key"
```

In Grafana, update the datasource:
- URL: `https://localhost:8086`
- Check "Skip TLS Verify" only if using a self-signed certificate without CA installed in Grafana.

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 4.4 Grafana over HTTPS (nginx reverse proxy)

**What:** Grafana on port 3000 serves HTTP by default. Accessing from LAN or internet exposes sessions and credentials.

**How:**
```nginx
# /etc/nginx/sites-available/grafana
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/sniperstation/server.crt;
    ssl_certificate_key /etc/ssl/sniperstation/server.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_session_cache   shared:SSL:10m;

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
    }
}
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

## 5. Layer 5 — Session

### 5.1 Grafana session expiration time

**What:** If someone uses Grafana from a public phone or leaves the session open, the token must expire.

**How (`/etc/grafana/grafana.ini`):**
```ini
[auth]
login_maximum_inactive_lifetime_duration = 7d
login_maximum_lifetime_duration = 30d
token_rotation_interval_minutes = 10
```

**Priority:** 🟢 LOW | **Difficulty:** ⚡ Easy

---

### 5.2 Rate limiting on photo HTTP endpoint (TimerCam X)

**What:** The endpoint receiving HTTP POSTs from TimerCam must have rate limiting to prevent abuse (photo flood, DoS).

**How (nginx):**
```nginx
# In the http {} block of nginx.conf
limit_req_zone $binary_remote_addr zone=timercam:1m rate=10r/m;

# In the endpoint location
location /upload {
    limit_req zone=timercam burst=5 nodelay;
    # ... rest of config
}
```

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 5.3 Disable remote access to Proxmox web UI from internet

**What:** The Proxmox web panel (port 8006) must not be accessible from the internet.

**How:**
- On the router: do not port-forward 8006.
- If you need remote access: use VPN (WireGuard in pfSense/OPNsense) and access only through VPN.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

## 6. Layer 7 — Application

### 6.1 Disable anonymous access in Mosquitto

**What:** By default Mosquitto may accept connections without username/password.

**How:**
```bash
# Create a user for each device
mosquitto_passwd -c /etc/mosquitto/passwd station485
mosquitto_passwd -b /etc/mosquitto/passwd cyd_master <password>
mosquitto_passwd -b /etc/mosquitto/passwd cyd_kids <password>
mosquitto_passwd -b /etc/mosquitto/passwd timercam <password>
mosquitto_passwd -b /etc/mosquitto/passwd telegraf_bridge <password>
mosquitto_passwd -b /etc/mosquitto/passwd telegram_bot <password>
```

In `/etc/mosquitto/mosquitto.conf`:
```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Restart: `systemctl restart mosquitto`

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 6.2 MQTT ACLs — topic control per client

**What:** Each device should only be able to publish/subscribe to its own topics. Station-485 should not publish to indoor topics, and Telegram Bot should not publish to sensor topics.

**How — Create `/etc/mosquitto/acl`:**

```
# station485 — publishes exterior sensors, receives pump commands
user station485
topic write sniperstation/exterior/#
topic write sniperstation/sucufer/#
topic write sniperstation/sucurod/#
topic write sniperstation/agua/#
topic write sniperstation/sistema/#
topic write sniperstation/alertas
topic read  sniperstation/sucufer/bomba/set
topic read  sniperstation/sucurod/bomba/set

# cyd_master — publishes indoor master, reads all sensors for display
user cyd_master
topic write sniperstation/interior/master/#
topic read  sniperstation/#

# cyd_kids — same as master but for kids bedroom
user cyd_kids
topic write sniperstation/interior/kids/#
topic read  sniperstation/#

# timercam — only publishes capture event
user timercam
topic write sniperstation/camaras/sucufer/captura

# telegram_bot — reads alerts, sends pump commands
user telegram_bot
topic read  sniperstation/alertas
topic read  sniperstation/#
topic write sniperstation/sucufer/bomba/set
topic write sniperstation/sucurod/bomba/set

# telegraf_bridge — reads everything to write to InfluxDB
user telegraf_bridge
topic read  sniperstation/#
```

In `mosquitto.conf`:
```
acl_file /etc/mosquitto/acl
```

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 6.3 InfluxDB 2.x authentication with tokens

**What:** InfluxDB 2.x uses tokens instead of username/password. Each service that writes or reads must have its own token with minimal permissions.

**How:**
```bash
# Create write-only token for Telegraf/MQTT bridge
influx auth create \
  --org sniperstation \
  --write-bucket sniperstation \
  --description "telegraf-write-only"

# Create read-only token for Grafana
influx auth create \
  --org sniperstation \
  --read-bucket sniperstation \
  --description "grafana-read-only"

# List tokens
influx auth list
```

- Telegraf/bridge → use the write token.
- Grafana datasource → use the read token.
- **Never** use the admin token (All Access) in services.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 6.4 Grafana authentication — change admin password and disable default admin

**What:** Grafana installs with `admin:admin`. This is the first credential any attacker tries.

**How:**
```bash
# Change from CLI
grafana-cli admin reset-admin-password "strong_password_here"
```

`/etc/grafana/grafana.ini`:
```ini
[security]
admin_user = sniperstation_admin   # Change admin username
admin_password = <strong_password>
disable_gravatar = true

[users]
allow_sign_up = false
allow_org_create = false

[auth.anonymous]
enabled = false
```

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 6.5 HTTP photo endpoint authentication (TimerCam X)

**What:** The endpoint receiving HTTP POSTs from TimerCam must not be public. It must require authentication.

**How — API key in HTTP header:**

TimerCam X sends the header in the POST:
```
Authorization: Bearer <secret_token>
```

On the server (Python Flask or FastAPI):
```python
API_KEY = os.environ.get("TIMERCAM_API_KEY")

@app.route("/upload", methods=["POST"])
def upload_photo():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {API_KEY}":
        return {"error": "unauthorized"}, 401
    # ... process photo
```

The token is configured in the TimerCam firmware as a constant (see section 12).

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 6.6 Validate pump commands in firmware (input sanitization)

**What:** The topic `sniperstation/sucufer/bomba/set` accepts external commands (from Telegram Bot). If unexpected values are injected, the firmware could activate the pump indefinitely.

**How — in Station-485 firmware:**
```cpp
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Sanitize payload length
    if (length != 1) return;

    char cmd = (char)payload[0];

    if (strcmp(topic, "sniperstation/sucufer/bomba/set") == 0) {
        if (cmd == '1') {
            activatePump(PUMP_SUCU_FER);
        } else if (cmd == '0') {
            deactivatePump(PUMP_SUCU_FER);
        }
        // Any other value is silently dropped
    }
}

// Safety watchdog: force-stop pump after MAX_PUMP_DURATION_MS
#define MAX_PUMP_DURATION_MS 60000  // 60 seconds absolute max
```

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

## 7. Authentication and Authorization

### 7.1 Credentials summary per service

| Service | Mechanism | Users to create |
|---------|-----------|-----------------|
| Mosquitto | username/password + ACL | station485, cyd_master, cyd_kids, timercam, telegraf_bridge, telegram_bot |
| InfluxDB 2.x | Tokens with minimal permissions | Write token (Telegraf), Read token (Grafana) |
| Grafana | username/password | admin (renamed), optional reader without write access |
| Photo HTTP endpoint | API key in Bearer header | timercam (1 token) |
| Proxmox | username/password + 2FA | LAN/VPN access only |

### 7.2 Enable 2FA in Grafana

**What:** If Grafana is accessible from the internet or shared devices, a second factor prevents access with a stolen password.

**How:**
```ini
# /etc/grafana/grafana.ini
[auth]
disable_login_form = false

[auth.basic]
enabled = true
```

Then in the Grafana UI user profile: enable TOTP (Google Authenticator / Authy).

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 7.3 Telegram bot token — protect against unauthorized use

**What:** The Telegram bot token allows anyone to send commands if they obtain it.

**How:**
- Restrict the bot to only accept messages from your personal `chat_id`:

```python
AUTHORIZED_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID"))

def handle_message(update, context):
    if update.message.chat_id != AUTHORIZED_CHAT_ID:
        update.message.reply_text("Unauthorized")
        return
    # ... process command
```

- For commands from multiple people (family), use a list: `AUTHORIZED_IDS = [id1, id2]`.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

## 8. Encryption in Transit

### 8.1 Encryption summary per protocol

| Protocol | Current state | Target |
|----------|--------------|--------|
| MQTT (ESP32 → broker) | Plaintext :1883 | MQTTS :8883 with TLS 1.2+ |
| HTTP POST (TimerCam → LXC) | Plaintext | HTTPS with self-signed cert |
| InfluxDB (Telegraf → DB) | Plaintext | HTTPS with TLS |
| Grafana (browser → LXC) | HTTP | HTTPS via nginx reverse proxy |
| Telegram Bot API | Already HTTPS | Maintain |

### 8.2 Centralized self-signed certificate generation

For a home system, an own CA (see section 4.1) is sufficient. All services can share the same server cert/key pair, or have individual certificates.

**Script to generate all certs at once:**

```bash
#!/bin/bash
# Run as root on the LXC
CERTS_DIR="/etc/sniperstation/certs"
mkdir -p "$CERTS_DIR"
cd "$CERTS_DIR"

# CA
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=SniperStation-CA/O=Home/C=US"

# Server cert (used by Mosquitto, nginx, InfluxDB)
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/CN=192.168.1.50/O=SniperStation/C=US"
openssl x509 -req -days 3650 -in server.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

echo "Certificates generated in $CERTS_DIR"
echo "CA fingerprint (embed in ESP32 firmware):"
openssl x509 -in ca.crt -fingerprint -noout
```

**Priority:** 🔴 HIGH | **Difficulty:** 🛠️ Hard (firmware changes)

---

## 9. Encryption at Rest

### 9.1 InfluxDB volume encryption with LUKS

**What:** InfluxDB data (sensor time series, photo metadata) is stored in plain text on the LXC filesystem. If someone gains access to the Proxmox host, they can read everything.

**How:**
- Create a LUKS-encrypted virtual disk for the InfluxDB data volume.
- This requires the LXC to have access to `/dev/mapper` (in Proxmox, the LXC must be "privileged" type or with special configuration).

```bash
# On Proxmox host — create encrypted disk
dd if=/dev/zero of=/var/lib/vz/images/influxdb-encrypted.raw bs=1G count=10
losetup /dev/loop10 /var/lib/vz/images/influxdb-encrypted.raw
cryptsetup luksFormat /dev/loop10
cryptsetup luksOpen /dev/loop10 influxdb_data
mkfs.ext4 /dev/mapper/influxdb_data
mount /dev/mapper/influxdb_data /var/lib/influxdb
```

**Simpler alternative:** Encrypt the entire LXC volume at the Proxmox storage level (ZFS with encryption or using a LUKS disk as PVE storage).

**Priority:** 🟢 LOW (home network, not HIPAA/PCI) | **Difficulty:** 🛠️ Hard

---

### 9.2 Do not store credentials in plain text on the filesystem

**What:** Mosquitto passwords, InfluxDB tokens, and Telegram bot token must not be in config files in plain text without restrictive permissions.

**How:**
```bash
# Correct permissions for sensitive files
chmod 600 /etc/mosquitto/passwd
chmod 600 /etc/mosquitto/acl
chmod 640 /etc/mosquitto/certs/ca.key
chmod 640 /etc/mosquitto/certs/server.key
chown root:mosquitto /etc/mosquitto/passwd

# Environment variables for the Telegram bot
# Create /etc/sniperstation/secrets.env (not in git repo)
chmod 600 /etc/sniperstation/secrets.env
chown root:root /etc/sniperstation/secrets.env
```

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 9.3 TimerCam photos — directory permissions

**What:** The directory where succulent photos are stored must have correct permissions.

**How:**
```bash
mkdir -p /var/sniperstation/photos
chown www-data:www-data /var/sniperstation/photos  # or the Python process user
chmod 750 /var/sniperstation/photos
```

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

## 10. ESP32 Firmware Security

### 10.1 Do not hardcode credentials in source code

**What:** The most common and dangerous pattern: putting WiFi password, MQTT password, and API tokens directly in the `.ino` or `.cpp`. If the repo is public (GitHub), the credentials are public.

**How — use a local unversioned config file:**

Create `firmware/station485/secrets.h` (in `.gitignore`):
```cpp
// secrets.h — NOT committed to git
#define WIFI_SSID     "iot_network_name"
#define WIFI_PASSWORD "wifi_password"
#define MQTT_HOST     "192.168.1.50"
#define MQTT_PORT     8883
#define MQTT_USER     "station485"
#define MQTT_PASSWORD "mqtt_station_password"
```

In the main `.ino`:
```cpp
#include "secrets.h"
// Use WIFI_SSID, WIFI_PASSWORD, etc.
```

In `.gitignore`:
```
firmware/station485/secrets.h
firmware/cyd_indoor/secrets.h
firmware/timercam/secrets.h
```

Provide a `secrets.h.example` with placeholder values so others know what variables are needed.

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 10.2 Use ESP32 NVS (Non-Volatile Storage) for credentials

**What:** An improvement over `secrets.h` is storing credentials in the ESP32's NVS partition, which is separate from code flash and can be protected. This allows changing credentials without recompiling firmware.

**How:**
```cpp
#include <Preferences.h>

Preferences prefs;

void loadCredentials() {
    prefs.begin("secrets", true);  // Read-only namespace
    String ssid = prefs.getString("wifi_ssid", "");
    String wpass = prefs.getString("wifi_pass", "");
    String mqttUser = prefs.getString("mqtt_user", "");
    String mqttPass = prefs.getString("mqtt_pass", "");
    prefs.end();
}

// To write credentials initially (only once, from serial):
void writeCredentials() {
    prefs.begin("secrets", false);  // Read-write
    prefs.putString("wifi_ssid", "network_name");
    prefs.putString("wifi_pass", "password");
    prefs.putString("mqtt_user", "station485");
    prefs.putString("mqtt_pass", "mqtt_password");
    prefs.end();
}
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 10.3 Enable Flash Encryption on ESP32

**What:** The ESP32 has native support for encrypting flash content with AES-256. Without this, connecting the ESP32 to a USB programmer allows reading the full firmware (and any hardcoded credentials).

**How (Arduino IDE + esptool):**
```bash
# Enable flash encryption during flashing
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash_encrypt \
  --flash_mode dio --flash_freq 40m --flash_size detect \
  0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 firmware.bin

# Verify flash encryption status
esptool.py --chip esp32 --port /dev/ttyUSB0 get_security_info
```

**Warning:** Once flash encryption is enabled in "Release" mode, the ESP32 CANNOT be re-programmed via UART. It can only be updated via OTA. Use "Development" mode for testing.

**Priority:** 🟡 MEDIUM | **Difficulty:** 🛠️ Hard

---

### 10.4 Secure OTA (Over-The-Air) updates

**What:** ESP32s must be updatable without physical access. Without OTA security, an attacker on the network could inject malicious firmware.

**How (ArduinoOTA with password):**
```cpp
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setPassword("secret_ota_password");
    ArduinoOTA.setHostname("station485");

    ArduinoOTA.onStart([]() {
        Serial.println("OTA update starting");
    });

    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA Error[%u]\n", error);
    });

    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();
    // ... rest of loop
}
```

**For OTA from own server (more secure than mDNS):**
```cpp
#include <HTTPUpdate.h>

void checkOTAUpdate() {
    WiFiClientSecure client;
    client.setCACert(ca_cert);  // Verify the OTA server
    t_httpUpdate_return ret = httpUpdate.update(
        client,
        "https://192.168.1.50/ota/station485.bin",
        CURRENT_FIRMWARE_VERSION
    );
}
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 10.5 Watchdog timer enabled

**What:** Not strictly security, but a hung ESP32 that is not responding can leave the pump active indefinitely.

**How:**
```cpp
#include <esp_task_wdt.h>

void setup() {
    // 30-second watchdog — if loop does not reset it, ESP32 restarts
    esp_task_wdt_init(30, true);
    esp_task_wdt_add(NULL);
}

void loop() {
    esp_task_wdt_reset();  // Reset watchdog at start of each cycle

    // Safety: never leave pump active longer than MAX_PUMP_DURATION_MS
    // (see section 6.6)
}
```

**Priority:** 🔴 HIGH (plant operational safety) | **Difficulty:** ⚡ Easy

---

## 11. Network Segmentation — IoT VLAN

### 11.1 Recommended network architecture

```
[Internet]
     │
  [ISP Router/Modem]
     │
  [pfSense/OPNsense]
     ├── LAN (VLAN 1) — 192.168.1.0/24
     │   ├── Computers, phones
     │   ├── Proxmox LXC (192.168.1.50)
     │   └── NAS, printers
     │
     ├── IoT VLAN (VLAN 10) — 192.168.10.0/24
     │   ├── Station-485     → 192.168.10.10
     │   ├── CYD master      → 192.168.10.11
     │   ├── CYD kids        → 192.168.10.12
     │   └── TimerCam X      → 192.168.10.13
     │
     └── [Access Point with multiple SSIDs]
         ├── "HomeNetwork"    → VLAN 1
         └── "HomeIoT"        → VLAN 10 (hidden, WPA2)
```

### 11.2 Complete firewall rules

**Rules on IoT VLAN (OPT1) — "deny all, permit by exception" policy:**

```
# pfSense/OPNsense — Rules → IoT Interface (OPT1)
# Order matters — evaluated top to bottom

Rule 1: PASS  UDP  IoT:any → 192.168.1.50:1883   (MQTT plaintext — temporary)
Rule 2: PASS  TCP  IoT:any → 192.168.1.50:8883   (MQTTS)
Rule 3: PASS  TCP  IoT:any → 192.168.1.50:443    (HTTPS photos TimerCam)
Rule 4: PASS  UDP  IoT:any → 0.0.0.0:123         (NTP)
Rule 5: PASS  TCP  IoT:any → 0.0.0.0:443         (HTTPS for OTA updates)
Rule 6: BLOCK any  IoT:any → 192.168.1.0/24      (total block to LAN)
Rule 7: BLOCK any  IoT:any → any                  (deny all default)
```

**Notes:**
- Remove Rule 1 once MQTTS is working.
- Rule 5 (HTTPS to internet) is needed for OTA and HTTPS NTP sync. Remove if not using OTA.

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 11.3 Separate DNS for IoT VLAN

**What:** Using own DNS on IoT VLAN prevents IoT devices from resolving tracking domains or being victims of DNS poisoning.

**How (pfSense):**
- In IoT VLAN DHCP, set DNS server = 192.168.1.1 (pfSense itself with DNS Resolver).
- Block external DNS queries from IoT VLAN (port 53 UDP/TCP only to pfSense):
  ```
  PASS UDP IoT:any → pfSense_IoT_IP:53
  BLOCK UDP IoT:any → any:53
  ```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

## 12. Secrets Management

### 12.1 Complete system secrets list

| Secret | Used by | Recommended storage |
|--------|---------|---------------------|
| WiFi SSID + password (IoT VLAN) | All ESP32s | secrets.h (not in git) + NVS |
| MQTT password (station485) | Station-485 firmware | secrets.h + NVS |
| MQTT password (cyd_master) | CYD master firmware | secrets.h + NVS |
| MQTT password (cyd_kids) | CYD kids firmware | secrets.h + NVS |
| MQTT password (timercam) | TimerCam firmware | secrets.h + NVS |
| MQTT password (telegram_bot) | Python bot | Environment variable / secrets.env |
| MQTT password (telegraf_bridge) | Telegraf | Environment variable / secrets.env |
| InfluxDB write token | Telegraf | Environment variable |
| InfluxDB read token | Grafana | Grafana datasource config |
| Telegram Bot token | Python bot | Environment variable |
| Authorized Telegram Chat ID | Python bot | Environment variable |
| TimerCam API key (HTTP upload) | TimerCam + server | secrets.h + env var |
| OTA password | ESP32 + OTA client | secrets.h |
| Grafana admin password | Grafana | grafana.ini (perms 640) |
| Proxmox root password | Admin | Password manager (Bitwarden) |

### 12.2 Secrets structure on the LXC

```bash
# /etc/sniperstation/secrets.env
# chmod 600, chown root:root
MQTT_PASSWORD_TELEGRAF=<password>
INFLUXDB_TOKEN_WRITE=<token>
INFLUXDB_TOKEN_READ=<token>
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_CHAT_ID=<chat_id>
TIMERCAM_API_KEY=<api_key>
```

Load in services:
```bash
# systemd service file for Telegram bot
[Service]
EnvironmentFile=/etc/sniperstation/secrets.env
ExecStart=/usr/bin/python3 /opt/sniperstation/telegram_bot/bot.py
```

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

### 12.3 Periodic credential rotation

**What:** MQTT passwords and InfluxDB tokens must be rotated if compromise is suspected or periodically (every 6–12 months).

**MQTT rotation procedure:**
```bash
# 1. Generate new password
mosquitto_passwd -b /etc/mosquitto/passwd station485 <new_password>

# 2. Update secrets.h in firmware
# 3. Re-flash the affected ESP32 (or via OTA)
# 4. Verify it reconnects correctly
# 5. Restart Mosquitto if needed
systemctl reload mosquitto
```

**Priority:** 🟢 LOW | **Difficulty:** 🔧 Medium

---

### 12.4 Add secrets.h to .gitignore (verification)

```bash
# Verify the repo .gitignore covers secrets files
cat /home/claude/sniperstation/.gitignore
```

Add if missing:
```gitignore
# Secrets — never commit
firmware/station485/secrets.h
firmware/cyd_indoor/secrets.h
firmware/timercam/secrets.h
software/telegram_bot/.env
software/mosquitto/passwd
*.key
*.pem
secrets.env
```

**Priority:** 🔴 HIGH | **Difficulty:** ⚡ Easy

---

## 13. Security Monitoring and Alerts

### 13.1 Logging failed MQTT connections

**What:** Detect access attempts to the broker with incorrect credentials.

**How — Mosquitto log:**
```
# /etc/mosquitto/mosquitto.conf
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
connection_messages true
log_timestamp true
```

Then monitor with `tail -f /var/log/mosquitto/mosquitto.log` or configure `fail2ban`.

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 13.2 Fail2ban for Mosquitto and Grafana

**What:** Block IPs that make multiple failed authentication attempts.

**How:**
```bash
apt install -y fail2ban

# /etc/fail2ban/jail.local
[mosquitto]
enabled  = true
port     = 1883,8883
filter   = mosquitto
logpath  = /var/log/mosquitto/mosquitto.log
maxretry = 5
bantime  = 3600
findtime = 600

[grafana]
enabled  = true
port     = 3000,443
filter   = grafana
logpath  = /var/log/grafana/grafana.log
maxretry = 5
bantime  = 3600
```

Create filter `/etc/fail2ban/filter.d/mosquitto.conf`:
```ini
[Definition]
failregex = .* Client .* failed to connect: not authorised
            .* bad user name or password
ignoreregex =
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 13.3 Telegram alert when an ESP32 unexpectedly disconnects

**What:** If a device stops publishing to MQTT, it may indicate a normal disconnection (restart) or a security event (physical tampering, WiFi jam).

**How — MQTT Last Will and Testament (LWT):**

In the firmware of each ESP32:
```cpp
// Configure LWT before connecting to the broker
mqttClient.setWill(
    "sniperstation/sistema/lwt",  // topic
    "offline",                     // payload
    false,                         // retain
    1                              // QoS
);

// On successful connection, publish online
mqttClient.publish("sniperstation/sistema/lwt", "online");
```

In the Telegram bot:
```python
def on_lwt_message(client, userdata, msg):
    device = msg.topic.split("/")[2]
    if msg.payload.decode() == "offline":
        send_telegram_alert(f"ALERT: {device} disconnected from MQTT broker")
```

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 13.4 Telegram alert on unexpected topic publication

**What:** If someone compromises a device and starts publishing to topics that don't correspond (e.g. station485 publishing to indoor topics), the bot should alert.

**How:**
```python
EXPECTED_PUBLISHERS = {
    "sniperstation/exterior/+": "station485",
    "sniperstation/sucufer/+": "station485",
    "sniperstation/sucurod/+": "station485",
    "sniperstation/interior/master/+": "cyd_master",
    "sniperstation/interior/kids/+": "cyd_kids",
    "sniperstation/camaras/sucufer/+": "timercam",
}
# Monitor with client_id in message and compare with expected publisher
```

**Note:** Mosquitto does not expose the client_id in the payload by default. This requires a custom implementation in the broker or a bridge that enriches the messages.

**Priority:** 🟢 LOW | **Difficulty:** 🛠️ Hard

---

### 13.5 Security panel in Grafana

**What:** Dashboard dedicated to operational security metrics.

**Suggested panels:**
- Last connection timestamp for each ESP32 (detect silent devices).
- MQTT reconnect counter per device per hour.
- Messages received per topic graph (volume anomalies).
- Water level status (alert if empty > 6h without intervention).
- Pump activation history (detect unexpected activations).

**Priority:** 🟡 MEDIUM | **Difficulty:** 🔧 Medium

---

### 13.6 Periodic MQTT broker audit

**How:**
```bash
# See currently connected clients
mosquitto_sub -h localhost -u admin -P password \
  -t '$SYS/broker/clients/connected' -C 1

# See all active topics
mosquitto_sub -h localhost -u admin -P password \
  -t '$SYS/#' -v -C 20

# Count messages per topic
mosquitto_sub -h localhost -u admin -P password \
  -t 'sniperstation/#' -v --retained-only
```

**Priority:** 🟢 LOW | **Difficulty:** ⚡ Easy

---

## 14. Physical Security

### 14.1 Outdoor enclosure protection against extreme heat

**Security context:** Orlando in summer can bring the inside of a closed box to >70°C. Station-485 has a 60°C limit. An ESP32 in thermal shutdown can leave the pump active (if the relay pin stays HIGH), risking plant damage.

**Measures:**
- Enclosure in permanent shade (never direct sun).
- Passive ventilation: 10mm holes with mesh at the bottom (intake) and top (exhaust), with rain cover "mushroom vent" style.
- If temperature > 45°C sustained: add the 5V SunFounder fan from inventory with thermistor control (available in the kit).
- Firmware must have: if `internal_box_temp > 58°C`, shut off relays and send Telegram alert.

**Priority:** 🔴 HIGH | **Difficulty:** 🔧 Medium

---

### 14.2 Protection against pump cable sabotage

**What:** The 12V cables going to the pumps are accessible from outside the enclosure. Someone could cut them.

**Measures:**
- Use cable with braided steel cover (bicycle cable type) between enclosure and pumps.
- Cables exiting the enclosure should exit at the bottom to make access harder.
- Firmware detects soil moisture sensor error and alerts if an activated pump produces no humidity change in 5 minutes.

**Priority:** 🟢 LOW | **Difficulty:** ⚡ Easy

---

### 14.3 Hardware inventory and labeling

**What:** Document all devices for quick detection of unauthorized hardware connected to the network.

**How:**
- Photograph and record the MAC address of each ESP32 before installing it.
- Physically label each device with its hostname (station485, cyd_master, etc.).
- Keep an updated list in this repository (`hardware/inventory.md`).
- Periodically review the router DHCP client table to detect unrecognized devices on the IoT VLAN.

**Priority:** 🟡 MEDIUM | **Difficulty:** ⚡ Easy

---

### 14.4 UPS or backup battery for the LXC

**What:** A power interruption while the pump is active can leave the relay in an indeterminate state. If the LXC (Mosquitto) goes down, ESP32s lose MQTT connectivity.

**Firmware measures (without UPS):**
- Use NVS to store pump state (active/inactive) with timestamp.
- On restart, if stored state is "active" and more than 2 minutes have passed, assume failure and force relay deactivation.

```cpp
void setup() {
    prefs.begin("state", false);
    bool pump1WasActive = prefs.getBool("pump1_active", false);
    ulong lastActive = prefs.getULong("pump1_ts", 0);

    if (pump1WasActive && (millis() - lastActive > 120000)) {
        digitalWrite(RELAY_PUMP1, LOW);  // Force off
        prefs.putBool("pump1_active", false);
        // Send MQTT alert when connected
    }
    prefs.end();
}
```

**Priority:** 🔴 HIGH (plant safety) | **Difficulty:** 🔧 Medium

---

## Implementation Checklist

### HIGH Priority — Before going to production

- [ ] Change Grafana admin password (do not use admin:admin)
- [ ] Disable anonymous in Mosquitto + create one user per device
- [ ] Add `secrets.h` to `.gitignore` before first firmware commit
- [ ] Configure MQTT ACLs per user
- [ ] Create InfluxDB tokens with minimal permissions (separate write and read)
- [ ] Telegram bot chat_id restriction
- [ ] Implement authentication on the photo HTTP endpoint (TimerCam)
- [ ] Create IoT VLAN in pfSense/OPNsense with LAN block rules
- [ ] Static IP for the LXC
- [ ] Watchdog timer on all ESP32s
- [ ] Firmware relay force-off: absolute pump duration limit
- [ ] Disable WPS on the router
- [ ] Proxmox web UI not accessible from internet (no port forwarding)
- [ ] Permissions 600 on LXC secrets files

### MEDIUM Priority — First week

- [ ] Implement MQTTS (port 8883, TLS 1.2)
- [ ] HTTPS for photo endpoint (TimerCam)
- [ ] nginx reverse proxy with TLS for Grafana
- [ ] InfluxDB with TLS enabled
- [ ] Fail2ban for Mosquitto and Grafana
- [ ] Logging enabled in Mosquitto
- [ ] LWT configured on all ESP32s + Telegram alert on disconnection
- [ ] MAC filtering on IoT VLAN
- [ ] Separate DNS for IoT VLAN
- [ ] Credentials in NVS instead of compiled secrets.h
- [ ] OTA with password on all ESP32s
- [ ] 2FA in Grafana
- [ ] Security panel in Grafana

### LOW Priority — Additional hardening

- [ ] Flash encryption on ESP32
- [ ] IoT VLAN SSID hidden
- [ ] LUKS for InfluxDB volume
- [ ] Periodic credential rotation (every 6 months)
- [ ] Cable glands + outdoor enclosure sealing
- [ ] Torx security screws on outdoor enclosure
- [ ] Hardware inventory documented with MACs
- [ ] Anomalous MQTT topic monitoring

---

*Document generated: 2026-03-26*
*Architecture: M5Stack Station-485 + 2x CYD ESP32 + TimerCam X + Proxmox LXC (Mosquitto + InfluxDB + Grafana + Telegram Bot)*
*Network: Orlando, Florida — home network with pfSense/OPNsense*
