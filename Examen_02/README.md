# Examen Práctico 02 – Sistema de Control Serial Inteligente
Laboratorio de Elementos Programables · UART • PWM • ADC • Entrada digital • Dual-Core

## Integrantes
Andrea Ceja Lara

**Fecha:** 23/10/2026 · **Placa:** Raspberry Pi Pico · **Firmware:** MicroPython · **IDE:** Thonny

## Descripción

La Pico recibe comandos de texto escritos en el shell de Thonny (USB), los envía por el UART0 en loopback (GP0 → GP1) y los interpreta al recibirlos. Controla un LED digital y un LED con PWM, lee un ADC y un botón, y mantiene una adquisición en segundo plano en el Core 1 sin detener la comunicación del Core 0.

## Pines usados

| Elemento | Pin | Función |
|---|---|---|
| LED digital | GP13 | Encendido/apagado |
| LED PWM | GP15 | Brillo 0–100 % (1 kHz) |
| Botón | GP16 | Funcionamiento como latch (presiono una vez =1, vuelvo a presionarlo= 0), y se repite ese ciclo|
| ADC | GP26 / ADC0 | Sensor o potenciómetro 0–3.3 V |
| UART0 TX | GP0 | Transmisión (9600 baud, 8N1) |
| UART0 RX | GP1 | Recepción; **jumper GP0 ↔ GP1** (loopback) |

### Diagrama de conexión

```
GP13 ──[330 Ω]──►|── GND        (LED digital)
GP15 ──[330 Ω]──►|── GND        (LED PWM)
GP16 ──── botón ──── GND        (PULL_UP interno)
GP0 (TX) ──── jumper ──── GP1 (RX)   (loopback UART0)
3V3 ──── potenciómetro ──── GND
              └── cursor ── GP26 (ADC0)
```

> Ajustar el diagrama si se usó shield, LDR o NTC.

## Arquitectura

| Core 0 (hilo principal) | Core 1 (`_thread`) |
|---|---|
| Recibe y procesa comandos seriales | Lee el ADC cada 100 ms (promedio de 8 lecturas) |
| Controla LED digital y PWM | Actualiza `adc_raw`, `adc_pct` |
| Genera ACK / ERR / STATUS | Incrementa `sample_count` |
| Reporta el evento del botón | Detecta el botón con antirrebote (30 ms) |

**Flujo TX/RX:** el comando escrito en Thonny llega por USB → Core 0 lo transmite por UART0 (GP0, TX) → el jumper lo regresa a GP1 (RX) → Core 0 lee la línea completa (`\n`) → `handle_frame()` la interpreta, actúa sobre las salidas y responde `ACK` / `ERR` / `STATUS`. Si no llega nada, muestra `UART RX : SIN DATOS`.

Las variables compartidas se protegen con un `lock`. La conversión PWM es `duty_u16 = n * 65535 // 100`.

## Comandos

| Comando | Acción | Respuesta |
|---|---|---|
| `PING` | Comprueba comunicación | `PONG` |
| `LED,0` / `LED,1` | Apaga / enciende el LED digital | `ACK,LED,0/1` |
| `PWM,n` (0–100) | Ajusta el brillo del LED PWM | `ACK,PWM,n` |
| `STATUS` | Estado completo | `STATUS,LED=…,PWM=…,ADC=…,BTN=…,SAMPLES=…` |
| `PWM,POT` _(bonus)_ | El LED PWM se enciende al % del potenciómetro y sigue cambiando mientras lo giras (se cancela con `PWM,n` o `ALL,n`) | `ACK,PWM,POT` |
| `ALL,0` / `ALL,1` | LED digital + PWM juntos (0 → LED apagado y PWM 0 %; 1 → LED encendido y PWM 100 %) | `ACK,ALL,0/1` |
| `TOGGLE` _(bonus)_ | Invierte el LED digital | `ACK,TOGGLE,0/1` |
| `HELP` _(bonus)_ | Lista los comandos | `HELP,...` |

En `STATUS`, `ADC` es el porcentaje 0–100 % y `BTN` funciona como **latch**: cada pulsación del botón invierte su estado (0 → 1 → 0 …) y ningún comando lo modifica. Al presionar el botón se imprime `EVENT,BTN,n` (n = nuevo estado) seguido de un `STATUS`.


## Pruebas realizadas

| # | Prueba | Resultado esperado | check/no check |
|---|---|---|---|
| 1 | `PING` | `PONG` | check|
| 2 | `LED,1` / `LED,0` | LED enciende / apaga |check|
| 3 | `PWM,25` / `PWM,50` / `PWM,100` | Brillo aumenta | check |
| 4 | Mover potenciómetro + `STATUS` | `ADC` cambia | check |
| 5 | Presionar botón (y otra vez) | `EVENT,BTN,1` y luego `EVENT,BTN,0`; `STATUS` refleja el estado | check |
| 6 | `ALL,1` / `ALL,0` | Ambos LEDs cambian | check |
| 7 | `STATUS` dos veces con pausa | `SAMPLES` aumenta | check |
| 8 | `PWM,150`, `LED,7`, `PWM`, `HOLA` | Errores y el sistema continúa | check |

