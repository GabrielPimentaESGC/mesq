#!/bin/bash

echo "Instalando dependências do sistema..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev

echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

echo "Instalando dependências Python..."
pip install -r requirements.txt

echo "Instalação concluída!"
echo "Para executar o programa, use:"
echo "source venv/bin/activate"
echo "python app.py" 