FROM python:3.9-slim-bullseye as base

FROM base as build

# Copiar el script de descarga y configuracion del honeypot
COPY install_heralding.sh /opt/install_heralding.sh
RUN chmod +x /opt/install_heralding.sh

# Ejecutar el script para descargar y configurar Heralding
RUN /opt/install_heralding.sh

FROM base

# Copiar el directorio .local desde la etapa de construcción
COPY --from=build /root/.local /root/.local

# Establecer la variable de entorno PATH
ENV PATH=/root/.local/bin:$PATH

# Comando por defecto para ejecutar Heralding
CMD ["heralding"]

# Exponer puertos
EXPOSE 21 22 23 25 80 110 143 443 465 993 995 1080 2222 3306 3389 5432 5900
