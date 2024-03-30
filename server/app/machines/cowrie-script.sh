#!/bin/bash

# Función para manejar errores
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Instalar dependencias
apt-get update 
apt-get install -y git python3.10-venv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind || handle_error "No se pudieron instalar las dependencias."

# Establecer contraseña para el usuario root
echo "root:root" | chpasswd || handle_error "No se pudo establecer la contraseña para el usuario 'root'."

# Crear usuario cowrie y establecer contraseña
adduser --disabled-password cowrie || handle_error "No se pudo crear el usuario 'cowrie'."
#passwd -d cowrie || handle_error "No se pudo establecer la contraseña para el usuario 'cowrie'."

# Cambiar al usuario cowrie
su - cowrie << EOF || handle_error "No se pudo iniciar cowrie."
    handle_error() {
        echo "Error: \$1" >&2
        exit 1
    }

    # Clonar el repositorio de Cowrie
    git clone http://github.com/cowrie/cowrie || handle_error "No se pudo clonar el repositorio de Cowrie."
    cd cowrie || handle_error 
    
    # Configurar entorno virtual de Python
    python3 -m venv cowrie-env || handle_error "No se pudo crear el entorno virtual de Python."
    source cowrie-env/bin/activate || handle_error "No se pudo activar el entorno virtual de Python."

    python -m pip install --upgrade pip
    python -m pip install --upgrade -r requirements.txt || handle_error "No se pudieron instalar las dependencias de Cowrie."
    
    # Iniciar Cowrie
    bin/cowrie start

EOF

# Cambiar al usuario root
su root << EOF || handle_error "No se pudo cambiar al usuario 'root'."
    handle_error() {
        echo "Error: \$1" >&2
        exit 1
    }
    #iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222 || handle_error "No se pudo configurar iptables para ssh"
    #iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223 || handle_error "No se pudo configurar iptables para telnet"

EOF

echo "Instalación y configuración completadas correctamente."

# touch /etc/authbind/byport/22 || handle_error "No se pudo crear el archivo '/etc/authbind/byport/22'."
# chown cowrie:cowrie /etc/authbind/byport/22 || handle_error "No se pudo cambiar el propietario de '/etc/authbind/byport/22'."
# chmod 770 /etc/authbind/byport/22 || handle_error "No se pudo cambiar los permisos de '/etc/authbind/byport/22'."
# pwd
# sed -i 's/AUTHBIND_ENABLED=false/AUTHBIND_ENABLED=true/' /home/cowrie/cowrie/bin/cowrie || handle_error "No se pudo habilitar authbind en Cowrie."


