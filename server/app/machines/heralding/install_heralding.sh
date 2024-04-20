#!/bin/bash

# Instalar Git
apt-get update && apt-get install -y git

# Clonar el repositorio de Heralding desde GitHub
git clone https://github.com/johnnykv/heralding.git /opt/heralding
cd /opt/heralding

# Instalar las dependencias
apt-get install -y libpq-dev gcc \
&& pip install --user --no-cache-dir -r requirements.txt \
&& rm -rf /var/lib/apt/lists/*

# Instalar Heralding
python setup.py install --user
