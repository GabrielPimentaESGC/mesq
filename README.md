# Controle de Carrinho Raspberry Pi

Este projeto implementa um sistema de controle para um carrinho robótico baseado em Raspberry Pi, utilizando um smartphone como controle remoto.

## Componentes de Hardware

- Raspberry Pi 4B
- Módulo L298N para controle dos motores
- 2 motores DC (esquerdo e direito)
- Buzzer
- Webcam (futura implementação)
- Bateria para alimentação

## Funcionalidades

- Controle direcional via joystick virtual
- Acionamento de buzina
- Controle de bagageira (a ser implementado)
- Funcionalidade de falar (a ser implementado)
- Transmissão de vídeo da webcam (futura implementação)

## Requisitos de Software

- Python 3.7+
- Flask
- RPi.GPIO (apenas na Raspberry Pi)
- Navegador web moderno no smartphone

## Instalação na Raspberry Pi

### Método 1: Usando ambiente virtual (Recomendado)

Este método evita problemas com o erro "externally-managed-environment":

```bash
# Baixe o projeto
git clone https://github.com/seu-usuario/controle-carrinho-raspberry.git
cd controle-carrinho-raspberry

# Torne o script de instalação executável
chmod +x instalar.sh

# Execute o script de instalação
./instalar.sh
```

Para executar o programa após a instalação:

```bash
./executar.sh
```

### Método 2: Instalação forçada (Não recomendado)

Use este método apenas se o método 1 não funcionar:

```bash
# Torne o script executável
chmod +x instalar_alternativo.sh

# Execute o script
./instalar_alternativo.sh
```

### Método 3: Instalação manual

Se preferir instalar manualmente:

```bash
# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute o programa
python app.py
```

## Modo de Simulação

O programa agora inclui um modo de simulação que funciona mesmo sem a biblioteca RPi.GPIO. Isso permite testar a interface em qualquer computador, não apenas na Raspberry Pi.

Quando executado em um computador que não é uma Raspberry Pi ou sem a biblioteca RPi.GPIO, o programa automaticamente entra no modo de simulação e exibe mensagens no console em vez de controlar os pinos GPIO.

## Acesso à Interface Web

1. Conecte seu smartphone à mesma rede Wi-Fi da Raspberry Pi
2. Descubra o endereço IP da sua Raspberry Pi:
   ```
   hostname -I
   ```
3. Abra o navegador no smartphone e acesse:
   ```
   http://[IP-DA-RASPBERRY-PI]:5000
   ```

## Conexões do Hardware

### Módulo L298N
- Motor Esquerdo:
  - Enable: GPIO 25
  - Input 1: GPIO 24
  - Input 2: GPIO 23
  
- Motor Direito:
  - Enable: GPIO 17
  - Input 1: GPIO 27
  - Input 2: GPIO 22

### Buzzer
- Pino de sinal: GPIO 18

## Uso

1. Conecte seu smartphone à mesma rede Wi-Fi da Raspberry Pi
2. Abra o navegador e acesse o endereço do servidor
3. Use o joystick virtual para controlar a direção do carrinho
4. Use os botões para acionar funções especiais (buzina, bagageira, etc.)

## Personalização

Você pode ajustar os pinos GPIO e outras configurações editando as constantes no início do arquivo `app.py`.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 