# Sesión 07 · ADC Signal Conditioning (Smart Analog Monitor)

## Objetivo de la práctica

Leer una señal analógica con el ADC de la Raspberry Pi Pico, acondicionarla con un filtro de promedio móvil, convertirla a voltaje y porcentaje, y clasificarla en tres estados (NORMAL, WARNING y ALARM) que se indican con LEDs y por el puerto serie.

## Qué es el ADC y qué significa `read_u16()`

Un **ADC** (convertidor analógico-digital) transforma un voltaje continuo, entre 0 V y 3.3 V, en un número entero que el microcontrolador puede procesar.

`read_u16()` es el método de MicroPython que lee el canal del ADC y devuelve un entero sin signo de 16 bits (*unsigned 16-bit*), es decir, un valor entre **0 y 65535**:

| Voltaje en el pin | `raw` aproximado |
|---|---|
| 0 V | 0 |
| 1.65 V | 32767 |
| 3.3 V | 65535 |

Conversiones usadas en el código:

```python
voltaje = raw * 3.3 / 65535
porcentaje = raw * 100 / 65535
```

## Circuito utilizado

Se usó una Raspberry Pi Pico con una fotoresistencia (LDR) como sensor, conectada en un divisor de voltaje con una resistencia fija de 10 kΩ. Tres LEDs indican el estado, cada uno con una resistencia de 220 Ω en serie.

```
3V3 (pin 36) ──[ LDR ]──┬── GP26 (pin 31)
                        │
                     [10 kΩ]
                        │
                    AGND (pin 33)
```



## Explicación del filtro

Se usa un **promedio móvil** de `WINDOW_SIZE = 10` muestras. Cada nueva lectura se agrega a una lista; si la lista supera 10 elementos se elimina la más antigua, y la salida del filtro es el promedio de la lista.

```python
def filter_average(raw):
    window.append(raw)
    if len(window) > WINDOW_SIZE:
        window.pop(0)
    return sum(window) / len(window)
```

- Reduce el ruido y los saltos bruscos del ADC.
- Con una lectura cada 300 ms, la señal filtrada tarda unos 3 s en alcanzar un cambio brusco de `raw`.
- El voltaje, el porcentaje y el estado se calculan a partir del valor **filtrado**, no del `raw`.

## Umbrales elegidos

| Estado | Condición (porcentaje filtrado) | LED activo |
|---|---|---|
| NORMAL | menor a 50 % | Verde |
| WARNING | de 50 % a menos de 75 % | Amarillo |
| ALARM | 75 % o más | Rojo |

```python
WARNING = 50
ALARM = 75
```

Solo se enciende un LED a la vez.

## Tabla de pruebas

| Prueba | Esperado | Resultado obtenido | PASS/FAIL |
|---|---|---|---|
| ADC mínimo | raw cercano a 0 / 0 % | raw ≈ 300 (≈ 0.5 %) | PASS |
| ADC medio | raw cercano a 32767 / 50 % | _Pendiente: completar con el valor de la prueba repetida_ | _Pendiente_ |
| ADC máximo | raw cercano a 65535 / 100 % | raw ≈ 65556 (≈ 100 %) | PASS |
| Filtro | la señal filtrada cambia suavemente | `raw` salta de golpe y `filtered` sube o baja gradualmente | PASS |
| Normal | LED verde activo | Estado NORMAL, solo el LED verde encendido | PASS |
| Warning | LED amarillo activo | Estado WARNING, solo el LED amarillo encendido | PASS |
| Alarm | LED rojo activo | Estado ALARM, solo el LED rojo encendido | PASS |
| Recuperación | vuelve de ALARM a NORMAL al bajar la señal | Al bajar la señal, el estado pasó de ALARM a WARNING y luego a NORMAL | PASS |

