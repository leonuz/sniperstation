# Changelog

Todos los cambios notables a SniperStation serán documentados en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Sin publicar]

### Planificado
- Firmware Station-485 (Fase 2)
- Firmware CYD ESP32-2432S028 interior x2 (Fase 2)
- Firmware TimerCam X — captura timelapse + HTTP upload + evento MQTT (Fase 2)
- Stack de software Proxmox LXC incluyendo endpoint para fotos + panel Grafana (Fase 3)
- Rediseño + impresión carcasa interior para el CYD (Fase 1)

## [0.6.0] — 2026-03-27

### Agregado
- LXC `snipermqtt.uzc` aprovisionado (VMID 112, Debian 12, 192.168.0.79) en Proxmox
- Mosquitto 2.0.11 — auth activado (`allow_anonymous false`), un usuario por dispositivo, ACL por topic
- InfluxDB 2.8 — org `sniperstation`, bucket `sniperstation`, token escritura (Telegraf) + token lectura (Grafana)
- Telegraf 1.38 — bridge MQTT → InfluxDB como suscriptor
- Grafana 12.4.2 — datasource InfluxDB configurado, contraseña admin cambiada, registro deshabilitado
- nginx — proxy inverso HTTPS para Grafana + endpoint `/upload` para fotos TimerCam, TLS via pfSense CA
- Bot de Telegram (`software/telegram_bot/`) — desplegado como servicio systemd en snipermqtt LXC
  - Consultas en lenguaje natural via agente LLM (Claude o Ollama, seleccionable via `LLM_BACKEND`)
  - Comandos: `/start`, `/estado`/`/status`, `/riego`/`/water`, `/foto`/`/photo`, `/lang`
  - Suscriptor MQTT LWT — alerta por Telegram cuando un dispositivo se desconecta
  - Reportes por email via Resend: diario x3, semanal x1, mensual x1
  - Bilingüe EN/ES — cambiable en tiempo real con `/lang en|es`, persiste en disco
  - Menú de comandos Telegram se actualiza dinámicamente al cambiar idioma
- `software/telegram_bot/agent.py` — loop agéntico multi-LLM (Claude Haiku / Ollama)
- `software/telegram_bot/tools.py` — herramientas de consulta InfluxDB para todos los sensores
- `software/telegram_bot/reports.py` — generación de reportes por email via Resend
- `software/telegram_bot/sniperstation-bot.service` — unidad systemd con secretos via EnvironmentFile
- Hook global en Claude Code: verificación de calidad en archivos Python antes de escribir (sin imports muertos, sin toy code, strings EN/ES, comentarios en inglés)

### Infraestructura
- Secretos almacenados en `/etc/sniperstation/secrets.env` (chmod 600) en la LXC
- Certificados TLS de la CA interna de pfSense desplegados en `/etc/sniperstation/certs/`
- Nesting habilitado en LXC (`features: nesting=1`) para soporte de namespaces de Grafana
- Directorios de fotos creados: `/var/sniperstation/photos/sucufer/` y `sucurod/`

---

## [0.5.0] — 2026-03-26

### Cambiado
- Carpeta del proyecto renombrada: `sucustation/` → `sniperstation/`
- Documento principal renombrado: `sucustation_project.md` → `sniperstation_project.md`

### Agregado
- M5Stack ESP32 PSRAM Timer Camera X (OV3660, 3MP) — pedida, una unidad cubre el área de los materos
- Topics MQTT: `sniperstation/camaras/sucufer/captura` y `sucurod/captura` para eventos de foto
- Almacenamiento de fotos timelapse planificado: HTTP POST desde TimerCam → Proxmox LXC → `photos/sucufer/YYYY-MM-DD_HH.jpg`
- Panel Grafana planificado: última foto por planta
- Comando Telegram planificado: `/foto sucufer` envía la última foto
- Buck converter LM2596 ajustable (con display voltímetro) — alimenta TimerCam X desde el rail de 12V
- Wago 221-415 lever nuts (x2) — distribución del rail +12V y GND sin soldadura
- Nuevo archivo `hardware/schematics/outdoor_power.md` — diagrama completo de distribución de poder outdoor

### Decisiones
- TimerCam X (OV3660 3MP) en vez de ESP32-CAM genérico (OV2640 2MP): hardware dedicado para timelapse, batería + RTC integrados, mismo ecosistema M5Stack
- FOV 66.5° confirmado suficiente para cubrir ambos materos con una sola cámara
- Subida de fotos via HTTP POST (no MQTT): fotos muy grandes para MQTT — MQTT solo para notificación de captura
- Deep sleep por defecto cada 4h (configurable via NVS)
- LM2596 ajustable elegido sobre versión fija 5V: display voltímetro integrado elimina necesidad de multímetro
- Wago 221-415 sobre empalme directo o borneras: más fácil, sin soldadura, reutilizable

---

## [0.4.0] — 2026-03-26

### Cambiado
- Proyecto renombrado: **SucuStation → SniperStation**
- `matero1` renombrado a **SucuFer** (suculenta de Fernanda, sembrada el 22 de abril de 2024, 10 años)
- `matero2` renombrado a **SucuRod** (suculenta de Rodrigo, sembrada el 22 de abril de 2024, 6 años)
- Todos los topics MQTT actualizados: `sucustation/` → `sniperstation/`, `matero1` → `sucufer`, `matero2` → `sucurod`
- Directorio firmware renombrado: `esp8266_interior/` → `cyd_indoor/`

### Agregado
- Proyecto bilingüe EN/ES — todos los documentos disponibles en ambos idiomas (archivos .md y .es.md separados)
- Selección de idioma por dispositivo (CYD y Station-485), guardada en NVS flash, predeterminado inglés
- Strings bilingüe en firmware via `strings.h` con arrays `STR_xxx[2]`
- Vista detalle SucuFer: foto de Fernanda como fondo + humedad suelo + edad de la planta desde el 22/04/2024
- Vista detalle SucuRod: foto de Rodrigo como fondo + humedad suelo + edad de la planta desde el 22/04/2024
- Directorio `assets/photos/` con fotos originales del día de siembra (Fernanda_sucu.jpeg, Rodrigo_sucu.jpeg)

### Decisiones
- Nombres de plantas son personales — Fernanda (10) y Rodrigo (6) sembraron sus suculentas el mismo día
- Fotos de cada niño con su planta usadas como fondo del CYD en la vista de detalle
- Edad de la planta calculada dinámicamente desde la fecha de siembra (22/04/2024) usando reloj NTP

---

## [0.3.0] — 2026-03-26

### Cambiado
- Hardware unidad interior reemplazado: ESP8266 + OLED SSH1106 + TTP223 → **CYD ESP32-2432S028** (todo en uno)
- Firmware interior cambiado a librería TFT_eSPI (antes era U8g2)
- Rediseño de carcasa 3D requerido para el form factor del CYD (marco de pared simple)

### Agregado
- UI multi-vista planificada: screensaver → vista principal (todos los cuartos) → vista detalle (toca una planta)
- CYD suscribe a todos los topics MQTT → muestra exterior + ambos cuartos interiores + suelo + bombas en una pantalla
- Navegación táctil entre vistas (touch resistivo XPT2046, integrado)

### Decisiones
- CYD ESP32-2432S028 sobre ESP8266 + OLED + TTP223: pantalla color táctil, todo en uno, carcasa más simple, UI más rica
- Librería: TFT_eSPI (estándar para CYD, bien documentado)
- ESP8266 x2 y TTP223 x2 liberados de vuelta al inventario

---

## [0.2.0] — 2026-03-25

### Cambiado
- Arquitectura unidad interior expandida de 1 a **2 unidades** (Master Bedroom + Kids Bedroom)
- Unidad ESP8266 interior mejorada: se agregó pantalla OLED SSH1106 1.3" + sensor TTP223 por unidad
- Topics MQTT actualizados: `sniperstation/interior/temperatura` → `sniperstation/interior/{master|kids}/temperatura|humedad`

### Agregado
- Modelo OpenSCAD de carcasa: `hardware/enclosure/indoor_unit.scad` — paramétrico, dos piezas (shell + back plate), montaje en pared con keyhole, salida USB por abajo
- Comportamiento display OLED: screensaver (logo, tenue) → toque → activo (datos, brillante) → timeout 30s
- Lógica de brillo adaptivo: screensaver 10/255, activo 200/255, modo nocturno 00–06h apagado
- Sincronización NTP (pool.ntp.org, America/New_York) — fecha/hora mostrada en display activo
- Sensor táctil TTP223 para despertar display desde screensaver
- OLED SSH1106 1.3" agregado al BOM como pendiente de compra (pack de 2 HiLetgo)
- Carcasa interior (x2) agregada al BOM

### Decisiones
- OLED SSH1106 1.3" sobre SSD1306 0.96" — mejor visibilidad del logo
- Librería SSH1106: U8g2 (soporte nativo SH1106)
- TTP223 del inventario como interfaz táctil
- SHT30 montado en la parte superior de la carcasa 3D usando su casing plástico con ranuras de ventilación

---

## [0.1.0] — 2026-03-25

### Agregado
- Diseño y arquitectura completa del proyecto documentados en `sucustation_project.md`
- Hardware finalizado: M5Stack Station-485, SHT30 x2, BH1750, Earth Sensors x2, XKC-Y25, bombas peristálticas x2, módulos relay x2, ESP8266 NodeMCU
- Esquema de topics MQTT definido
- Lógica de riego diseñada (ciclo 6h, condicionado por suelo/humedad/nivel agua)
- Paneles dashboard Grafana planificados
- Tipos de alertas Telegram definidos
- Inventario completo catalogado (kit SunFounder + componentes adicionales)
- Estructura de documentación del proyecto creada (README, ROADMAP, TODO, CHANGELOG, hardware/)
- Lista de materiales — `hardware/BOM.md`
- Diagramas de conexión — `hardware/schematics/`
- Referencias de datasheets — `hardware/datasheets/SOURCES.md`

### Decisiones
- Bomba peristáltica sobre sumergible (precisión para suculentas)
- Un recipiente grande compartido para las dos bombas
- Sensor de nivel de agua capacitivo (XKC-Y25, sin partes móviles)
- Station-485 afuera con los materos (cables cortos)
- ESP8266 adentro para SHT30 interior (sin cables atravesando paredes)
- Proxmox LXC para el stack de software (infraestructura existente)
- SHT30 genérico en vez de ENV III M5Stack (sin stock, mismo chip)
