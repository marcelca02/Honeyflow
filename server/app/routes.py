import subprocess
#import docker
import json
import os
from flask import render_template, request, jsonify, abort
from app import app
from app.intrusion_detection import start_detection, ssh_brute_force_detection, port_scaning_detection, dns_tunneling_detection
from app.db import DBMethods
import plotly.graph_objs as go

# Variable global para saber si el docker del honeypot esta corriendo o no
docker_running = False

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/configurar_honeypots')
def configurar_honeypots():
	return render_template('configurar_honeypots.html')

@app.route('/deploy_honeypot')
def deploy_honeypot():
    return render_template('deploy_honeypot.html')


@app.route('/ejecutar_docker', methods=['POST'])
def ejecutar_docker():
    global docker_running # indicamos que se usa la variable global
    proceso = subprocess.run(['python3', 'app/run_docker_cowrie.py'])
    if proceso.returncode == 0:
        docker_running = True
        return render_template('resultado_honeypot.html', deploy=True, exito=True)
    else:
        docker_running = False # no haria falta si ya es False por defecto
        return render_template('resultado_honeypot.html', deploy=True, exito=False)


@app.route('/stop_honeypot')
def stop_honeypot():
    return render_template('stop_honeypot.html', docker_running=docker_running)


@app.route('/stop_docker', methods=['POST'])
def stop_docker():
    global docker_running
    # de momento solo habra un resultado solo uno corriendo
    proceso = subprocess.run(['docker', 'ps', '-a', '--filter', 'ancestor=honeypot1:v1','--format', '{{.ID}}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    container_id = proceso.stdout.decode().strip()
    proceso2 = subprocess.run(['docker', 'stop', container_id])
    if proceso2.returncode == 0:
        docker_running = False
        return render_template('resultado_honeypot.html', deploy=False, exito=True)
    else:
        return render_template('resultado_honeypot.html', deploy=False, exito=False)


@app.route('/show_results')
def show_results():
    # Aquí puedes definir el JSON que deseas pasar
    # En este ejemplo, estoy pasando un JSON simple como un diccionario de Python
    #os.path.join('JSON DIRECTORY', 'json file')
   
   json_file_path = os.path.join ('app', 'test.json')

   # Verificar si el archivo existe
   if os.path.exists(json_file_path):
        # Leer el contenido del archivo JSON
        with open(json_file_path, 'r') as json_file:
            datos_json = json.load(json_file)
        return render_template('show_results.html', datos=datos_json)
   else:
        # Verifica si el archivo JSON existe
        # Devuelve un código de estado HTTP 404 y un mensaje personalizado

        return render_template('error.html'), 404
