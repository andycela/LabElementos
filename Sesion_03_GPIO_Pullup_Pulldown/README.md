# Semáforo para Peatones con Botón (Raspberry Pi Pico)

En esta sesión se trabaja con los pines GPIO de la Raspberry Pi Pico configurados como entradas digitales. Las prácticas avanzan paso a paso hasta construir un semáforo que responde cuando un peatón presiona un botón.

## Estructura del proyecto

* `01_button_read`: Primer acercamiento a la lectura de un botón. Se detecta si está presionado o no usando las resistencias internas pull-up y pull-down de la Pico.
* `02_button_debounce`: Solución al rebote mecánico del botón. Se agrega un filtro por software (debounce) para que una sola pulsación no se registre varias veces por error.
* `03_semaforo_peatonal`: Proyecto integrador. El semáforo permanece en su ciclo normal hasta que se detecta una pulsación válida del botón; en ese momento cambia de estado y ejecuta la secuencia para que el peatón pueda cruzar de forma segura.
