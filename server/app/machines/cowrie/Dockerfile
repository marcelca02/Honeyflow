FROM ubuntu:22.04

# Copiar el script al contenedor
COPY install_cowrie.sh /tmp/install_cowrie.sh
RUN chmod +x /tmp/install_cowrie.sh

# Ejecutar el script Bash de instalación básica de Cowrie
RUN /tmp/install_cowrie.sh

# Exponer los puertos necesarios para Cowrie
EXPOSE 2222
EXPOSE 22

COPY restart_cowrie.sh /tmp/restart_cowrie.sh
RUN chmod +x /tmp/restart_cowrie.sh

COPY entry_point.sh /tmp/entry_point.sh
RUN chmod +x /tmp/entry_point.sh

# Entrypoint para ejecutar el script de reinicio de Cowrie, para que se aplique el puerto 22, y lanzar una shell
ENTRYPOINT ["/tmp/entry_point.sh"]
