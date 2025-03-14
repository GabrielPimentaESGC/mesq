#!/bin/bash

echo "AVISO: Este método força a instalação de pacotes no ambiente do sistema."
echo "Isso pode causar problemas com outros programas Python no seu sistema."
echo "É recomendado usar o método de ambiente virtual (instalar.sh) em vez disso."
echo ""
read -p "Deseja continuar? (s/n): " resposta

if [ "$resposta" != "s" ]; then
    echo "Instalação cancelada."
    exit 1
fi

echo "Instalando dependências..."
pip install --break-system-packages -r requirements.txt

echo "Instalação concluída!"
echo "Para executar o programa, use:"
echo "python app.py" 