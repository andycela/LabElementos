Sesión 06 – PWM con Motor DC y driver L298N

Laboratorio de Elementos Programables- Andrea Ceja Lara 
1. ¿Qué es PWM?
PWM (Pulse Width Modulation, modulación por ancho de pulso) es una técnica que genera una señal digital que alterna rápidamente entre ALTO (3.3 V/5 V) y BAJO (0 V). Lo que se varía es el ciclo de trabajo (duty cycle): el porcentaje del periodo en que la señal está en ALTO.
Duty 0 % → motor detenido
Duty 50 % → el motor recibe, en promedio, la mitad de la potencia
Duty 100 % → motor a máxima velocidad
El motor no ve los pulsos individuales: por su inercia mecánica y eléctrica responde al valor promedio del voltaje. Así se controla la velocidad sin usar un voltaje analógico variable y con muy poca pérdida de energía.

2.Pines IN1 / IN2 / ENA del L298N
El L298N es un puente H doble. Para un motor se usan tres pines de control:
-Pin	Función
-IN1	Entrada digital de dirección (lado A)
-IN2	Entrada digital de dirección (lado B)

ENA:Habilitación del canal; aquí se aplica la señal PWM para controlar la velocidad

3.Rampa
Una rampa consiste en subir o bajar el duty cycle poco a poco (por ejemplo, de 5 % en 5 % con una pausa corta) en lugar de saltar de golpe a la velocidad objetivo.

¿Por qué se usa?
Evita picos de corriente en el arranque, que pueden bajar el voltaje de la fuente y reiniciar el microcontrolador.
Reduce el esfuerzo mecánico en el motor y los engranes.
Reduce el estrés térmico en el L298N.
Da un movimiento más suave y controlado.

4.Cambio seguro de dirección

Invertir IN1/IN2 de golpe con el motor girando es peligroso: genera picos de corriente y fuerza el cambio de sentido contra la inercia. La secuencia segura implementada es:

-Bajar la velocidad con rampa hasta duty = 0 %.
-Esperar un tiempo corto (ej. 200–500 ms) a que el motor se detenga.
-Cambiar IN1/IN2 al nuevo sentido (con PWM en 0 %).
-Subir la velocidad con rampa hasta el duty deseado.
Así el motor nunca recibe una inversión brusca con carga.

5.Tabla de pruebas (por completar, cuando ya esté el circuito físico)

6. Problemas encontrados (por completar)
