# snipermqtt — Plan de Despliegue

**Host:** snipermox.uzc (192.168.0.2) — Proxmox 9.1.5
**Nombre LXC:** snipermqtt.uzc
**OS:** Debian 12 (Bookworm)
**Almacenamiento:** local2 (todo — template, rootdir, fotos)
**Red:** vmbr0 (LAN 192.168.0.x)
**IP estática:** 192.168.0.79
**DNS:** snipermqtt.uzc (registrado en Pi-hole)
**MAC:** pendiente — autogenerado al crear LXC, luego reservar en pfSense

---

## Reglas Proxmox (no negociables)

- NO reiniciar el host Proxmox
- NO tocar VMs o LXCs existentes (100–111, 200)
- NO modificar bridges de red ni configuración de red de Proxmox
- Actualizaciones permitidas solo dentro del nuevo LXC
- Si se requiere reinicio (actualización de kernel, etc.) → consultar a Leo primero

---

## Especificaciones del LXC

| Parámetro | Valor |
|---|---|
| VMID | 112 |
| Hostname | snipermqtt |
| Template | debian-12-standard_12.x_amd64.tar.zst (descargar a local2) |
| Almacenamiento | local2 |
| Disco | 20GB |
| RAM | 1024 MB |
| Swap | 512 MB |
| CPU | 2 núcleos |
| Red | vmbr0, estática 192.168.0.79/24, gw 192.168.0.254 |
| DNS | 192.168.0.240 (sniperhole Pi-hole) |
| Sin privilegios | sí |
| Iniciar al arrancar | sí |

---

## Servicios a Instalar

### 1. Mosquitto (Broker MQTT)
- Versión: última desde repos Debian 12 (`apt install mosquitto`)
- Puerto: 1883 (texto plano, temporal) → 8883 (MQTTS, seguridad Fase 3)
- Config: `/etc/mosquitto/mosquitto.conf`
- Auth: un usuario por dispositivo (station485, cyd_master, cyd_kids, timercam, telegraf_bridge, telegram_bot)
- Archivo ACL: permisos por topic por usuario (ver `docs/security.md` §6.2)
- Logs: `/var/log/mosquitto/mosquitto.log`

### 2. InfluxDB 2.x
- Método de instalación: repo oficial InfluxData apt para Debian 12
- Puerto: 8086
- Org: `sniperstation`
- Bucket: `sniperstation`
- Tokens: solo escritura (Telegraf), solo lectura (Grafana)

### 3. Grafana
- Método de instalación: repo oficial Grafana Labs apt
- Puerto: 3000 (detrás de proxy inverso nginx en 443)
- Datasource: InfluxDB (token de solo lectura)
- Admin: renombrar desde el predeterminado, contraseña fuerte, 2FA

### 4. Telegraf (puente MQTT → InfluxDB)
- Método de instalación: repo oficial InfluxData apt
- Rol: suscribirse a `sniperstation/#` en Mosquitto, escribir a InfluxDB
- Config: `/etc/telegraf/telegraf.conf`

### 5. Bot de Telegram (con lenguaje natural + reportes)
- Runtime: Python 3 (sistema)
- Ubicación: `/opt/sniperstation/telegram_bot/`
- Servicio: unidad systemd, carga secrets desde `/etc/sniperstation/secrets.env`
- Auth: restringido al chat_id autorizado únicamente
- **Lenguaje natural:** Claude API (claude-opus-4-6) — consulta InfluxDB y responde en forma conversacional
  - Ejemplos: "¿Cómo están las matas?", "¿Cuándo fue el último riego?", "¿Qué temperatura hay afuera?"
  - Mismo patrón agéntico que SniperFIN
- **Reportes por email via Resend API:**
  - Diario x3: temperatura (todos los cuartos) + humedad + estado del suelo
  - Semanal x1: resumen de riego, tendencias, anomalías
  - Mensual x1: estadísticas históricas completas
  - Destinatario: leonuz@hotmail.com

### 6. nginx
- Rol: proxy inverso para Grafana (HTTPS) + endpoint HTTP para fotos de TimerCam X
- Puertos: 80 (redirige a 443), 443 (Grafana + endpoint /upload)
- TLS: certificados de la CA de pfSense
- Rate limiting: 10 req/min en /upload
- Almacenamiento de fotos: `/var/sniperstation/photos/`

---

## TLS / Certificados

- CA: CA interna de pfSense (ya existe)
- Ubicación de archivos cert en LXC: `/etc/sniperstation/certs/` (chmod 700)
- Staging temporal en host Proxmox: `/root/sniperstation-certs/` (chmod 700) — nunca en git
- Usados por: nginx (HTTPS), Mosquitto (MQTTS puerto 8883)

---

## Secrets

Todos los secrets almacenados en `/etc/sniperstation/secrets.env` — `chmod 600`, cargados via `EnvironmentFile` de systemd.

| Secret | Usado por |
|---|---|
| Contraseñas MQTT (por dispositivo) | Cada firmware ESP32 + servicios |
| Token de escritura InfluxDB | Telegraf |
| Token de lectura InfluxDB | Grafana |
| Token del bot Telegram | Bot |
| chat_id Telegram | Bot |
| Clave API Claude | Bot (lenguaje natural) |
| Clave API Resend | Bot (reportes por email) |
| Clave API TimerCam | Bot + nginx /upload |

---

## Estructura de Directorios (dentro del LXC)

```
/etc/mosquitto/
├── mosquitto.conf
├── passwd
└── acl

/etc/sniperstation/
├── secrets.env          # chmod 600 — todos los secrets de servicios
└── certs/               # chmod 700 — certs TLS de CA pfSense

/etc/telegraf/
└── telegraf.conf

/opt/sniperstation/
└── telegram_bot/
    ├── bot.py
    ├── agent.py          # Loop LLM (Claude API)
    ├── tools.py          # Herramientas de consulta InfluxDB
    ├── reports.py        # Reportes diarios/semanales/mensuales (Resend)
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

## Orden de Instalación

1. Descargar template Debian 12 a local2
2. Crear LXC (pct create) → obtener MAC autogenerada
3. Registrar MAC en pfSense (IP 192.168.0.79) + DNS en Pi-hole (snipermqtt.uzc)
4. Iniciar LXC, configuración inicial (locale, timezone America/New_York, apt update/upgrade)
5. Instalar Mosquitto → configurar auth + ACL
6. Instalar InfluxDB 2.x → crear org, bucket, tokens
7. Instalar Telegraf → configurar entrada MQTT + salida InfluxDB
8. Instalar Grafana → configurar datasource, cambiar contraseña admin
9. Instalar nginx → configurar proxy inverso + endpoint /upload + certs TLS de CA pfSense
10. Desplegar bot Telegram → servicio systemd (lenguaje natural + reportes)
11. Crear directorios de fotos con permisos correctos
12. Aplicar hardening de seguridad (fail2ban, permisos de archivos, secrets.env)
13. Prueba de humo: publicar mensaje MQTT de prueba → verificar en InfluxDB → verificar en Grafana → verificar Telegram

---

## Checklist de Seguridad (Fase 3 — de ROADMAP)

- [ ] `allow_anonymous false` en Mosquitto
- [ ] Un usuario MQTT por dispositivo con ACL
- [ ] Tokens InfluxDB con permisos mínimos
- [ ] Contraseña predeterminada de Grafana cambiada, registro deshabilitado, 2FA habilitado
- [ ] Rate limiting en nginx para /upload
- [ ] TLS en nginx (cert CA pfSense)
- [ ] `/etc/sniperstation/secrets.env` chmod 600
- [ ] `/etc/sniperstation/certs/` chmod 700
- [ ] fail2ban para Mosquitto y Grafana
- [ ] Bot Telegram restringido al chat_id autorizado

---

*Plan creado: 2026-03-27*
*Actualizado: 2026-03-27 — IP 192.168.0.79, DNS snipermqtt.uzc, bot NL con Claude API, reportes por email Resend, TLS con CA pfSense*
