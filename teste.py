from flask import Flask, render_template, Response, request, jsonify
import cv2
import sys
import time
import threading

# Verifica se o sistema é Windows ou Raspberry Pi
ON_WINDOWS = sys.platform == 'win32'

# Configuração dos pinos (altere conforme necessário)
if not ON_WINDOWS:
    import RPi.GPIO as GPIO
    IN1 = 17
    IN2 = 27
    IN3 = 22
    IN4 = 23
    ENA = 18
    ENB = 24
    BUZZER_PIN = 25

    # Inicialização do GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(ENB, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    # Inicialização do PWM
    pwm_a = GPIO.PWM(ENA, 1000)
    pwm_b = GPIO.PWM(ENB, 1000)
    pwm_a.start(0)
    pwm_b.start(0)
else:
    print("Executando no Windows. Modo de simulação ativado.")

# Inicialização do Flask
app = Flask(__name__)

# Variáveis globais para controle de potência dos motores
left_motor_power = 0
right_motor_power = 0

# Funções de controle do carro
def set_motor_power(left_power, right_power):
    global left_motor_power, right_motor_power
    left_motor_power = max(-100, min(100, left_power))  # Limita entre -100 e 100
    right_motor_power = max(-100, min(100, right_power))  # Limita entre -100 e 100

    if not ON_WINDOWS:
        # Define a direção e a potência dos motores
        if left_motor_power > 0:
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
        else:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
        pwm_a.ChangeDutyCycle(abs(left_motor_power))

        if right_motor_power > 0:
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.LOW)
        else:
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.HIGH)
        pwm_b.ChangeDutyCycle(abs(right_motor_power))
    else:
        print(f"Simulação: Motor Esquerdo = {left_motor_power}%, Motor Direito = {right_motor_power}%")

def stop():
    set_motor_power(0, 0)

def beep():
    if not ON_WINDOWS:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
    else:
        print("Simulação: Buzzer ativado.")

# Função para gerar frames da câmera
def generate_frames():
    if not ON_WINDOWS:
        camera = cv2.VideoCapture(0)
    else:
        # No Windows, use uma câmera virtual ou um vídeo de teste
        camera = cv2.VideoCapture(0)  # Altere para um arquivo de vídeo se necessário
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Rota para a interface web
@app.route('/')
def index():
    return render_template('index.html')

# Rota para o vídeo ao vivo
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Rota para controle do carro
@app.route('/control', methods=['POST'])
def control():
    data = request.json
    command = data.get('command')
    left_power = data.get('left_power', 0)
    right_power = data.get('right_power', 0)

    if command == 'set_power':
        set_motor_power(left_power, right_power)
    elif command == 'stop':
        stop()
    elif command == 'beep':
        beep()

    return jsonify(status="success", left_power=left_motor_power, right_power=right_motor_power)

# Função para limpeza do GPIO
def cleanup_gpio():
    if not ON_WINDOWS:
        GPIO.cleanup()

# Inicialização do servidor Flask
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        cleanup_gpio()