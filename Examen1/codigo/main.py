from machine import Pin, Timer 
import time 
 
btnA = Pin(16, Pin.IN, Pin.PULL_UP) 
btnB = Pin(17, Pin.IN, Pin.PULL_UP) 
 
ledRed = Pin(13, Pin.OUT) 
ledYellow = Pin(14, Pin.OUT) 
ledGreen = Pin(15, Pin.OUT) 
 
LOCKED = 0 
WAITING_B = 1 
ACCESS_GRANTED = 2 
SECURITY_LOCK = 3 
 
state = LOCKED 
fail_count = 0 
 
DEBOUNCE_MS = 250 
last_a_time = 0 
last_b_time = 0 
 
timer_window = Timer(-1)   
timer_access = Timer(-1)   
timer_security = Timer(-1)  
 
 
def set_leds(red=False, yellow=False, green=False): 
    ledRed.value(1 if red else 0) 
    ledYellow.value(1 if yellow else 0) 
    ledGreen.value(1 if green else 0) 
 
 
def go_locked(mensaje_listo=True): 
    global state 
    state = LOCKED 
    set_leds(red=True) 
    if mensaje_listo: 
        print("[LISTO] Intenta nuevamente con A -> B") 
 
 
def go_security_lock(): 
    global state 
    state = SECURITY_LOCK 
    set_leds(red=True) 
    print("[BLOQUEO] 3 errores detectados") 
    print("[BLOQUEO] Sistema bloqueado 10 segundos") 
    timer_security.init(
        period=10000, 
        mode=Timer.ONE_SHOT, 
        callback=_security_timeout
    ) 
 
 
def register_fail(motivo): 
    global fail_count 
    fail_count += 1 
    print("[ERROR] " + motivo) 
    print("[ERROR] Intentos fallidos: " + str(fail_count)) 
    
    if fail_count >= 3: 
        fail_count = 0 
        go_security_lock() 
    else: 
        go_locked() 
 
 
def _security_timeout(t): 
    global fail_count 
    fail_count = 0 
    go_locked() 
 
 
def _window_timeout(t): 
    if state == WAITING_B: 
        register_fail("Tiempo agotado, B no fue presionado a tiempo") 
 
 
def _access_timeout(t): 
    if state == ACCESS_GRANTED: 
        print("[INFO] Regresando a estado bloqueado") 
        go_locked() 
 
 
def handle_a(pin): 
    global last_a_time, state 
    now = time.ticks_ms() 
    
    if time.ticks_diff(now, last_a_time) < DEBOUNCE_MS: 
        return 
    
    last_a_time = now 
 
    if state == LOCKED: 
        state = WAITING_B 
        set_leds(yellow=True) 
        print("[INFO] A detectado, esperando B (5s)") 
        timer_window.init(
            period=5000, 
            mode=Timer.ONE_SHOT, 
            callback=_window_timeout
        ) 
 
    elif state == WAITING_B: 
        print("[AVISO] No presiones el boton A, ya fue detectado. Espera a presionar B.") 
 
    elif state == ACCESS_GRANTED: 
        print("[INFO] A ignorado: acceso concedido") 
 
    elif state == SECURITY_LOCK: 
        print("[INFO] A ignorado: bloqueo de seguridad") 
 
 
def handle_b(pin): 
    # CAMBIO: agregamos fail_count como variable global
    global last_b_time, state, fail_count 
    
    now = time.ticks_ms() 
    
    if time.ticks_diff(now, last_b_time) < DEBOUNCE_MS: 
        return 
    
    last_b_time = now 
 
    if state == WAITING_B: 
        timer_window.deinit() 
        state = ACCESS_GRANTED 
        
        fail_count = 0
        
        set_leds(green=True) 
        print("[ACCESO] Acceso concedido") 
        timer_access.init(
            period=3000, 
            mode=Timer.ONE_SHOT, 
            callback=_access_timeout
        ) 
 
    elif state == LOCKED: 
        register_fail("B fue presionado antes que A") 
 
    elif state == ACCESS_GRANTED: 
        print("[INFO] B ignorado: acceso concedido") 
 
    elif state == SECURITY_LOCK: 
        print("[INFO] B ignorado: bloqueo de seguridad") 
 
 
btnA.irq(trigger=Pin.IRQ_FALLING, handler=handle_a) 
btnB.irq(trigger=Pin.IRQ_FALLING, handler=handle_b) 
 
print("[INFO] Sistema iniciado: BLOQUEADO") 
go_locked(mensaje_listo=False) 
 
while True: 
    time.sleep(1)