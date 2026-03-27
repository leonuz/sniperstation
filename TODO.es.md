# SniperStation — TODO

## Pendiente Comprar

- [x] ~~Adaptador DC 12V 2A, conector barrel 5.5mm~~ — pedido ✅
- [ ] Caja weatherproof outdoor — IP65 mínimo, con ranuras de ventilación o soporte para fan (Amazon)
- [x] ~~Cable Grove↔Dupont HY2.0-4P a 2.54mm female 20cm~~ — pedido ✅
- [x] ~~Buck converter DC-DC LM2596 (ajustable, display voltímetro integrado)~~ — pedido ✅
- [x] ~~OLED SSH1106 1.3" I2C 128x64~~ — reemplazado por CYD ESP32-2432S028 (todo en uno)
- [x] ~~Wago 221-415 lever nuts (5-port) x2~~ — pedidos ✅
- [x] ~~M5Stack ESP32 PSRAM Timer Camera X (OV3660)~~ — pedida ✅
- [x] ~~LM2596 buck converter x2 (ajustable, display voltímetro)~~ — pedidos ✅

## Hardware — Sin Resolver

- [ ] **Confirmar GPIO para señal OUT del XKC-Y25** — puertos B1 y B2 usados por sensores de suelo, C1 y C2 por relays. Opciones: usar un GPIO expuesto directamente o reasignar un sensor. Documentar decisión final en `hardware/schematics/station485_wiring.md`.

## Unidades Interiores — Diseño Pendiente

- [ ] Rediseñar carcasa 3D para CYD ESP32-2432S028 (marco de pared simple, ventana pantalla 2.8" + slot SHT30 arriba)
  - [ ] Medir board CYD cuando llegue
  - [ ] Actualizar indoor_unit.scad para nuevo form factor
  - [ ] **BLOQUEADO: medir casing real del SHT30** — cuando llegue el pedido
  - [ ] Exportar STL y mandar a imprimir x2
- [ ] Buscar servicio de impresión 3D económico (local u online — JLCPCB, Treatstock, biblioteca local, etc.)
- [ ] Imprimir x2 (master bedroom + kids bedroom)

## Documentación

- [ ] Traducir documentos hardware al español:
  - [ ] `hardware/BOM.es.md`
  - [ ] `hardware/schematics/station485_wiring.es.md`
  - [ ] `hardware/schematics/esp8266_interior.es.md`
  - [ ] `hardware/schematics/system_overview.es.md`
  - [ ] `hardware/enclosure/indoor_unit_design.es.md`
  - [ ] `hardware/enclosure/requirements.es.md`
- [ ] Agregar esquemáticos Fritzing o KiCad a `hardware/schematics/` una vez confirmada la asignación de GPIO
- [ ] Agregar PDFs de datasheets a `hardware/datasheets/` (actualmente solo URLs en SOURCES.md)

## Fase 1 — Hardware (no iniciado)

- [ ] Bench test I2C BH1750 (dirección esperada 0x23)
- [ ] Bench test I2C SHT30 (dirección esperada 0x44)
- [ ] Verificar sin conflicto de direcciones I2C en bus A1/A2
- [ ] Bench test lecturas analógicas Earth Sensor (valores ADC en seco/mojado)
- [ ] Bench test salida digital XKC-Y25 (HIGH/LOW con agua / sin agua)
- [ ] Prueba actuación relay + giro bomba a 12V
- [ ] Verificar presupuesto de energía: medir consumo real a 12V con sensores + 1 bomba activa

## Fase 2 — Firmware (no iniciado)

- [ ] Firmware Station-485 (ver ROADMAP Fase 2)
- [ ] Firmware CYD indoor (ver ROADMAP Fase 2)

## Fase 3 — Software (en progreso)

- [x] ~~Provisionar LXC en Proxmox~~ — snipermqtt.uzc 192.168.0.79 ✅
- [x] ~~Mosquitto 2.0.11~~ — auth + ACL, un usuario por dispositivo ✅
- [x] ~~InfluxDB 2.8~~ — org+bucket `sniperstation`, tokens escritura/lectura ✅
- [x] ~~Telegraf 1.38~~ — bridge MQTT → InfluxDB ✅
- [x] ~~Grafana 12.4.2~~ — datasource configurado, HTTPS via nginx + pfSense CA ✅
- [x] ~~Bot Telegram~~ — agente NL (Claude/Ollama), comandos, alertas LWT, reportes email, EN/ES ✅
- [ ] Dashboard Grafana — 7 paneles (esperando datos reales del ESP32)
- [ ] Endpoint HTTP para fotos TimerCam X
- [ ] Almacenamiento fotos: `photos/sucufer/YYYY-MM-DD_HH.jpg`
- [ ] Panel Grafana: última foto por planta
- [ ] 2FA (TOTP) en cuenta admin Grafana
- [ ] fail2ban para Mosquitto y Grafana

## Decisiones Pendientes

- [ ] Definir lógica de cooldown: tiempo mínimo entre ciclos de riego para evitar re-regar muy pronto
- [x] ~~Elegir librería bot Telegram~~ — python-telegram-bot 22.7 ✅
- [ ] Definir diseño del logo bitmap + layout UI para pantalla TFT CYD (screensaver + vista principal + vista detalle)
- [ ] Fotos actualizadas de Fernanda y Rodrigo con sus suculentas (las actuales del día de siembra serán reemplazadas)
