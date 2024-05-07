import subprocess
#import docker
import json
import os
from flask import render_template, request, jsonify, abort
from app import app
from app.intrusion_detection import start_detection, ssh_brute_force_detection, port_scaning_detection, dns_tunneling_detection
from app.db import DBMethods
import pandas as pd
from app.kubernetes import init_k8s, create_cowrie_pod, get_pods, delete_pod

# Variable global para saber si el docker del honeypot esta corriendo o no
docker_running = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/configurar_honeypots')
def configurar_honeypots():
    return render_template('configurar_honeypots.html')

@app.route('/about_project')
def about_project():
    return render_template('about_project.html')


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

@app.route('/k8s_cowrie')
def k8s_cowrie():
    v1 = init_k8s()
    create_cowrie_pod(v1)
    pods = get_pods(v1)
    return "Pods: " + str(pods)
    


@app.route('/honeypots_analysis')
def honeypots_analysis():
    # Lista de honeypots disponibles con sus nombres y rutas HTML asociadas
    honeypots = [
        {'name': 'Cowrie', 'html_route': 'show_results_cowrie'},
        {'name': 'Heralding', 'html_route': 'show_results_heralding'},
        {'name': 'Mailoney', 'html_route': 'show_results_mailoney'}
        # Agrega más honeypots según sea necesario con sus nombres y rutas HTML correspondientes
    ]

    return render_template('honeypots_analysis.html', honeypots=honeypots)

@app.route('/show_results_cowrie')
def show_results_cowrie():
    # Ejecutar comando docker para copiar archivo JSON
    processo = subprocess.run(['docker', 'cp', 'cowrie:/home/cowrie/cowrie/var/log/cowrie/cowrie.json', 'app/data_analysis/cowrie/cowrie.json'])
    
    if processo.returncode == 0:
        json_file_path = os.path.join('app', 'data_analysis', 'cowrie', 'cowrie.json')
        
        # Verificar si el archivo existe
        if os.path.exists(json_file_path):
            try:
                # Abre el archivo JSON y lee su contenido
                with open(json_file_path, 'r') as json_file:
                      data_str = json_file.read()
                # Divide la cadena en varias líneas
                lines = data_str.splitlines()
                # Combina las líneas en un solo objeto JSON
                combined_data = '[' + ','.join(lines) + ']'

                # Convierte el objeto JSON combinado en un arreglo de Python
                data = json.loads(combined_data)
                # Crea un diccionario de DataFrames en función del valor de la clave 'eventid'
                dataframes = {}
                for d in data:
                    eventid = d['eventid']
                    if eventid not in dataframes:
                        dataframes[eventid] = pd.DataFrame(columns=d.keys())
                    dataframes[eventid] = pd.concat([dataframes[eventid], pd.DataFrame([d])], ignore_index=True)                
                    if 'fingerprint'in d.keys():
                        dataframes[eventid].drop('fingerprint', axis=1, inplace=True)
                    if 'key'in d.keys():
                        dataframes[eventid].drop('key', axis=1, inplace=True)
                    if 'kexAlgs'in d.keys():
                        dataframes[eventid].drop('kexAlgs', axis=1, inplace=True)
                    if 'keyAlgs'in d.keys():
                        dataframes[eventid].drop('keyAlgs', axis=1, inplace=True)
                    if 'hasshAlgorithms'in d.keys():
                        dataframes[eventid].drop('hasshAlgorithms', axis=1, inplace=True)
                    if 'encCS'in d.keys():
                        dataframes[eventid].drop('encCS', axis=1, inplace=True)
                    if 'macCS'in d.keys():
                        dataframes[eventid].drop('macCS', axis=1, inplace=True)
                    if 'langCS'in d.keys():
                         dataframes[eventid].drop('langCS', axis=1, inplace=True)
                    if 'compCS'in d.keys():
                         dataframes[eventid].drop('compCS', axis=1, inplace=True)
                # Render the template with the DataFrames
                return render_template('show_results_cowrie.html', dataframes=dataframes)
            except json.JSONDecodeError as error:
                print(f"Error al leer archivo JSON: {error}")
                return "Error al leer archivo JSON", 500
        else:
            print("Archivo JSON no encontrado")
            return "Archivo JSON no encontrado", 404
    else:
        print("Error al ejecutar comando docker")
        return "Error al ejecutar comando docker", 500
        #Verifica si el archivo JSON existe
        #Devuelve un código de estado HTTP 404 y un mensaje personalizado
    #else:
    #    return render_template('error.html'), 404

@app.route('/show_results_heralding')
def show_results_heralding():
    processo = subprocess.run(['docker', 'cp', 'heralding:/log_session.json', 'app/data_analysis/heralding/heralding.json'])
    if processo.returncode == 0:
        json_file_path = os.path.join('app', 'data_analysis', 'heralding', 'heralding.json')
        
        # Verificar si el archivo existe
        if os.path.exists(json_file_path):
            try:
                # Abre el archivo JSON y lee su contenido
                with open(json_file_path, 'r') as json_file:
                      data_str = json_file.read()
                # Divide la cadena en varias líneas
                lines = data_str.splitlines()
                # Combina las líneas en un solo objeto JSON
                combined_data = '[' + ','.join(lines) + ']'

                # Convierte el objeto JSON combinado en un arreglo de Python
                data = json.loads(combined_data)

                dataframe = pd.DataFrame(data)
                # Filtrar los datos para crear un DataFrame específico para auth_attempts
                # Crear un DataFrame para almacenar los datos de auth_attempts
                auth_attempts_df = pd.DataFrame(columns=['timestamp', 'username', 'password'])

                # Crear un nuevo DataFrame para auth_attempts_df
                if 'auth_attempts' in dataframe.columns:
                    auth_attempts_list = dataframe['auth_attempts'].tolist()
                    auth_attempts_df_list = []
                    for auth_attempt in auth_attempts_list:
                        auth_attempts_df = pd.DataFrame(auth_attempt)
                        auth_attempts_df.columns = ['timestamp', 'username', 'password']
                        auth_attempts_df_list.append(auth_attempts_df)
                    auth_attempts_df = pd.concat(auth_attempts_df_list)
                    dataframe.drop('auth_attempts', axis=1, inplace=True)
                return render_template('show_results_heralding.html', dataframe=dataframe, auth_attempts_df=auth_attempts_df)
            except json.JSONDecodeError as error:
                        print(f"Error al leer archivo JSON: {error}")
                        return "Error al leer archivo JSON", 500
        else:
            print("Archivo JSON no encontrado")
            return "Archivo JSON no encontrado", 404
    else:
        print("Error al ejecutar comando docker")
        return "Error al ejecutar comando docker", 500


@app.route('/show_results_mailoney')
def show_results_mailoney():
    return render_template('graficos_cowrie.html')

@app.route('/graficos_cowrie')
def graficos_cowrie():
    return render_template('graficos_cowrie.html')

@app.route('/graficos_heralding')
def graficos_heralding():
    return render_template('graficos_heralding.html')

@app.route('/graficos_mailoney')
def graficos_mailoney():
    return render_template('graficos_mailoney.html')
