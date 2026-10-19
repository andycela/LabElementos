# Sesión 08 - Versión Pico física con dual-core real (_thread)
# CORE 1: sensor crítico (lee ADC, filtra, clasifica, guarda en shared)
# CORE 0: UI (LEDs, heartbeat, botón, terminal)
# Los datos compartidos se protegen con lock.

from machine import Pin, ADC
from time import ticks_ms, ticks_diff, sleep_ms
import _thread

# ---------- Hardware (mismos pines que en Wokwi) ----------
adc = ADC(26)
led_normal = Pin(13, Pin.OUT)
led_warning = Pin(14, Pin.OUT)
led_alarm = Pin(15, Pin.OUT)
heartbeat = Pin(12, Pin.OUT)
button = Pin(16, Pin.IN, Pin.PULL_UP)

# ---------- Datos compartidos + candado ----------
lock = _thread.allocate_lock()
shared = {
    "raw": 0,
    "avg": 0,
    "percent": 0.0,
    "state": "INIT",
    "samples": 0,
}

FILTER_N = 10


def classify(percent):
    if percent < 50:
        return "NORMAL"
    elif percent < 75:
        return "WARNING"
    else:
        return "ALARM"


# ---------- CORE 1: tarea rápida y simple ----------
def sensor_core():
    buffer = []
    while True:
        raw = adc.read_u16()

        buffer.append(raw)
        if len(buffer) > FILTER_N:
            buffer.pop(0)
        avg = sum(buffer) // len(buffer)

        percent = avg * 100 / 65535
        state = classify(percent)

        lock.acquire()
        shared["raw"] = raw
        shared["avg"] = avg
        shared["percent"] = percent
        shared["state"] = state
        shared["samples"] += 1
        lock.release()

        sleep_ms(20)   # 50 Hz; sin prints ni LEDs aquí


def read_shared():
    """Copia segura de los datos compartidos (para usar en core 0)."""
    lock.acquire()
    snap = dict(shared)
    lock.release()
    return snap


# ---------- CORE 0: UI, alarmas, terminal ----------
def due(now, target):
    return ticks_diff(now, target) >= 0


alarm_ack = False
alarm_blink = False
last_button = 1

ui_period = 200
log_period = 1000
button_period = 50

next_ui = ticks_ms()
next_log = ticks_ms()
next_button = ticks_ms()

# Arranca el core 1
_thread.start_new_thread(sensor_core, ())

print("SHOW 2: dual-core real | Core 1 = sensor, Core 0 = UI")

while True:
    now = ticks_ms()
    data = read_shared()

    # Si la alarma desaparece, se borra el ACK
    if data["state"] != "ALARM":
        alarm_ack = False

    if due(now, next_button):
        current_button = button.value()
        if last_button == 1 and current_button == 0:
            if data["state"] == "ALARM":
                alarm_ack = True
                print(">>> ALARMA RECONOCIDA | ACK=True")
            else:
                print(">>> Botón presionado, pero no hay ALARM")
        last_button = current_button
        next_button = now + button_period

    if due(now, next_ui):
        heartbeat.toggle()
        state = data["state"]

        if state == "NORMAL":
            led_normal.on()
            led_warning.off()
            led_alarm.off()
        elif state == "WARNING":
            led_normal.off()
            led_warning.on()
            led_alarm.off()
        elif state == "ALARM":
            led_normal.off()
            led_warning.off()
            if alarm_ack:
                led_alarm.on()
            else:
                alarm_blink = not alarm_blink
                led_alarm.value(alarm_blink)

        next_ui = now + ui_period

    if due(now, next_log):
        voltage = data["avg"] * 3.3 / 65535
        print("raw=", data["raw"],
              "avg=", data["avg"],
              "voltage=", round(voltage, 2), "V",
              "state=", data["state"],
              "samples=", data["samples"],
              "ack=", alarm_ack)
        next_log = now + log_period

    sleep_ms(5)