FROM ubuntu

# Instalar Python 3 y pip
RUN apt update && apt install -y python3 python3-pip git

# Copiar el script de descarga del honeypot
COPY install_mailoney.sh /opt/install_mailoney.sh
RUN chmod +x /opt/install_mailoney.sh

# Ejecutar el script para descargar y hacer el setup de Mailoney
RUN /opt/install_mailoney.sh

# Establecer el directorio de trabajo
WORKDIR /mailoney/

# Establecer un volumen para el registro de Mailoney
VOLUME /var/log/mailoney

# Punto de entrada para ejecutar Mailoney
ENTRYPOINT ["/usr/bin/python3", "mailoney.py", "-i", "0.0.0.0", "-p", "25", "-t", "schizo_open_relay", "-logpath", "/var/log/mailoney", "-s", "PTIhoneySMTP"]
