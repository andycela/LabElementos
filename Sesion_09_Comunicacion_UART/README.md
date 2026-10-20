# Sesión 09 · Comunicación UART — CHALLENGE 09: UART Command Center

Laboratorio de Elementos Programables I · MicroPython en Raspberry Pi Pico · Thonny

## Objetivo

Construir un **protocolo de comandos pequeño, claro y comprobable**. La computadora manda comandos por USB (consola de Thonny) y la Pico los envía por **UART0** a través de un cable *loopback*. Lo que regresa por el UART se interpreta y se ejecuta sobre dos LEDs. Cada comando recibe una respuesta `ACK`, `STATUS` o `ERR`.

## Hardware

| Elemento | Pin de la Pico |
|----------|----------------|
| UART0 TX | GP0 |
| UART0 RX | GP1 |
| LED1 | GP13 |
| LED2 | GP14 |
| Jumper (loopback) | GP0 ↔ GP1 |


## 1. Qué es UART

**UART** (*Universal Asynchronous Receiver-Transmitter*) es una forma de comunicación **serial** entre dos dispositivos. Los datos viajan **bit por bit** por un solo cable. Es **asíncrona**: no existe una línea de reloj compartida. Ambos lados se ponen de acuerdo *de antemano* en la velocidad y en el formato de cada byte, y con eso saben cuándo leer cada bit.

Por eso solo hacen falta tres conexiones: **TX**, **RX** y **GND**.

## 2. TX y RX

- **TX** (*Transmit*): pin por donde el dispositivo **envía** datos.
- **RX** (*Receive*): pin por donde el dispositivo **recibe** datos.

Entre dos dispositivos distintos la conexión se **cruza**: el TX de uno va al RX del otro, y viceversa.

```
 Dispositivo A            Dispositivo B
   TX  ───────────────────►  RX
   RX  ◄───────────────────  TX
   GND ───────────────────  GND
```

## 3. Baud rate y 8N1

El **baud rate** es la velocidad de transmisión, en símbolos (aquí, bits) por segundo. **Los dos lados deben usar el mismo valor**, de lo contrario se reciben caracteres basura. Este proyecto usa:

```python
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
```

**8N1** es el formato de cada byte, y es la configuración por defecto de MicroPython:

| Parte | Significado |
|-------|-------------|
| **8** | 8 bits de datos |
| **N** | *None*: sin bit de paridad |
| **1** | 1 bit de parada |

Más el **bit de inicio** (1 bit), cada byte ocupa **10 bits** en la línea. A 9600 baud eso da unos 960 bytes por segundo, es decir, **≈ 1 ms por carácter**. La trama `SET,LED1,1\n` (11 caracteres) tarda unos 11.5 ms en viajar.

```
 línea en reposo (1)  ┌─ start ─┐┌── 8 bits de datos (LSB primero) ──┐┌─ stop ─┐
 ─────────────────────┘  (0)    └─ d0 d1 d2 d3 d4 d5 d6 d7 ──────────┘  (1)    ─────
```

## 4. USB/REPL ≠ UART

Aunque en el programa "todo sale por la misma consola", hay **dos canales distintos**:

| | USB / REPL | UART0 |
|---|-----------|-------|
| Qué es | Puerto serie virtual por el cable USB (COM3 en Windows) | Periférico de hardware con pines propios (GP0 y GP1) |
| Lo usa | Thonny, `print()` e `input()` | `uart.write()` y `uart.read()` |
| En el código | `input("CMD> ")`, `print(...)` | `uart.write(...)`, `uart.read(1)` |
| Conexión física | Cable USB a la PC | Jumper entre pines |

En la consola se distinguen por la etiqueta de cada línea:

- `USB CMD` → lo que escribiste por USB.
- `UART RX` → lo que **volvió** por el pin RX después de pasar por el UART.
- `RESP` → la respuesta que genera el programa tras interpretar esa trama.

## 5. Por qué usamos GP0 → GP1

En la Pico, **GP0 es el TX de UART0** y **GP1 es su RX**. Unirlos con un jumper crea un ***loopback***: todo lo que la Pico transmite por TX regresa por RX. Así se puede probar el protocolo completo (enviar, recibir y validar tramas) **sin necesitar un segundo dispositivo**.

Si el jumper no está conectado, ningún comando regresa y la consola muestra:

```
UART RX : SIN DATOS. Checar conexion
```

## 6. Formato de trama

Las tramas son **texto ASCII**, con campos separados por comas y terminadas en un salto de línea:

```
COMANDO,CAMPO1,CAMPO2\n
```

- El `\n` marca el **final de la trama**. El programa agrega `\n` al enviar, y `recieve_complete_line()` lee byte por byte hasta encontrarlo (ignora el `\r` sobrante).
- Si la trama no llega completa en **1000 ms**, se considera que no hay datos.
- No importan mayúsculas ni espacios alrededor de las comas: `set, led1, 1` equivale a `SET,LED1,1`.

### Comandos

| Comando | Qué hace |
|---------|----------|
| `PING` | Prueba de comunicación |
| `SET,LED1,0/1` | Apaga o enciende LED1 |
| `SET,LED2,0/1` | Apaga o enciende LED2 |
| `SET,ALL,0/1` | Apaga o enciende los dos LEDs a la vez |
| `GET,STATUS` | Reporta el estado de los LEDs |
| `TOGGLE,LED1` | Invierte el estado de un LED (también `LED2` o `ALL`) |
| `BLINK,LED2,500` | Parpadea un LED cambiando de estado cada 500 ms (rango de 50 a 10000 ms) |
| `BLINK,ALL,300` | Los dos LEDs parpadean sincronizados |
| `BLINK,LED1,0` | Detiene el parpadeo (también `LED2` o `ALL`) |
| `HELP` | Muestra la lista de comandos |

El parpadeo usa `machine.Timer`, así que sigue funcionando mientras el programa espera el siguiente comando en `input()`.

## 7. ACK, ERR y STATUS

Toda trama recibida genera exactamente **una respuesta**, que empieza con alguno de estos tres prefijos:

| Prefijo | Significado | Ejemplo |
|---------|-------------|---------|
| `ACK` | El comando fue válido y **se ejecutó** | `ACK,LED1,1` |
| `STATUS` | Respuesta a `GET,STATUS` con el estado de los LEDs | `STATUS,LED1,1,LED2,0` |
| `ERR` | El comando fue **rechazado**; no se modifica ningún LED | `ERR,BAD_DEVICE` |

### Códigos de error

| Código | Cuándo aparece | Ejemplo |
|--------|----------------|---------|
| `ERR,UNKNOWN_FRAME` | El texto no es ningún comando conocido | `texto libre` |
| `ERR,BAD_SET_FRAME` | `SET` sin los 3 campos | `SET,LED1` |
| `ERR,BAD_TOGGLE_FRAME` | `TOGGLE` sin los 2 campos | `TOGGLE` |
| `ERR,BAD_BLINK_FRAME` | `BLINK` sin los 3 campos | `BLINK,LED1` |
| `ERR,BAD_GET_FRAME` | `GET` con algo
