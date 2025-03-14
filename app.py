from flask import Flask, render_template, request, jsonify
import time
import threading
import os
import sys

# Verificar se estamos rodando em uma Raspberry Pi
RUNNING_ON_PI = os.uname()[4].startswith('arm') if hasattr(os, 'uname') else False

# Tentar importar RPi.GPIO, se não estiver disponível, usar modo de simulação
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    print("AVISO: RPi.GPIO não disponível. Usando modo de simulação.")
    GPIO_AVAILABLE = False

app = Flask(__name__)

# Configuração dos pinos GPIO
# Motor Esquerdo
MOTOR_ESQUERDO_ENABLE = 25
MOTOR_ESQUERDO_PIN1 = 24
MOTOR_ESQUERDO_PIN2 = 23

# Motor Direito
MOTOR_DIREITO_ENABLE = 17
MOTOR_DIREITO_PIN1 = 27
MOTOR_DIREITO_PIN2 = 22

# Buzzer
BUZZER_PIN = 18

# Variáveis para simulação
motor_esquerdo_estado = {'direcao': 'parar', 'velocidade': 0}
motor_direito_estado = {'direcao': 'parar', 'velocidade': 0}
buzzer_estado = False

# Configuração inicial do GPIO
def setup_gpio():
    if not GPIO_AVAILABLE:
        print("Modo de simulação: GPIO seria configurado aqui")
        return
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Configuração dos pinos do motor esquerdo
    GPIO.setup(MOTOR_ESQUERDO_ENABLE, GPIO.OUT)
    GPIO.setup(MOTOR_ESQUERDO_PIN1, GPIO.OUT)
    GPIO.setup(MOTOR_ESQUERDO_PIN2, GPIO.OUT)
    
    # Configuração dos pinos do motor direito
    GPIO.setup(MOTOR_DIREITO_ENABLE, GPIO.OUT)
    GPIO.setup(MOTOR_DIREITO_PIN1, GPIO.OUT)
    GPIO.setup(MOTOR_DIREITO_PIN2, GPIO.OUT)
    
    # Configuração do buzzer
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    
    # Configuração PWM para controle de velocidade
    global pwm_motor_esquerdo, pwm_motor_direito
    pwm_motor_esquerdo = GPIO.PWM(MOTOR_ESQUERDO_ENABLE, 100)
    pwm_motor_direito = GPIO.PWM(MOTOR_DIREITO_ENABLE, 100)
    
    pwm_motor_esquerdo.start(0)
    pwm_motor_direito.start(0)

# Funções de controle dos motores
def motor_esquerdo(direcao, velocidade):
    global motor_esquerdo_estado
    
    velocidade = max(0, min(100, velocidade))
    motor_esquerdo_estado = {'direcao': direcao, 'velocidade': velocidade}
    
    if not GPIO_AVAILABLE:
        print(f"Simulação: Motor esquerdo - Direção: {direcao}, Velocidade: {velocidade}")
        return
    
    pwm_motor_esquerdo.ChangeDutyCycle(velocidade)
    
    if direcao == 'frente':
        GPIO.output(MOTOR_ESQUERDO_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_ESQUERDO_PIN2, GPIO.LOW)
    elif direcao == 'tras':
        GPIO.output(MOTOR_ESQUERDO_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_ESQUERDO_PIN2, GPIO.HIGH)
    else:  # parar
        GPIO.output(MOTOR_ESQUERDO_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_ESQUERDO_PIN2, GPIO.LOW)

def motor_direito(direcao, velocidade):
    global motor_direito_estado
    
    velocidade = max(0, min(100, velocidade))
    motor_direito_estado = {'direcao': direcao, 'velocidade': velocidade}
    
    if not GPIO_AVAILABLE:
        print(f"Simulação: Motor direito - Direção: {direcao}, Velocidade: {velocidade}")
        return
    
    pwm_motor_direito.ChangeDutyCycle(velocidade)
    
    if direcao == 'frente':
        GPIO.output(MOTOR_DIREITO_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_DIREITO_PIN2, GPIO.LOW)
    elif direcao == 'tras':
        GPIO.output(MOTOR_DIREITO_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_DIREITO_PIN2, GPIO.HIGH)
    else:  # parar
        GPIO.output(MOTOR_DIREITO_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_DIREITO_PIN2, GPIO.LOW)

# Função para controlar o buzzer
def acionar_buzzer(duracao=0.5):
    global buzzer_estado
    
    buzzer_estado = True
    
    if not GPIO_AVAILABLE:
        print(f"Simulação: Buzzer acionado por {duracao} segundos")
        time.sleep(duracao)
        buzzer_estado = False
        return
    
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duracao)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    buzzer_estado = False

# Thread para acionar o buzzer sem bloquear o servidor
def buzzer_thread():
    acionar_buzzer()

# Rotas da aplicação web
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify({
        'running_on_pi': RUNNING_ON_PI,
        'gpio_available': GPIO_AVAILABLE,
        'motor_esquerdo': motor_esquerdo_estado,
        'motor_direito': motor_direito_estado,
        'buzzer': buzzer_estado
    })

@app.route('/controle', methods=['POST'])
def controle():
    data = request.get_json()
    
    if 'ping' in data:
        return jsonify({'status': 'success'})
    
    if 'joystick' in data:
        x = data['joystick']['x']  # -1 (esquerda) a 1 (direita)
        y = data['joystick']['y']  # -1 (para trás) a 1 (para frente)
        
        # Cálculo da velocidade e direção para cada motor
        velocidade_base = 70  # Velocidade base (0-100)
        
        # Ajuste de velocidade com base na posição Y do joystick
        velocidade_y = abs(y) * velocidade_base
        
        # Direção com base no sinal de Y
        direcao = 'frente' if y > 0 else 'tras' if y < 0 else 'parar'
        
        # Ajuste diferencial para curvas com base na posição X
        ajuste_x = abs(x) * velocidade_base * 0.5
        
        if x > 0:  # Virando à direita
            velocidade_esquerda = velocidade_y + ajuste_x
            velocidade_direita = velocidade_y - ajuste_x
        elif x < 0:  # Virando à esquerda
            velocidade_esquerda = velocidade_y - ajuste_x
            velocidade_direita = velocidade_y + ajuste_x
        else:  # Sem curva
            velocidade_esquerda = velocidade_y
            velocidade_direita = velocidade_y
        
        # Garantir que as velocidades estejam no intervalo correto
        velocidade_esquerda = max(0, min(100, velocidade_esquerda))
        velocidade_direita = max(0, min(100, velocidade_direita))
        
        # Se Y for próximo de zero, parar os motores
        if abs(y) < 0.1:
            motor_esquerdo('parar', 0)
            motor_direito('parar', 0)
        else:
            motor_esquerdo(direcao, velocidade_esquerda)
            motor_direito(direcao, velocidade_direita)
    
    if 'buzzer' in data and data['buzzer']:
        # Iniciar o buzzer em uma thread separada para não bloquear
        threading.Thread(target=buzzer_thread).start()
    
    if 'bagageira' in data:
        # Código para controlar a bagageira (a ser implementado)
        print("Simulação: Bagageira acionada")
        pass
    
    if 'falar' in data:
        # Código para a funcionalidade de falar (a ser implementado)
        print("Simulação: Função falar acionada")
        pass
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    try:
        setup_gpio()
        # Mostrar informações sobre o ambiente
        print(f"Rodando em Raspberry Pi: {RUNNING_ON_PI}")
        print(f"GPIO disponível: {GPIO_AVAILABLE}")
        if not GPIO_AVAILABLE:
            print("MODO DE SIMULAÇÃO ATIVADO - Os comandos serão apenas impressos no console")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        if GPIO_AVAILABLE:
            GPIO.cleanup() 