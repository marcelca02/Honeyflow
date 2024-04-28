#!/bin/bash

# Clonar el repositorio de Mailoney desde GitHub
git clone https://github.com/phin3has/mailoney.git

# Establecer el directorio de trabajo en /opt/mailoney
cd mailoney

# Instalar las dependencias de Mailoney
pip3 install -r requirements.txt

# Crear directorio y archivo de registro de Mailoney
mkdir -p /var/log/mailoney
touch /var/log/mailoney/commands.log
