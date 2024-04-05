import subprocess
#import docker
from flask import render_template, request, json
from app import app
from app.intrusion_detection import start_detection, ssh_brute_force_detection, port_scaning_detection, dns_tunneling_detection
from app.db import DBMethods

# Variable global para saber si el docker del honeypot esta corriendo o no
docker_running = False

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/deploy_honeypot')
def deploy_honeypot():
    return render_template('deploy_honeypot.html')


@app.route('/ejecutar_docker', methods=['POST'])
def ejecutar_docker():
    global docker_running # indicamos que se usa la variable global
    proceso = subprocess.run(['python3', 'run_docker_cowrie.py'])
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
