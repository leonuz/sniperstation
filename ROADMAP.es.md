# SniperStation — Roadmap

## Fase 1 — Ensamblaje de Hardware
**Objetivo:** Todos los componentes físicos conectados, alimentados y verificados de forma independiente antes de cualquier firmware.

- [ ] Comprar componentes faltantes: adaptador 12V, caja outdoor IP65
- [ ] Rediseñar carcasa 3D para el CYD (marco de pared simple) cuando lleguen los boards
- [ ] Enviar carcasa a imprimir x2 (master bedroom + kids bedroom)
- [ ] Conectar Station-485 con todos los sensores Grove (BH1750, SHT30, Earth Sensors x2)
- [ ] Conectar módulos relay y bombas peristálticas
- [ ] Conectar sensor nivel XKC-Y25 (confirmar asignación de GPIO)
- [ ] Conectar CYD (master): SHT30 en conector CN1 (GPIO21/22), pull-ups 10KΩ
- [ ] Conectar CYD (kids): igual que master
- [ ] Prueba de encendido: verificar 12V → Station-485 + bombas
- [ ] Bench test de cada sensor individualmente (I2C scanner, lecturas analógicas)
- [ ] Bench test pantalla CYD con TFT_eSPI (hello world + calibración de touch)
- [ ] Configuración hardware TimerCam X
  - [ ] Probar WiFi y captura de foto de la TimerCam X
  - [ ] Montar en caja outdoor con ventana de acrílico apuntando a los materos
  - [ ] Confirmar alimentación 5V USB-C (buck converter LM2596 desde rail 12V)
  - [ ] Ajustar buck converter a 5V usando el display voltímetro integrado

---

## Fase 2 — Desarrollo de Firmware
**Objetivo:** Todos los microcontroladores leyendo sensores y publicando a MQTT.

- [ ] Firmware Station-485 (Arduino IDE)
  - [ ] Lectura I2C: BH1750 + SHT30
  - [ ] Lectura analógica humedad suelo (B1=SucuFer, B2=SucuRod)
  - [ ] Lectura digital nivel agua (XKC-Y25)
  - [ ] Control relay para bombas (C1=SucuFer, C2=SucuRod)
  - [ ] WiFi + publicación MQTT
  - [ ] Lógica de riego (ciclo 6h, RTC BM8563)
  - [ ] MQTT subscribe para comandos manuales de riego
  - [ ] Estado en pantalla 1.14" integrada
  - [ ] Soporte bilingüe EN/ES (selección por menú, guardado en NVS)
- [ ] Firmware CYD ESP32-2432S028 — idéntico para ambas unidades, `ROOM_ID` configurable (Arduino IDE)
  - [ ] Lectura SHT30 I2C via CN1 (GPIO21 SDA, GPIO22 SCL)
  - [ ] Init pantalla TFT via librería TFT_eSPI
  - [ ] Screensaver: cactus animado + resumen compacto de temperaturas (timeout 30s)
  - [ ] Vista principal: todos los cuartos + exterior + humedad suelo
  - [ ] Vista detalle: toca una planta → foto de fondo + datos + edad de planta
  - [ ] Manejo touch resistivo (XPT2046) → navegación entre vistas
  - [ ] Selección de idioma EN/ES — por dispositivo, guardado en NVS flash
  - [ ] Strings bilingüe en `strings.h` — `STR_xxx[2]` con índice `lang` (0=EN, 1=ES)
  - [ ] Brillo adaptivo: activo 255, screensaver 30, modo nocturno 00–06h apagado
  - [ ] WiFi + sincronización NTP (pool.ntp.org, America/New_York)
  - [ ] MQTT subscribe a todos los topics de sniperstation/ (muestra todos los datos)
  - [ ] MQTT publish cada 60s a `sniperstation/interior/{ROOM_ID}/temperatura|humedad`

---

## Fase 3 — Stack de Software (Proxmox LXC)
**Objetivo:** Pipeline completo de datos MQTT → dashboard Grafana + alertas Telegram.

- [ ] Provisionar contenedor LXC (Debian 12)
- [ ] Instalar y configurar broker Mosquitto
- [ ] Instalar y configurar InfluxDB 2.x
  - [ ] Crear org, bucket `sniperstation`, API token
  - [ ] Bridge MQTT → InfluxDB (Telegraf o script Python personalizado)
- [ ] Instalar y configurar Grafana
  - [ ] Conectar fuente de datos InfluxDB
  - [ ] Construir dashboard (paneles: exterior, master, kids, SucuFer, SucuRod, nivel agua)
  - [ ] Habilitar vista responsive para celular
- [ ] Bot Telegram
  - [ ] Crear bot via BotFather
  - [ ] Implementar triggers de alerta (recipiente vacío, suelo seco, temp alta, errores)
  - [ ] Implementar comando manual de riego via bot
  - [ ] Soporte bilingüe EN/ES en mensajes del bot
- [ ] Firmware TimerCam X
  - [ ] Configurar intervalo de despertar RTC (por defecto: cada 4h)
  - [ ] HTTP POST de foto al endpoint en Proxmox LXC
  - [ ] Publicar MQTT `sniperstation/camaras/sucufer/captura` después de cada toma
  - [ ] Retornar a deep sleep tras la subida (~2µA sleep)
- [ ] Servicio de almacenamiento de fotos timelapse (Proxmox LXC)
  - [ ] Endpoint HTTP para recibir fotos desde TimerCam X (Python/Flask o Nginx)
  - [ ] Guardar fotos organizadas por fecha: `photos/sucufer/YYYY-MM-DD_HH.jpg`
  - [ ] Panel Grafana: mostrar última foto por planta
  - [ ] Comando Telegram: `/foto sucufer` envía la última foto

---

## Fase 4 — Calibración en Campo
**Objetivo:** Sistema ajustado a los materos reales y el ambiente.

- [ ] Calibrar Earth Sensors con los materos reales (lecturas seco/húmedo/mojado)
- [ ] Calibrar caudal de bombas a 12V (medir ml/segundo con probeta graduada)
- [ ] Ajustar duración de riego según caudal medido
- [ ] Ajustar umbrales de seco/húmedo/mojado para la especie de suculenta
- [ ] Stress test: observar ciclo completo de riego de principio a fin
- [ ] Validar que las alertas Telegram se disparan correctamente

---

## Fase 5 — Instalación Definitiva
**Objetivo:** Instalación outdoor permanente.

- [ ] Preparación final de caja exterior (prensaestopas, ventilación, montaje)
- [ ] Instalar Station-485 en caja weatherproof outdoor
- [ ] Tender tuberías desde el recipiente de agua hasta los materos
- [ ] Ejecutar prueba de monitoreo de 72h sin supervisión
- [ ] Documentar valores finales de calibración en la config del firmware

---

## Ideas Futuras

| Feature | Componentes Necesarios |
|---|---|
| Generar GIF/video timelapse desde fotos almacenadas | ffmpeg en Proxmox LXC |
| Segunda TimerCam X (una por matero) | M5Stack TimerCam X |
| Alerta sonora local cuando recipiente vacío | Active Buzzer + Station-485 |
| Control remoto IR del riego | IR Receiver 38kHz + ESP8266 |
| Ventilador automático para la caja | Fan 5V + Relay + Termistor |
| Bomba reversible (drenar mangueras) | L293D H-Bridge |
| Expandir a más materos | MCP3008 ADC + relays adicionales |
| Display visual nivel de agua | LED Bar Graph (10 segmentos) |
| Control manual con encoder rotativo | Rotary Encoder + Station-485 |
