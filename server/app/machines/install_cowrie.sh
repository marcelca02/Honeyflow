#!/bin/bash

# Instalar paquetes necesarios
apt-get update && apt-get install -y \
    git \
    python3-virtualenv \
    libssl-dev \
    libffi-dev \
    build-essential \
    libpython3-dev \
    python3-minimal \
    authbind \
    virtualenv \
    python3.10-venv

# Crear usuario 'cowrie'
adduser --disabled-password cowrie

# Instalar python3.10-venv
apt-get install -y python3.10-venv

# Cambiar al usuario 'cowrie'
su - cowrie << EOF
    # Clonar el repositorio de Cowrie
    git clone http://github.com/cowrie/cowrie

    # Cambiar al directorio cowrie
    cd cowrie

    # Configurar entorno virtual de Python
    python3 -m venv cowrie-env
    source cowrie-env/bin/activate

    # Actualizar pip
    python -m pip install --upgrade pip

    # Instalar requerimientos
    python -m pip install --upgrade -r requirements.txt

    # Iniciar Cowrie
    bin/cowrie start
    exit
EOF

# Instalar authbind y configurar el puerto 22
    apt-get install -y authbind
    touch /etc/authbind/byport/22
    chown cowrie:cowrie /etc/authbind/byport/22
    chmod 770 /etc/authbind/byport/22

    # Crear el archivo de configuración de Cowrie para SSH
    su - << 'EOF2'
        cat <<EOF > /home/cowrie/cowrie/etc/cowrie.cfg
[ssh]
listen_endpoints = tcp:22:interface=0.0.0.0
EOF
EOF2




