# SniperStation — Guía de Hardening de Seguridad

> Documento de referencia para asegurar el stack completo del sistema SniperStation.
> Aplica a: M5Stack Station-485, CYD ESP32-2432S028 (x2), M5Stack TimerCam X, Proxmox LXC (Mosquitto, InfluxDB, Grafana, Telegram Bot).
> Red doméstica — Orlando, Florida.

---

## Índice

1. [Capa 1 — Física](#1-capa-1--física)
2. [Capa 2 — Enlace de Datos](#2-capa-2--enlace-de-datos)
3. [Capa 3 — Red](#3-capa-3--red)
4. [Capa 4 — Transporte](#4-capa-4--transporte)
5. [Capa 5 — Sesión](#5-capa-5--sesión)
6. [Capa 7 — Aplicación](#6-capa-7--aplicación)
7. [Autenticación y Autorización](#7-autenticación-y-autorización)
8. [Cifrado en Tránsito](#8-cifrado-en-tránsito)
9. [Cifrado en Reposo](#9-cifrado-en-reposo)
10. [Seguridad del Firmware ESP32](#10-seguridad-del-firmware-esp32)
11. [Segmentación de Red — IoT VLAN](#11-segmentación-de-red--iot-vlan)
12. [Gestión de Secretos](#12-gestión-de-secretos)
13. [Monitoreo y Alertas de Seguridad](#13-monitoreo-y-alertas-de-seguridad)
14. [Seguridad Física](#14-seguridad-física)

---

## Convenciones

| Ícono | Prioridad |
|-------|-----------|
| 🔴 | **ALTA** — riesgo real, implementar antes de poner el sistema en producción |
| 🟡 | **MEDIA** — mejora significativa de postura, implementar en primera semana |
| 🟢 | **BAJA** — hardening adicional, buena práctica |

| Símbolo | Dificultad |
|---------|-----------|
| ⚡ | Fácil — menos de 30 min, sin conocimiento previo especializado |
| 🔧 | Media — requiere editar configs o compilar firmware |
| 🛠️ | Difícil — cambios de arquitectura, certificados TLS, NVS flash |

---

## 1. Capa 1 — Física

### 1.1 Enclosure weatherproof con cierre con llave

**Qué:** El Station-485 está afuera en Orlando. Cualquiera que pueda tocarlo físicamente puede resetearlo, leer las credenciales WiFi si el firmware no está protegido, o simplemente destruirlo.

**Cómo:**
- Usar caja IP65 o superior con tornillos de seguridad (Torx o hexalobe) en vez de Phillips estándar.
- Si el presupuesto lo permite: caja con candado.
- Montar la caja a una altura mínima de 1.8m sobre el suelo, o en ubicación no obvia.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 1.2 Protección del botón de reset del ESP32

**Qué:** El botón EN (reset) del Station-485 y los CYD expuesto permite un reset físico que puede interrumpir el riego o borrar el estado de la SRAM.

**Cómo:**
- En el enclosure exterior: cubrir o bloquear mecánicamente el acceso al botón EN con un tope de plástico impreso en 3D.
- Para los CYD indoor: los enclosures custom 3D deben dejar expuesto solo la pantalla, sin acceso al botón EN.

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 1.3 Cable management sellado

**Qué:** Los cables que salen del enclosure exterior (Grove sensors, relay, 12V) son puntos de entrada de agua y vectores de manipulación física.

**Cómo:**
- Usar prensaestopas PG7 o PG9 (cable glands) para cada cable que atraviese la caja.
- Sellar con silicona neutra (no acética) alrededor de los prensaestopas una vez instalados.
- Usar cable conduit corrugado entre la caja y los materos para los cables de bomba.

**Prioridad:** 🔴 ALTA (Orlando lluvia intensa) | **Dificultad:** ⚡ Fácil

---

### 1.4 Protección contra robo del hardware

**Qué:** La TimerCam X está afuera sin enclosure y podría ser sustraída.

**Cómo:**
- Montar la cámara con tornillos desde adentro (no accesibles desde afuera).
- Usar cable de seguridad tipo Kensington si se monta en superficie plana.
- Documentar el número de serie de cada ESP32 y M5Stack para reclamación de seguro si aplica.

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

## 2. Capa 2 — Enlace de Datos

### 2.1 Desactivar WPS en el router

**Qué:** WPS (WiFi Protected Setup) tiene vulnerabilidades conocidas (ataque Pixie Dust, brute force PIN) que permiten obtener la clave WiFi sin conocerla. Si los ESP32 están en la red principal, comprometer WPS comprometer todo.

**Cómo:**
- Acceder al panel del router (192.168.1.1 o similar).
- Buscar la sección "Wireless" o "Advanced Wireless Settings".
- Desactivar "WPS" / "Wi-Fi Protected Setup" completamente.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 2.2 Filtrado MAC en la VLAN IoT

**Qué:** Solo los dispositivos conocidos (Station-485, 2x CYD, TimerCam X) deben poder conectarse a la VLAN IoT.

**Cómo:**
- Registrar las MAC addresses de cada dispositivo ESP32 (aparecen en el log serial durante el boot o en el router como clientes DHCP).
- En pfSense/OPNsense → DHCP → Static Mappings: mapear MAC → IP fija para cada dispositivo.
- Habilitar filtrado MAC en el access point de la VLAN IoT (si el AP lo soporta).

```
Station-485:     MAC → 192.168.10.10
CYD master:      MAC → 192.168.10.11
CYD kids:        MAC → 192.168.10.12
TimerCam X:      MAC → 192.168.10.13
```

**Nota:** El filtrado MAC no es una defensa fuerte por sí sola (las MACs se pueden spoofear), pero eleva la barrera de entrada considerablemente en un entorno doméstico.

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 2.3 SSID de IoT VLAN no broadcast

**Qué:** No difundir el nombre de la red IoT reduce la exposición pasiva (war-driving, escaneos de vecinos).

**Cómo:**
- En el AP: desactivar "Broadcast SSID" para la red IoT.
- Los ESP32 se conectan igual: `WiFi.begin("nombre_ssid", "password")` con el SSID oculto funciona normalmente.
- El SSID oculto no es una defensa fuerte, pero elimina el target obvio.

**Prioridad:** 🟢 BAJA | **Dificultad:** ⚡ Fácil

---

## 3. Capa 3 — Red

### 3.1 VLAN IoT separada (medida más importante de red)

**Qué:** Todos los ESP32 del sistema deben vivir en una VLAN aislada (ej. VLAN 10, subred 192.168.10.0/24). Esta VLAN NO debe tener acceso a la red de computadoras/celulares (VLAN principal). Si un ESP32 es comprometido, el atacante queda confinado a la VLAN IoT.

**Cómo (pfSense/OPNsense):**

```
1. Interfaces → VLANs → Add
   - Parent: interfaz LAN (ej. igb0)
   - VLAN Tag: 10
   - Description: IoT

2. Interfaces → Assignments → asignar la VLAN a una interfaz (OPT1)
   - Enable interface
   - IPv4 Configuration: Static
   - IPv4 Address: 192.168.10.1/24

3. Services → DHCP Server → OPT1 (IoT)
   - Range: 192.168.10.100 – 192.168.10.200
   - Static mappings para los ESP32 (ver sección 2.2)

4. Firewall → Rules → IoT (OPT1):
   - PERMITIR: IoT → Proxmox LXC (puerto 1883 MQTT, 8086 InfluxDB solo si es necesario)
   - PERMITIR: IoT → Internet (para NTP, OTA updates si aplica)
   - BLOQUEAR: IoT → LAN (red principal) — regla explícita de bloqueo
   - BLOQUEAR: IoT → LAN (cualquier otro tráfico)
```

**El Proxmox LXC puede estar en la LAN principal** con una regla de firewall que permita solo los puertos necesarios desde la VLAN IoT.

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 3.2 Reglas de firewall específicas por puerto y origen

**Qué:** No basta con separar VLANs. Las reglas deben ser mínimas y explícitas.

**Reglas recomendadas (pfSense/OPNsense):**

```
# IoT → LXC (solo lo que necesita el sistema)
PASS  TCP/UDP  192.168.10.0/24 → LXC_IP:1883    # MQTT
PASS  TCP      192.168.10.0/24 → LXC_IP:8086    # InfluxDB (solo si TimerCam o algo lo necesita directo)
PASS  UDP      192.168.10.0/24 → 0.0.0.0:123    # NTP (necesario para ESP32 time sync)
PASS  TCP      192.168.10.0/24 → 0.0.0.0:443    # HTTPS (para OTA updates, NTP alternativo)
BLOCK any      192.168.10.0/24 → 192.168.1.0/24 # Bloqueo explícito a red principal
BLOCK any      192.168.10.0/24 → any             # Bloqueo por defecto (deny all)

# LAN → LXC (usuarios acceden a Grafana)
PASS  TCP      192.168.1.0/24  → LXC_IP:3000    # Grafana
PASS  TCP      192.168.1.0/24  → LXC_IP:8086    # InfluxDB (opcional, solo para admin)
```

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 3.3 IP estática para el Proxmox LXC

**Qué:** El LXC debe tener IP fija para que las reglas de firewall no roten.

**Cómo:**
- En Proxmox: Network → Edit → IPv4/CIDR: 192.168.1.50/24 (o la IP que uses).
- Alternativamente en pfSense: DHCP Static Mapping por MAC del LXC.
- Actualizar todas las referencias en configs de Mosquitto, firmware ESP32, y bot de Telegram.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 3.4 Deshabilitar ping ICMP en la VLAN IoT hacia la LAN

**Qué:** Impide que un ESP32 comprometido haga reconnaissance de la red principal.

**Cómo:**
```
pfSense → Firewall → Rules → IoT
BLOCK ICMP  192.168.10.0/24 → 192.168.1.0/24
```

**Prioridad:** 🟢 BAJA | **Dificultad:** ⚡ Fácil

---

## 4. Capa 4 — Transporte

### 4.1 TLS para MQTT (MQTTS en puerto 8883)

**Qué:** Por defecto, Mosquitto en puerto 1883 transmite todo en texto plano. Credenciales MQTT, datos de sensores, y comandos de bomba son visibles en la red WiFi con cualquier sniffer.

**Cómo — Generar CA y certificados:**

```bash
# En el LXC — crear directorio para certs
mkdir -p /etc/mosquitto/certs && cd /etc/mosquitto/certs

# 1. Crear CA privada
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=SniperStation-CA/O=Home/C=US"

# 2. Certificado para el broker Mosquitto
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
  -subj "/CN=192.168.1.50/O=SniperStation/C=US"
openssl x509 -req -days 3650 -in server.csr -CA ca.crt \
  -CAkey ca.key -CAcreateserial -out server.crt

# 3. Permisos
chmod 640 server.key ca.key
chown mosquitto:mosquitto server.key ca.key server.crt ca.crt
```

**Config Mosquitto (`/etc/mosquitto/mosquitto.conf`):**
```
listener 8883
cafile   /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile  /etc/mosquitto/certs/server.key
tls_version tlsv1.2
require_certificate false   # Los ESP32 usan autenticación usuario/password
allow_anonymous false
password_file /etc/mosquitto/passwd
```

**En el firmware ESP32 (Arduino):**
```cpp
// Incluir el certificado CA en el código
// ca.crt → convertir a array con: xxd -i ca.crt > ca_cert.h
#include "ca_cert.h"
WiFiClientSecure espClient;
espClient.setCACert(ca_cert);  // Verifica el broker
PubSubClient mqttClient(espClient);
mqttClient.setServer("192.168.1.50", 8883);
```

**Nota importante:** Los ESP32 tienen limitaciones de memoria RAM para TLS. Usar `espClient.setInsecure()` durante desarrollo y cambiar a `setCACert()` en producción. Si la memoria es un problema, usar `espClient.setInsecure()` solo si la red está completamente aislada en VLAN con firewall fuerte.

**Prioridad:** 🔴 ALTA | **Dificultad:** 🛠️ Difícil

---

### 4.2 HTTPS para endpoint de fotos (TimerCam X)

**Qué:** La TimerCam X hace HTTP POST para subir fotos. En texto plano, cualquiera en la red puede interceptar las fotos.

**Cómo:**
- Crear un endpoint HTTPS simple con nginx como reverse proxy + certificado self-signed (o Let's Encrypt si el LXC tiene dominio).
- La TimerCam X (ESP32 con firmware M5Stack) soporta `WiFiClientSecure` para HTTPS.

**Configuración nginx en LXC:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate     /etc/ssl/sniperstation/server.crt;
    ssl_certificate_key /etc/ssl/sniperstation/server.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location /upload {
        # Script Python o endpoint que recibe el POST
        proxy_pass http://127.0.0.1:5000/upload;
        client_max_body_size 10M;
    }
}
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 4.3 InfluxDB sobre HTTPS

**Qué:** Si Grafana o cualquier cliente accede a InfluxDB, debe hacerlo por HTTPS (puerto 8086 con TLS).

**Cómo (InfluxDB 2.x):**
```bash
# InfluxDB 2.x soporta TLS nativo
# /etc/influxdb/config.toml:
[tls]
  cert = "/etc/influxdb/certs/server.crt"
  key  = "/etc/influxdb/certs/server.key"
```

En Grafana, actualizar el datasource:
- URL: `https://localhost:8086`
- Marcar "Skip TLS Verify" solo si usas certificado self-signed sin CA instalada en Grafana.

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 4.4 Grafana sobre HTTPS (reverse proxy nginx)

**Qué:** Grafana en puerto 3000 sirve HTTP por defecto. Acceder desde la LAN o desde internet expone sesiones y credenciales.

**Cómo:**
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

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

## 5. Capa 5 — Sesión

### 5.1 Tiempo de expiración de sesiones Grafana

**Qué:** Si alguien usa Grafana desde un celular público o deja la sesión abierta, el token debe expirar.

**Cómo (`/etc/grafana/grafana.ini`):**
```ini
[auth]
login_maximum_inactive_lifetime_duration = 7d
login_maximum_lifetime_duration = 30d
token_rotation_interval_minutes = 10
```

**Prioridad:** 🟢 BAJA | **Dificultad:** ⚡ Fácil

---

### 5.2 Rate limiting en endpoint HTTP de fotos (TimerCam X)

**Qué:** El endpoint que recibe los HTTP POST de la TimerCam debe tener rate limiting para evitar abuso (flood de fotos, DoS).

**Cómo (nginx):**
```nginx
# En el bloque http {} de nginx.conf
limit_req_zone $binary_remote_addr zone=timercam:1m rate=10r/m;

# En el location del endpoint
location /upload {
    limit_req zone=timercam burst=5 nodelay;
    # ... resto de la config
}
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 5.3 Deshabilitar acceso remoto a Proxmox web UI desde internet

**Qué:** El panel web de Proxmox (puerto 8006) no debe ser accesible desde internet.

**Cómo:**
- En el router: no hacer port forwarding del 8006.
- Si necesitas acceso remoto: usar VPN (WireGuard en pfSense/OPNsense) y acceder solo desde la VPN.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

## 6. Capa 7 — Aplicación

### 6.1 Deshabilitar anonymous access en Mosquitto

**Qué:** Por defecto Mosquitto puede aceptar conexiones sin usuario/password.

**Cómo:**
```bash
# Crear usuario para cada dispositivo
mosquitto_passwd -c /etc/mosquitto/passwd station485
mosquitto_passwd -b /etc/mosquitto/passwd cyd_master <password>
mosquitto_passwd -b /etc/mosquitto/passwd cyd_kids <password>
mosquitto_passwd -b /etc/mosquitto/passwd timercam <password>
mosquitto_passwd -b /etc/mosquitto/passwd telegraf_bridge <password>
mosquitto_passwd -b /etc/mosquitto/passwd telegram_bot <password>
```

En `/etc/mosquitto/mosquitto.conf`:
```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Reiniciar: `systemctl restart mosquitto`

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 6.2 ACLs MQTT — control de topics por cliente

**Qué:** Cada dispositivo solo debe poder publicar/suscribirse a sus propios topics. El Station-485 no debe poder publicar en topics de indoor, y el Telegram Bot no debe poder publicar en topics de sensores.

**Cómo — Crear `/etc/mosquitto/acl`:**

```
# station485 — publica sensores exterior, recibe comandos de bomba
user station485
topic write sniperstation/exterior/#
topic write sniperstation/sucufer/#
topic write sniperstation/sucurod/#
topic write sniperstation/agua/#
topic write sniperstation/sistema/#
topic write sniperstation/alertas
topic read  sniperstation/sucufer/bomba/set
topic read  sniperstation/sucurod/bomba/set

# cyd_master — publica indoor master, lee todos los sensores para display
user cyd_master
topic write sniperstation/interior/master/#
topic read  sniperstation/#

# cyd_kids — igual que master pero para kids bedroom
user cyd_kids
topic write sniperstation/interior/kids/#
topic read  sniperstation/#

# timercam — solo publica evento de captura
user timercam
topic write sniperstation/camaras/sucufer/captura

# telegram_bot — lee alertas, envía comandos de bomba
user telegram_bot
topic read  sniperstation/alertas
topic read  sniperstation/#
topic write sniperstation/sucufer/bomba/set
topic write sniperstation/sucurod/bomba/set

# telegraf_bridge — lee todo para escribir a InfluxDB
user telegraf_bridge
topic read  sniperstation/#
```

En `mosquitto.conf`:
```
acl_file /etc/mosquitto/acl
```

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 6.3 Autenticación InfluxDB 2.x con tokens

**Qué:** InfluxDB 2.x usa tokens en vez de usuario/password. Cada servicio que escribe o lee debe tener su propio token con permisos mínimos.

**Cómo:**
```bash
# Crear token de solo escritura para Telegraf/bridge MQTT
influx auth create \
  --org sniperstation \
  --write-bucket sniperstation \
  --description "telegraf-write-only"

# Crear token de solo lectura para Grafana
influx auth create \
  --org sniperstation \
  --read-bucket sniperstation \
  --description "grafana-read-only"

# Listar tokens
influx auth list
```

- Telegraf/bridge → usa el token de escritura.
- Grafana datasource → usa el token de lectura.
- **Nunca** usar el token de administrador (All Access) en los servicios.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 6.4 Autenticación Grafana — cambiar password admin y deshabilitar admin por defecto

**Qué:** Grafana instala con `admin:admin`. Es la primera credencial que cualquier atacante prueba.

**Cómo:**
```bash
# Cambiar desde CLI
grafana-cli admin reset-admin-password "contraseña_fuerte_aqui"

# O desde grafana.ini — deshabilitar signup y anonymous
```

`/etc/grafana/grafana.ini`:
```ini
[security]
admin_user = sniperstation_admin   # Cambiar nombre de usuario admin
admin_password = <password_fuerte>
disable_gravatar = true

[users]
allow_sign_up = false
allow_org_create = false

[auth.anonymous]
enabled = false
```

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 6.5 Autenticación del endpoint HTTP de fotos (TimerCam X)

**Qué:** El endpoint que recibe HTTP POST de la TimerCam no debe ser público. Debe requerir autenticación.

**Cómo — API key en header HTTP:**

La TimerCam X envía el header en el POST:
```
Authorization: Bearer <token_secreto>
```

En el servidor (Python Flask o FastAPI):
```python
API_KEY = os.environ.get("TIMERCAM_API_KEY")

@app.route("/upload", methods=["POST"])
def upload_photo():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {API_KEY}":
        return {"error": "unauthorized"}, 401
    # ... procesar foto
```

El token se configura en el firmware de la TimerCam como constante (ver sección 12).

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 6.6 Validar comandos de bomba en el firmware (sanitización de inputs)

**Qué:** El topic `sniperstation/sucufer/bomba/set` acepta comandos externos (del Telegram Bot). Si hay inyección de valores inesperados, el firmware podría activar la bomba indefinidamente.

**Cómo — en el firmware del Station-485:**
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

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

## 7. Autenticación y Autorización

### 7.1 Resumen de credenciales por servicio

| Servicio | Mecanismo | Usuarios a crear |
|----------|-----------|------------------|
| Mosquitto | usuario/password + ACL | station485, cyd_master, cyd_kids, timercam, telegraf_bridge, telegram_bot |
| InfluxDB 2.x | Tokens con permisos mínimos | Token escritura (Telegraf), Token lectura (Grafana) |
| Grafana | usuario/password | admin (renombrado), lector opcional sin write access |
| HTTP endpoint fotos | API key en Bearer header | timercam (1 token) |
| Proxmox | usuario/password + 2FA | Solo acceso desde LAN/VPN |

### 7.2 Habilitar 2FA en Grafana

**Qué:** Si Grafana es accesible desde internet o dispositivos compartidos, el segundo factor previene acceso con password robada.

**Cómo:**
```ini
# /etc/grafana/grafana.ini
[auth]
disable_login_form = false

[auth.basic]
enabled = true
```

Luego en el perfil de usuario en Grafana UI: habilitar TOTP (Google Authenticator / Authy).

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 7.3 Token del bot de Telegram — proteger contra uso no autorizado

**Qué:** El token del bot de Telegram permite a cualquiera enviar comandos si lo obtiene.

**Cómo:**
- Restringir el bot a solo aceptar mensajes de tu `chat_id` personal (no de otros usuarios):

```python
AUTHORIZED_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID"))

def handle_message(update, context):
    if update.message.chat_id != AUTHORIZED_CHAT_ID:
        update.message.reply_text("Unauthorized")
        return
    # ... procesar comando
```

- Si quieres comandos desde múltiples personas (familia), usar una lista: `AUTHORIZED_IDS = [id1, id2]`.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

## 8. Cifrado en Tránsito

### 8.1 Resumen de cifrado por protocolo

| Protocolo | Estado actual | Objetivo |
|-----------|--------------|----------|
| MQTT (ESP32 → broker) | Plaintext :1883 | MQTTS :8883 con TLS 1.2+ |
| HTTP POST (TimerCam → LXC) | Plaintext | HTTPS con cert self-signed |
| InfluxDB (Telegraf → DB) | Plaintext | HTTPS con TLS |
| Grafana (browser → LXC) | HTTP | HTTPS via nginx reverse proxy |
| Telegram Bot API | Ya es HTTPS | Mantener |

### 8.2 Generación centralizada de certificados self-signed

Para un sistema doméstico, un CA propio (ver sección 4.1) es suficiente. Todos los servicios pueden compartir el mismo par cert/key del servidor, o tener certificados individuales.

**Script para generar todos los certs de una vez:**

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

**Prioridad:** 🔴 ALTA | **Dificultad:** 🛠️ Difícil (cambios en firmware)

---

## 9. Cifrado en Reposo

### 9.1 Cifrado de volumen InfluxDB con LUKS

**Qué:** Los datos de InfluxDB (series de tiempo de sensores, fotos metadata) se almacenan en texto plano en el filesystem del LXC. Si alguien obtiene acceso al host Proxmox, puede leer todo.

**Cómo:**
- Crear un disco virtual cifrado con LUKS para el volumen de datos de InfluxDB.
- Esto requiere que el LXC tenga acceso a `/dev/mapper` (en Proxmox, el LXC debe ser tipo "privileged" o con configuración especial).

```bash
# En el host Proxmox — crear disco cifrado
dd if=/dev/zero of=/var/lib/vz/images/influxdb-encrypted.raw bs=1G count=10
losetup /dev/loop10 /var/lib/vz/images/influxdb-encrypted.raw
cryptsetup luksFormat /dev/loop10
cryptsetup luksOpen /dev/loop10 influxdb_data
mkfs.ext4 /dev/mapper/influxdb_data
mount /dev/mapper/influxdb_data /var/lib/influxdb
```

**Alternativa más simple:** Cifrar el volumen completo del LXC a nivel de Proxmox storage (ZFS con encryption o usando un disco LUKS como storage del PVE).

**Prioridad:** 🟢 BAJA (red doméstica, no HIPAA/PCI) | **Dificultad:** 🛠️ Difícil

---

### 9.2 No almacenar credenciales en texto plano en el filesystem

**Qué:** Las passwords de Mosquitto, tokens de InfluxDB, y el token del bot de Telegram no deben estar en archivos de config en texto plano sin permisos restrictivos.

**Cómo:**
```bash
# Permisos correctos para archivos sensibles
chmod 600 /etc/mosquitto/passwd
chmod 600 /etc/mosquitto/acl
chmod 640 /etc/mosquitto/certs/ca.key
chmod 640 /etc/mosquitto/certs/server.key
chown root:mosquitto /etc/mosquitto/passwd

# Variables de entorno para el bot de Telegram
# Crear /etc/sniperstation/secrets.env (no en repo git)
chmod 600 /etc/sniperstation/secrets.env
chown root:root /etc/sniperstation/secrets.env
```

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 9.3 Fotos de TimerCam — permisos de directorio

**Qué:** El directorio donde se almacenan las fotos de las suculentas debe tener permisos correctos.

**Cómo:**
```bash
mkdir -p /var/sniperstation/photos
chown www-data:www-data /var/sniperstation/photos  # o el usuario del proceso Python
chmod 750 /var/sniperstation/photos
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

## 10. Seguridad del Firmware ESP32

### 10.1 No hardcodear credenciales en el código fuente

**Qué:** El patrón más común y peligroso: poner WiFi password, MQTT password, y API tokens directamente en el `.ino` o `.cpp`. Si el repo es público (GitHub), las credenciales son públicas.

**Cómo — usar un archivo de configuración local no versionado:**

Crear `firmware/station485/secrets.h` (en `.gitignore`):
```cpp
// secrets.h — NOT committed to git
#define WIFI_SSID     "nombre_red_iot"
#define WIFI_PASSWORD "password_wifi"
#define MQTT_HOST     "192.168.1.50"
#define MQTT_PORT     8883
#define MQTT_USER     "station485"
#define MQTT_PASSWORD "password_mqtt_station"
```

En el `.ino` principal:
```cpp
#include "secrets.h"
// Usar WIFI_SSID, WIFI_PASSWORD, etc.
```

En `.gitignore`:
```
firmware/station485/secrets.h
firmware/cyd_indoor/secrets.h
firmware/timercam/secrets.h
```

Proporcionar un `secrets.h.example` con valores placeholder para que otros sepan qué variables necesitan.

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 10.2 Usar ESP32 NVS (Non-Volatile Storage) para credenciales

**Qué:** Una mejora sobre `secrets.h` es almacenar las credenciales en la partición NVS del ESP32, que es separada del código flash y puede ser protegida. Esto permite cambiar credenciales sin recompilar el firmware.

**Cómo:**
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

// Para escribir las credenciales inicialmente (solo una vez, desde serial):
void writeCredentials() {
    prefs.begin("secrets", false);  // Read-write
    prefs.putString("wifi_ssid", "nombre_red");
    prefs.putString("wifi_pass", "password");
    prefs.putString("mqtt_user", "station485");
    prefs.putString("mqtt_pass", "password_mqtt");
    prefs.end();
}
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 10.3 Habilitar Flash Encryption en ESP32

**Qué:** El ESP32 tiene soporte nativo para cifrar el contenido del flash con AES-256. Sin esto, conectar el ESP32 a un programador USB permite leer el firmware completo (y las credenciales hardcodeadas).

**Cómo (Arduino IDE + esptool):**
```bash
# Habilitar flash encryption durante el flashing
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash_encrypt \
  --flash_mode dio --flash_freq 40m --flash_size detect \
  0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 firmware.bin

# Verificar estado de flash encryption
esptool.py --chip esp32 --port /dev/ttyUSB0 get_security_info
```

**Advertencia:** Una vez habilitado el flash encryption en modo "Release", el ESP32 NO puede ser re-programado por UART. Solo se puede actualizar vía OTA. Usar modo "Development" para testing.

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🛠️ Difícil

---

### 10.4 OTA (Over-The-Air) updates seguros

**Qué:** Los ESP32 deben poder actualizarse sin acceso físico. Sin seguridad en OTA, un atacante en la red podría inyectar firmware malicioso.

**Cómo (ArduinoOTA con password):**
```cpp
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setPassword("password_ota_secreto");
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
    // ... resto del loop
}
```

**Para OTA desde servidor propio (más seguro que mDNS):**
```cpp
#include <HTTPUpdate.h>

void checkOTAUpdate() {
    WiFiClientSecure client;
    client.setCACert(ca_cert);  // Verificar el servidor de OTA
    t_httpUpdate_return ret = httpUpdate.update(
        client,
        "https://192.168.1.50/ota/station485.bin",
        CURRENT_FIRMWARE_VERSION
    );
}
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 10.5 Watchdog timer habilitado

**Qué:** No es estrictamente seguridad, pero un ESP32 colgado que no responde puede dejar la bomba activa indefinidamente.

**Cómo:**
```cpp
#include <esp_task_wdt.h>

void setup() {
    // Watchdog de 30 segundos — si el loop no hace reset, reinicia el ESP32
    esp_task_wdt_init(30, true);
    esp_task_wdt_add(NULL);
}

void loop() {
    esp_task_wdt_reset();  // Reset del watchdog al inicio de cada ciclo

    // Safety: nunca dejar la bomba activa más de MAX_PUMP_DURATION_MS
    // (ver sección 6.6)
}
```

**Prioridad:** 🔴 ALTA (seguridad operacional de las plantas) | **Dificultad:** ⚡ Fácil

---

## 11. Segmentación de Red — IoT VLAN

### 11.1 Arquitectura de red recomendada

```
[Internet]
     │
  [Router/Modem ISP]
     │
  [pfSense/OPNsense]
     ├── LAN (VLAN 1) — 192.168.1.0/24
     │   ├── Computadoras, celulares
     │   ├── Proxmox LXC (192.168.1.50)
     │   └── NAS, impresoras
     │
     ├── IoT VLAN (VLAN 10) — 192.168.10.0/24
     │   ├── Station-485     → 192.168.10.10
     │   ├── CYD master      → 192.168.10.11
     │   ├── CYD kids        → 192.168.10.12
     │   └── TimerCam X      → 192.168.10.13
     │
     └── [Access Point con múltiples SSIDs]
         ├── "HomeNetwork"    → VLAN 1
         └── "HomeIoT"        → VLAN 10 (oculta, WPA2)
```

### 11.2 Reglas de firewall completas

**Reglas en VLAN IoT (OPT1) — política "deny all, permit by exception":**

```
# pfSense/OPNsense — Rules → IoT Interface (OPT1)
# Orden importa — se evalúan de arriba a abajo

Regla 1: PASS  UDP  IoT:any → 192.168.1.50:1883   (MQTT plaintext — temporal)
Regla 2: PASS  TCP  IoT:any → 192.168.1.50:8883   (MQTTS)
Regla 3: PASS  TCP  IoT:any → 192.168.1.50:443    (HTTPS fotos TimerCam)
Regla 4: PASS  UDP  IoT:any → 0.0.0.0:123         (NTP)
Regla 5: PASS  TCP  IoT:any → 0.0.0.0:443         (HTTPS para OTA updates)
Regla 6: BLOCK any  IoT:any → 192.168.1.0/24      (bloqueo total a LAN)
Regla 7: BLOCK any  IoT:any → any                  (deny all default)
```

**Notas:**
- Eliminar Regla 1 una vez que MQTTS esté funcionando.
- La Regla 5 (HTTPS a internet) es necesaria para OTA y sincronización NTP por HTTPS. Si no usas OTA, removerla.

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 11.3 DNS separado para la VLAN IoT

**Qué:** Usar DNS propio en la VLAN IoT previene que los dispositivos IoT resuelvan dominios de tracking o que sean víctimas de DNS poisoning.

**Cómo (pfSense):**
- En DHCP de la VLAN IoT, configurar DNS server = 192.168.1.1 (el propio pfSense con DNS Resolver).
- Bloquear queries DNS al exterior desde la VLAN IoT (puerto 53 UDP/TCP solo al pfSense):
  ```
  PASS UDP IoT:any → pfSense_IoT_IP:53
  BLOCK UDP IoT:any → any:53
  ```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

## 12. Gestión de Secretos

### 12.1 Lista completa de secretos del sistema

| Secreto | Usado por | Almacenamiento recomendado |
|---------|-----------|---------------------------|
| WiFi SSID + password (IoT VLAN) | Todos los ESP32 | secrets.h (no en git) + NVS |
| MQTT password (station485) | Station-485 firmware | secrets.h + NVS |
| MQTT password (cyd_master) | CYD master firmware | secrets.h + NVS |
| MQTT password (cyd_kids) | CYD kids firmware | secrets.h + NVS |
| MQTT password (timercam) | TimerCam firmware | secrets.h + NVS |
| MQTT password (telegram_bot) | Python bot | Variable de entorno / secrets.env |
| MQTT password (telegraf_bridge) | Telegraf | Variable de entorno / secrets.env |
| InfluxDB token escritura | Telegraf | Variable de entorno |
| InfluxDB token lectura | Grafana | Grafana datasource config |
| Telegram Bot token | Python bot | Variable de entorno |
| Telegram Chat ID autorizado | Python bot | Variable de entorno |
| TimerCam API key (HTTP upload) | TimerCam + servidor | secrets.h + env var |
| OTA password | ESP32 + cliente OTA | secrets.h |
| Grafana admin password | Grafana | grafana.ini (perms 640) |
| Proxmox root password | Admin | Gestor de passwords (Bitwarden) |

### 12.2 Estructura de secretos en el LXC

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

Cargar en los servicios:
```bash
# systemd service file para el bot de Telegram
[Service]
EnvironmentFile=/etc/sniperstation/secrets.env
ExecStart=/usr/bin/python3 /opt/sniperstation/telegram_bot/bot.py
```

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

### 12.3 Rotación periódica de credenciales

**Qué:** Las passwords de MQTT y tokens de InfluxDB deben rotarse si hay sospecha de compromiso o periódicamente (cada 6-12 meses).

**Procedimiento de rotación MQTT:**
```bash
# 1. Generar nuevo password
mosquitto_passwd -b /etc/mosquitto/passwd station485 <nuevo_password>

# 2. Actualizar secrets.h en el firmware
# 3. Re-flashear el ESP32 afectado (o via OTA)
# 4. Verificar que reconecta correctamente
# 5. Reiniciar Mosquitto si es necesario
systemctl reload mosquitto
```

**Prioridad:** 🟢 BAJA | **Dificultad:** 🔧 Media

---

### 12.4 Agregar secrets.h a .gitignore (verificación)

```bash
# Verificar que el .gitignore del repo cubre los archivos de secretos
cat /home/claude/sniperstation/.gitignore
```

Agregar si no están:
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

**Prioridad:** 🔴 ALTA | **Dificultad:** ⚡ Fácil

---

## 13. Monitoreo y Alertas de Seguridad

### 13.1 Logging de conexiones MQTT fallidas

**Qué:** Detectar intentos de acceso al broker con credenciales incorrectas.

**Cómo — Mosquitto log:**
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

Luego monitorear con `tail -f /var/log/mosquitto/mosquitto.log` o configurar `fail2ban`.

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 13.2 Fail2ban para Mosquitto y Grafana

**Qué:** Bloquear IPs que hacen múltiples intentos fallidos de autenticación.

**Cómo:**
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

Crear filtro `/etc/fail2ban/filter.d/mosquitto.conf`:
```ini
[Definition]
failregex = .* Client .* failed to connect: not authorised
            .* bad user name or password
ignoreregex =
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 13.3 Alerta Telegram cuando un ESP32 se desconecta inesperadamente

**Qué:** Si un dispositivo deja de publicar en MQTT, puede indicar una desconexión normal (reinicio) o un evento de seguridad (manipulación física, jam WiFi).

**Cómo — MQTT Last Will and Testament (LWT):**

En el firmware de cada ESP32:
```cpp
// Configurar LWT antes de conectar al broker
mqttClient.setWill(
    "sniperstation/sistema/lwt",  // topic
    "offline",                     // payload
    false,                         // retain
    1                              // QoS
);

// Al conectar exitosamente, publicar online
mqttClient.publish("sniperstation/sistema/lwt", "online");
```

En el bot de Telegram:
```python
def on_lwt_message(client, userdata, msg):
    device = msg.topic.split("/")[2]
    if msg.payload.decode() == "offline":
        send_telegram_alert(f"ALERTA: {device} desconectado del broker MQTT")
```

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 13.4 Alerta Telegram ante publicación en topics no esperados

**Qué:** Si alguien compromete un dispositivo y empieza a publicar en topics que no corresponden (ej. station485 publicando en topics de indoor), el bot debe alertar.

**Cómo:**
```python
EXPECTED_PUBLISHERS = {
    "sniperstation/exterior/+": "station485",
    "sniperstation/sucufer/+": "station485",
    "sniperstation/sucurod/+": "station485",
    "sniperstation/interior/master/+": "cyd_master",
    "sniperstation/interior/kids/+": "cyd_kids",
    "sniperstation/camaras/sucufer/+": "timercam",
}
# Monitorear con client_id en el message y comparar con expected publisher
```

**Nota:** Mosquitto no expone el client_id en el payload por defecto. Esto requiere una implementación custom en el broker o un bridge que enriquezca los mensajes.

**Prioridad:** 🟢 BAJA | **Dificultad:** 🛠️ Difícil

---

### 13.5 Panel de seguridad en Grafana

**Qué:** Dashboard dedicado a métricas de seguridad operacional.

**Panels sugeridos:**
- Último timestamp de conexión de cada ESP32 (detectar dispositivos silentes).
- Contador de reconnects MQTT por dispositivo por hora.
- Gráfica de mensajes recibidos por topic (anomalías de volumen).
- Estado del nivel de agua (alerta si permanece en vacío > 6h sin intervención).
- Historial de activaciones de bomba (detectar activaciones inesperadas).

**Prioridad:** 🟡 MEDIA | **Dificultad:** 🔧 Media

---

### 13.6 Auditoría periódica del broker MQTT

**Cómo:**
```bash
# Ver clientes actualmente conectados
mosquitto_sub -h localhost -u admin -P password \
  -t '$SYS/broker/clients/connected' -C 1

# Ver todos los topics activos
mosquitto_sub -h localhost -u admin -P password \
  -t '$SYS/#' -v -C 20

# Contar mensajes por topic
mosquitto_sub -h localhost -u admin -P password \
  -t 'sniperstation/#' -v --retained-only
```

**Prioridad:** 🟢 BAJA | **Dificultad:** ⚡ Fácil

---

## 14. Seguridad Física

### 14.1 Protección del enclosure exterior contra calor extremo

**Contexto de seguridad:** Orlando en verano puede llevar el interior de una caja cerrada a >70°C. El Station-485 tiene límite de 60°C. Un ESP32 en thermal shutdown puede dejar la bomba activa (si el pin de relay queda en HIGH), con riesgo de daño a las plantas.

**Medidas:**
- Caja en sombra permanente (nunca sol directo).
- Ventilación pasiva: agujeros de 10mm con malla en la parte inferior (entrada) y superior (salida), con cubierta anti-lluvia tipo "mushroom vent".
- Si temperatura > 45°C sostenida: agregar el ventilador 5V del inventario SunFounder con control por termistor (disponible en el kit).
- El firmware debe tener: si `temp_interior_caja > 58°C`, apagar relays y enviar alerta Telegram.

**Prioridad:** 🔴 ALTA | **Dificultad:** 🔧 Media

---

### 14.2 Protección contra sabotaje de las bombas

**Qué:** Los cables de 12V que van a las bombas son accesibles desde afuera del enclosure. Alguien podría cortarlos.

**Medidas:**
- Usar cable con cubierta de acero trenzado (tipo cable de bicicleta) entre el enclosure y las bombas.
- Los cables que salen del enclosure deben salir por la parte inferior para dificultar el acceso.
- El firmware detecta error de sensor de humedad y alerta si una bomba activada no produce cambio de humedad en 5 minutos.

**Prioridad:** 🟢 BAJA | **Dificultad:** ⚡ Fácil

---

### 14.3 Inventario y etiquetado de hardware

**Qué:** Documentar todos los dispositivos para detección rápida de hardware no autorizado conectado a la red.

**Cómo:**
- Fotografiar y registrar la MAC address de cada ESP32 antes de instalarlo.
- Etiquetar físicamente cada dispositivo con su hostname (station485, cyd_master, etc.).
- Mantener lista actualizada en este repositorio (`hardware/inventory.md`).
- Revisar periódicamente la tabla de clientes DHCP del router para detectar dispositivos no reconocidos en la VLAN IoT.

**Prioridad:** 🟡 MEDIA | **Dificultad:** ⚡ Fácil

---

### 14.4 UPS o batería de respaldo para el LXC

**Qué:** Una interrupción de poder mientras la bomba está activa puede dejar el relay en estado indeterminado. Si el LXC (Mosquitto) se cae, los ESP32 pierden conectividad MQTT.

**Medidas de firmware (sin UPS):**
- Usar NVS para almacenar el estado de la bomba (activa/inactiva) con timestamp.
- Al reiniciar, si el estado almacenado es "activa" y han pasado >2 minutos, asumir fallo y forzar desactivación del relay.

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

**Prioridad:** 🔴 ALTA (seguridad de las plantas) | **Dificultad:** 🔧 Media

---

## Checklist de Implementación

### Prioridad ALTA — Antes de poner en producción

- [ ] Cambiar password admin de Grafana (no usar admin:admin)
- [ ] Deshabilitar anonymous en Mosquitto + crear usuario por dispositivo
- [ ] Agregar `secrets.h` al `.gitignore` antes del primer commit de firmware
- [ ] Configurar ACLs MQTT por usuario
- [ ] Crear tokens de InfluxDB con permisos mínimos (escritura y lectura separados)
- [ ] Restricción de chat_id en el bot de Telegram
- [ ] Implementar autenticación en el endpoint HTTP de fotos (TimerCam)
- [ ] Crear VLAN IoT en pfSense/OPNsense con reglas de bloqueo a LAN
- [ ] IP estática para el LXC
- [ ] Watchdog timer en todos los ESP32
- [ ] Relay force-off en firmware: limite absoluto de duración de bomba
- [ ] Deshabilitar WPS en el router
- [ ] Proxmox web UI no accesible desde internet (sin port forwarding)
- [ ] Permisos 600 en archivos de secretos del LXC

### Prioridad MEDIA — Primera semana

- [ ] Implementar MQTTS (puerto 8883, TLS 1.2)
- [ ] HTTPS para endpoint de fotos (TimerCam)
- [ ] Reverse proxy nginx con TLS para Grafana
- [ ] InfluxDB con TLS habilitado
- [ ] Fail2ban para Mosquitto y Grafana
- [ ] Logging habilitado en Mosquitto
- [ ] LWT configurado en todos los ESP32 + alerta Telegram en desconexión
- [ ] Filtrado MAC en VLAN IoT
- [ ] DNS separado para VLAN IoT
- [ ] Credenciales en NVS en vez de secrets.h compilado
- [ ] OTA con password en todos los ESP32
- [ ] 2FA en Grafana
- [ ] Panel de seguridad en Grafana

### Prioridad BAJA — Hardening adicional

- [ ] Flash encryption en ESP32
- [ ] SSID de IoT VLAN oculto
- [ ] LUKS para volumen InfluxDB
- [ ] Rotación periódica de credenciales (cada 6 meses)
- [ ] Cable glands + sellado de enclosure exterior
- [ ] Tornillos de seguridad Torx en enclosure exterior
- [ ] Inventario de hardware documentado con MACs
- [ ] Monitoreo de topics anómalos en MQTT

---

*Documento generado: 2026-03-26*
*Arquitectura: M5Stack Station-485 + 2x CYD ESP32 + TimerCam X + Proxmox LXC (Mosquitto + InfluxDB + Grafana + Telegram Bot)*
*Red: Orlando, Florida — doméstica con pfSense/OPNsense*
