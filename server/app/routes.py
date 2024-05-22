import subprocess
from kubernetes import client, config
import threading 
import time
import docker
import json
import os
from flask import render_template, request, redirect
from app import app
from app.intrusion_detection import start_detection
import pandas as pd
import re
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Variable global para saber si el del honeypot esta corriendo o no
docker_running_c = False
docker_running_h = False
docker_running_m = False


# Thread que hace la deteccion de intrusiones
t = {
    'detection_running': False,
    'thread': None
}
event = threading.Event() 

@app.context_processor
def inject_detection_running():
    return {'detection_running': t['detection_running']}

@app.route('/')
def home():
    return render_template('index.html', thread=t['detection_running'])

@app.route('/start_intrusion_detection', methods=['POST'])
def start_intrusion_detection():
    event.clear()
    t['thread'] = threading.Thread(target=start_detection, args=(60, event))
    t['thread'].start()
    t['detection_running'] = True
    if request.referrer:
        return redirect(request.referrer)
    else:
        return redirect('/')

@app.route('/delete_intrusion/<detection_file>', methods=['POST'])
def delete_intrusion(detection_file):
    path = os.path.join('app/data_analysis/detection', detection_file)
    if os.path.exists(path):
        os.remove(path)
        return redirect('/honeypots_analysis')
    else:
        return "Archivo no encontrado", 404

 

@app.route('/stop_intrusion_detection', methods=['POST'])
def stop_intrusion_detection():
    event.set()
    t['thread'].join()
    t['detection_running'] = False
    if request.referrer:
        return redirect(request.referrer)
    else:
        return redirect('/')

@app.route('/configurar_honeypots')
def configurar_honeypots():
    return render_template('configurar_honeypots.html')

@app.route('/about_project')
def about_project():
    return render_template('about_project.html')

# @app.route('/init_k8s')
# def init_k8s():
#     create_heralding_pod();
#     create_cowrie_pod();
#     create_mailoney_pod();
#     return "Todos los honeypots han sido lanzandos en kubernetes" 
#
# @app.route('/delete_k8s')
# def stop_k8s():
#     delete_pods(); 
#     return "Todos los pods han sido borrados"

@app.route('/show_detection/<detection_file>', methods=['GET'])
def show_detection(detection_file):
    path = os.path.join('app/data_analysis/detection', detection_file)
    if os.path.exists(path):
        with open(path, 'r') as file:
            data = json.load(file)
            file.close()
            return render_template('show_detection.html', json=data)
    else:
        return "Archivo no encontrado", 404


#@app.route('/deploy_honeypot')
#def deploy_honeypot():
#    return render_template('deploy_honeypot.html')


@app.route('/ejecutar_pod', methods=['POST'])
def ejecutar_pod():
    # indicamos que se usa la variable global
    global docker_running_c
    global docker_running_h 
    global docker_running_m

    h_name = request.form['h_name']
    if h_name != 'cowrie':
        proceso = subprocess.run(['python3', f'app/create_pod_{h_name}.py'])
    else:
        proceso = subprocess.run(['python3', f'app/run_docker_{h_name}.py'])
        clientdoc = docker.from_env()
        contenedor = clientdoc.containers.get(f'{h_name}')
        time.sleep(5)
        if contenedor.status == 'running':
            docker_running_c = True
            return render_template('resultado_honeypot.html', exito=True, isdocker=True)
        else:
            return render_template('resultado_honeypot.html', exito=False, isdocker=True)

    config.load_kube_config() # carga kube config
    v1 = client.CoreV1Api()

    # esperar a que el pod este en running
    max_retries = 10
    retry_count = 0
    pod_running = False

    while retry_count < max_retries:
        pod_list = v1.list_pod_for_all_namespaces()
        for pod in pod_list.items:
            if pod.metadata.name == h_name:
                if pod.status.phase == 'Running':
                    pod_running = True
                    break
        if pod_running:
            break
        retry_count += 1
        time.sleep(5)

    if pod_running:
        if h_name == 'cowrie':
            docker_running_c = True
        elif h_name == 'heralding':
            docker_running_h = True
        elif h_name == 'mailoney':
            docker_running_m = True
        return render_template('resultado_honeypot.html', exito=True, isdocker=False)
    else:
        docker_running_h = False # no haria falta si ya es False por defecto
        docker_running_c = False 
        docker_running_m = False 
        return render_template('resultado_honeypot.html', exito=False, isdocker=False)



#@app.route('/stop_honeypot')
#def stop_honeypot():
#    return render_template('stop_honeypot.html', docker_running=docker_running)


@app.route('/stop_pod', methods=['POST'])
def stop_pod():
    global docker_running_c
    global docker_running_h
    global docker_running_m

    h_name = request.form['h_name']

    if h_name == 'cowrie' and docker_running_c == False:
        return render_template('stop_honeypot.html', running_honeypot=False, isdocker=True) 
    elif h_name == 'heralding' and docker_running_h == False:
        return render_template('stop_honeypot.html', running_honeypot=False, isdocker=False) 
    elif h_name == 'mailoney' and docker_running_m == False:
        return render_template('stop_honeypot.html', running_honeypot=False, isdocker=False)

    if h_name == 'cowrie':
        clientdoc = docker.from_env()
        contenedor = clientdoc.containers.get(f'{h_name}')
        contenedor.stop()
    else:
        config.load_kube_config() # carga kube config
        v1 = client.CoreV1Api()
        nspace = 'default'
        v1.delete_namespaced_pod(name=h_name, namespace=nspace)

    if h_name == 'cowrie':
        docker_running_c = False
    if h_name == 'heralding':
        docker_running_h = False
    if h_name == 'mailoney':
        docker_running_m = False

    return render_template('stop_honeypot.html', running_honeypot=True, isdocker=(h_name=='cowrie'))


@app.route('/k8s_cowrie')
def k8s_cowrie():
    create_mailoney_pod()
    return "Hello"
    


@app.route('/honeypots_analysis')
def honeypots_analysis():
    # Lista de honeypots disponibles con sus nombres y rutas HTML asociadas
    honeypots = [
        {'name': 'Cowrie', 'html_route': 'show_results_cowrie'},
        {'name': 'Heralding', 'html_route': 'show_results_heralding'},
        {'name': 'Mailoney', 'html_route': 'show_results_mailoney'}
        # Agrega más honeypots según sea necesario con sus nombres y rutas HTML correspondientes
    ]

    # Diccionario de detecciones de intrusiones con sus nombres y archivos JSON asociados
    detections = []
    for file in os.listdir('app/data_analysis/detection'):
        if file.endswith('.json'):
            ip = file.split('_')[0]
            date = file.split('_')[1]
            hour = file.split('_')[2].replace('.json', '')
            name = f'Host: {ip} - Date: {date} - Hour: {hour}'
            detections.append({'file': file, 'name': name})
    date_filter = request.args.get('date_filter')
    return render_template('honeypots_analysis.html', honeypots=honeypots, detections=detections, date_filter=date_filter)

@app.route('/show_results_cowrie')
def show_results_cowrie():
    # Ejecutar comando docker para copiar archivo JSON
    # proceso = subprocess.run(['docker', 'cp', 'cowrie:/home/cowrie/cowrie/var/log/cowrie/cowrie.json', 'app/data_analysis/cowrie/cowrie.json'])

    # Ejecutar comando de kubernetes para copiar archivo JSON 
    proceso = subprocess.run(['kubectl', 'cp', 'default/cowrie:/home/cowrie/cowrie/var/log/cowrie/cowrie.json', 'app/data_analysis/cowrie/cowrie.json'])
    
    if proceso.returncode == 0:
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
    # proceso = subprocess.run(['docker', 'cp', 'heralding:/log_session.json', 'app/data_analysis/heralding/heralding.json'])

    # Ejecutar comando de kubernetes para copiar archivo JSON
    proceso = subprocess.run(['kubectl', 'cp', 'default/heralding:/log_session.json', 'app/data_analysis/heralding/heralding.json'])

    if proceso.returncode == 0:
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
                auth_attempts_df_list = []

                if 'auth_attempts' in dataframe.columns:
                    auth_attempts_list = dataframe['auth_attempts'].tolist()
                    for auth_attempt in auth_attempts_list:
                        # Verificar que auth_attempt no esté vacío y tenga las claves correctas
                        if auth_attempt and all(k in auth_attempt[0] for k in ['timestamp', 'username', 'password']):
                            temp_df = pd.DataFrame(auth_attempt)
                            temp_df.columns = ['timestamp', 'username', 'password']
                            auth_attempts_df_list.append(temp_df)
                    
                    if auth_attempts_df_list:
                        auth_attempts_df = pd.concat(auth_attempts_df_list, ignore_index=True)
                    else:
                        auth_attempts_df = pd.DataFrame(columns=['timestamp', 'username', 'password'])
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
    # proceso = subprocess.run(['docker', 'cp', 'mailoney:/var/log/mailoney/commands.log', 'app/data_analysis/mailoney/mailoney.log'])

    # Ejecutar comando de kubernetes para copiar archivo de registro
    proceso = subprocess.run(['kubectl', 'cp', 'default/mailoney:/var/log/mailoney/commands.log', 'app/data_analysis/mailoney/mailoney.log'])

    if proceso.returncode == 0:
        log_file_path = os.path.join('app', 'data_analysis', 'mailoney', 'mailoney.log')

        if os.path.exists(log_file_path):
            try:
                patterns_mail = {
                    'HELO': re.compile(r'\[(.*?)\]\[(.*?)\] HELO (.*)'),
                    'MAIL FROM': re.compile(r'\[(.*?)\]\[(.*?)\] MAIL FROM: <(.*?)>'),
                    'RCPT TO': re.compile(r'\[(.*?)\]\[(.*?)\] RCPT TO: <(.*?)>'),
                    'DATA': re.compile(r'\[(.*?)\]\[(.*?)\] DATA \+ (.*)')
                }
                pattern_http = re.compile(r'\[(.*?)\]\[(.*?)\] (GET|Host|Connection|Cache-Control|Upgrade-Insecure-Requests|User-Agent|Accept|Accept-Encoding|Accept-Language|Cookie): (.*)')

                data_mail = {}
                data_http = {}

                with open(log_file_path, 'r') as log_file:
                    for line in log_file:
                        matched = False
                        for action, pattern in patterns_mail.items():
                            match = pattern.match(line)
                            if match:
                                ip_port = match.group(2)
                                value = match.group(3)
                                if ip_port not in data_mail:
                                    data_mail[ip_port] = {
                                        'IP:Puerto': ip_port,
                                        'HELO': None,
                                        'MAIL FROM': None,
                                        'RCPT TO': None,
                                        'DATA': None
                                    }
                                data_mail[ip_port][action] = value
                                matched = True
                                break

                        if not matched:
                            match_http = pattern_http.match(line)
                            if match_http:
                                ip_port = match_http.group(2)
                                header = match_http.group(3)
                                value = match_http.group(4)

                                if ip_port not in data_http:
                                    data_http[ip_port] = {
                                        'IP:Puerto': ip_port,
                                        'Host': None,
                                        'Connection': None,
                                        'Cache-Control': None,
                                        'Upgrade-Insecure-Requests': None,
                                        'User-Agent': None,
                                        'Accept': None,
                                        'Accept-Encoding': None,
                                        'Accept-Language': None,
                                        'Cookie': None
                                    }
                                data_http[ip_port][header] = value


                df_mail = pd.DataFrame(list(data_mail.values()))
                df_http = pd.DataFrame(list(data_http.values()))

                # Renderizar la plantilla HTML y pasar los DataFrames como contexto
                return render_template('show_results_mailoney.html', dataframe_mail=df_mail, dataframe_http=df_http)

            except Exception as e:
                print(f"Error al leer el archivo de registro: {e}")
                return "Error al leer el archivo de registro", 500
        else:
            print("Archivo de registro no encontrado")
            return "Archivo de registro no encontrado", 404
    else:
        print("Error al ejecutar comando kubectl")
        return "Error al ejecutar comando kubectl", 500



@app.route('/graficos_cowrie')
def graficos_cowrie():
    # Definir el path del archivo JSON
    json_file_path = os.path.join('app', 'data_analysis', 'heralding', 'heralding.json')

    # Leer los datos desde el archivo JSON
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = [json.loads(line) for line in file]

        # Contar las ocurrencias de los protocolos
        protocol_counts = {
            'http': 0,
            'mysql': 0,
            'other': 0
        }

        for entry in data:
            protocol = entry.get('protocol', '').lower()
            if protocol == 'http':
                protocol_counts['http'] += 1
            elif protocol == 'mysql':
                protocol_counts['mysql'] += 1
            elif protocol:
                protocol_counts['other'] += 1

        # Total de entradas no vacías
        total_non_empty = protocol_counts['http'] + protocol_counts['mysql'] + protocol_counts['other']

        # Datos para el gráfico
        labels = ['HTTP', 'MySQL', 'Otros']
        sizes = [
            protocol_counts['http'] / total_non_empty * 100,
            protocol_counts['mysql'] / total_non_empty * 100,
            protocol_counts['other'] / total_non_empty * 100
        ]
        colors = ['#ff9999','#66b3ff','#99ff99']
        explode = (0.1, 0.1, 0.1)  # "explode" a bit the slices
        # Crear el gráfico de rosco
        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, colors=colors,
                                          autopct='%1.1f%%',pctdistance=0.85, shadow=True, startangle=90,
                                          wedgeprops=dict(width=0.5))
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Agregar leyenda
        plt.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5), title='Protocolos')
        for autotext in autotexts:
            autotext.set_color('black')
 # Guardar el gráfico en un objeto BytesIO
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)

        # Codificar la imagen en base64
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        return render_template('graficos_heralding.html', img_data=img_base64)

    else:
        return "Archivo JSON no encontrado", 404


@app.route('/graficos_heralding')
def graficos_heralding():
    return render_template('graficos_heralding.html')

@app.route('/graficos_mailoney')
def graficos_mailoney():
    return render_template('graficos_mailoney.html')
