from machine import Pin
from time import sleep_ms
 
import _thread
 
led_core0 = Pin(12, Pin.OUT)
led_core1 = Pin(13, Pin.OUT)
 
led_state_a = Pin(14, Pin.OUT)
led_state_b = Pin(15, Pin.OUT)
 
core1_counter = 0
 
lock = _thread.allocate_lock()
 
#nucleo 1 - Tareas Rapidas
 
def core1_task():
    global core1_counter
    while True:
        led_core1.toggle()
        lock.acquire()
        core1_counter += 1
        lock.release()
        sleep_ms(100)
# iniciar core 1
 
_thread.start_new_thread(
    core1_task,
    ()
)
 
#core 0
 
print()
print("=======================")
print(" Demostracion Dual - Core")
print("===========================")
print()
print("LED GP12 -> Coore 0")
print("LED GP13 -> Core 1")
print()
 
 
while True:
    #heartbeat de Core 0
    led_core0.toggle()
    lock.acquire()
    count = core1_counter
    lock.release()

    print(
        "Core 0 activo |",
        "Core 1 ciclos =",
        count
    )
    led_state_a.toggle()
    led_state_b.value(
        not led_state_a.value()
    )
    sleep_ms(1000)
