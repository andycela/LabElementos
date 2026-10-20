| # | Comando | Esperado | Respuesta de mi código | Qué hace / qué valida | PASS / FAIL |
|---|---------|------------------------|------------------------|------------------------|-------------|
| 1 | `PING` | `ACK,PONG` | `ACK,PONG` | Comprueba que la trama viaja por UART (TX→RX) y que el programa la interpreta | PASS |
| 2 | `SET,LED1,1` | `ACK,LED1,1` | `ACK,LED1,1` | Enciende LED1 (GP13) |PASS|
| 3 | `SET,LED2,1` | `ACK,LED2,1` | `ACK,LED2,1` | Enciende LED2 (GP14) | PASS |
| 4 | `SET,ALL,0` | `ACK,ALL,0` | `ACK,ALL,0` | Apaga los dos LEDs a la vez |PASS |
| 5 | `GET,STATUS` | `STATUS,...` | `STATUS,LED1,0,LED2,0` | Lee el estado real de los pines; da 0 y 0 porque la prueba 4 los apagó |PASS|
| 6 | `SET,LED3,1` | `ERR,...` | `ERR,BAD_DEVICE` | Rechaza un dispositivo que no existe y no cambia ningún LED | PASS|
| 7 | `SET,LED1,9` | `ERR,...` | `ERR,BAD_VALUE` | Rechaza un valor distinto de 0 o 1 y no cambia LED1 |PASS |
| 8 | `texto libre` | `ERR,...` | `ERR,UNKNOWN_FRAME` | Rechaza cualquier texto que no sea un comando conocido |PASS |


## Pruebas extra (Niveles 2 y 3)

| # | Comando | Respuesta de mi código | Qué hace / qué valida | PASS / FAIL |
|---|---------|------------------------|------------------------|-------------|
| 9 | `SET,ALL,1` | `ACK,ALL,1` | Enciende los dos LEDs al mismo tiempo | PASS|
| 10 | `SET,LED1` | `ERR,BAD_SET_FRAME` | Valida que la trama tenga todos sus campos |PASS|
| 11 | `TOGGLE,LED1` | `ACK,TOGGLE,LED1` | Invierte el estado de LED1 | PASS |
| 12 | `BLINK,LED2,500` | `ACK,BLINK,LED2,500` | LED2 cambia de estado cada 500 ms | PASS |
| 13 | `BLINK,LED2,100` | `ACK,BLINK,LED2,100` | Cambia la velocidad del parpadeo sin detenerlo antes |PASS|
| 14 | `BLINK,ALL,300` | `ACK,BLINK,ALL,300` | Los dos LEDs parpadean sincronizados |PASS |
| 15 | `BLINK,LED1,5` | `ERR,BAD_VALUE_RANGE` | Rechaza intervalos fuera del rango de 50 a 10000 ms | PASS|
| 16 | `BLINK,LED2,0` | `ACK,BLINK,LED2,0` | Detiene el parpadeo de LED2 | PASS|
| 17 | `HELP` | `ACK,HELP` + lista de comandos | Muestra la ayuda con todos los comandos disponibles | PASS |
