# Concurrencia y Multitarea en el microcontrolador RP2040

Este repositorio documenta una práctica enfocada en implementar y validar mecanismos de multitarea en el chip RP2040, explorando dos estrategias complementarias: simulación virtual orientada a eventos por tiempos en **Wokwi** y procesamiento paralelo real empleando ambos núcleos en hardware físico (**Raspberry Pi Pico**).

---

## ⚙️ ¿De qué trata la práctica?

El proyecto integra:

- Lectura de señales analógicas
- Indicación visual mediante LEDs
- Comunicación por puerto serie
- Sistema de latido (*heartbeat*)
- Gestión interactiva de alarmas con reconocimiento de usuario (*acknowledge*)

El concepto central de la multitarea aquí aplicada busca **evitar el bloqueo del procesador**, permitiendo atender múltiples rutinas de manera intercalada o verdaderamente simultánea.

---

## 💻 Simulación Interactiva en Wokwi

En este entorno, la concurrencia se simula ejecutando distintas tareas dentro de un bucle principal unificado, gestionadas mediante intervalos de tiempo específicos:

| Tarea | Intervalo |
|-------|-----------|
| Lectura de sensores (ADC) | Cada 20 ms |
| Lectura de pulsador | Cada 50 ms |
| Interfaz y latido (heartbeat) | Cada 500 ms |
| Reporte por monitor serie | Cada 1000 ms |

### Lógica de Umbrales y Alertas

El valor analógico del potenciómetro se transforma a una escala porcentual (0% a 100%) para definir tres escenarios operativos:

| Rango | Estado | Indicación |
|-------|--------|------------|
| Menor al 50% | **NORMAL** | LED indicador activo |
| Entre 50% y 74.9% | **WARNING** | LED de advertencia |
| Mayor o igual al 75% | **ALARM** | LED parpadeante |

**Reconocimiento (ACK):** al presionar el botón físico, el parpadeo de la alarma se detiene y pasa a un encendido fijo mientras persista la condición crítica. El *heartbeat* se encarga de evidenciar visualmente que el flujo del programa nunca se congela.

---

## ⚡ Implementación en Hardware (Raspberry Pi Pico)

La prueba sobre la tarjeta física explota la arquitectura **Dual-Core** nativa del RP2040 para lograr paralelismo real:

- **Núcleo 0 (Core 0):** administra el ciclo principal cada 1000 ms, gestiona un LED indicador y monitorea variables globales.
- **Núcleo 1 (Core 1):** ejecuta una rutina rápida cada 100 ms, conmuta un LED secundario e incrementa un contador compartido.
- **Sincronización:** se implementa un mecanismo de exclusión mutua (*lock*) para proteger el acceso concurrente al contador y evitar conflictos de memoria.

---

## 📊 Resumen de Comportamiento y Umbrales

### Niveles de Activación

```text
[ 0% ] -------- ( NORMAL ) -------- [ 50% ] -------- ( WARNING ) -------- [ 75% ] -------- ( ALARM ) -------- [ 100% ]
```

### Consideración sobre el Filtrado

El sistema contempla el uso de algoritmos de filtrado (como promedios móviles) para mitigar el ruido eléctrico propio de las entradas analógicas y evitar cambios de estado erráticos.

> **Nota:** su presencia depende de la versión específica del código cargada.

### Tabla de Resultados Obtenidos

| Acción / Componente | Comportamiento Esperado / Verificado |
|---------------------|--------------------------------------|
| Potenciómetro (nivel bajo/medio/alto) | Conmuta correctamente entre los estados NORMAL, WARNING y ALARM. |
| Latido (Heartbeat) | Oscilación constante sin interrupciones ni retrasos. |
| Monitoreo Serial | Envío fluido de datos actualizados cada segundo. |
| Pulsador (ACK) | Silencia el parpadeo de la alarma al ser presionado. |
| Prueba Dual-Core | Demuestra procesamiento paralelo exitoso empleando hilos (`_thread`). |

---

## 🎯 Conclusión

El desarrollo permitió contrastar con éxito dos paradigmas esenciales de la programación embebida: la **planificación cooperativa por tiempos** (ideal para optimizar recursos en un solo núcleo) y el **multiprocesamiento simétrico** (aprovechando los dos núcleos del RP2040 para tareas verdaderamente simultáneas y robustas).
