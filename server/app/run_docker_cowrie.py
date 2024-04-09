import subprocess
import os

def crear_docker_network():
    # Comprobar si la red de Docker existe
    proceso = subprocess.Popen(['docker', 'network', 'inspect', 'honeypot-network'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    salida, _ = proceso.communicate()

    if proceso.returncode != 0:  # La red no existe, crearla
        subprocess.run(['docker', 'network', 'create', '-d', 'bridge', 'honeypot-network'])
        print("Red de Docker creada exitosamente.")
    else:
        print("La red de Docker ya existe.")

def construir_docker_image():
    # Cambiar al directorio donde se encuentra el Dockerfile
    ruta_dockerfile = "./app/machines"
    os.chdir(ruta_dockerfile)

    # Construir la imagen si no existe
    proceso = subprocess.Popen(['docker', 'images', '-q', 'honeypot1:v1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    salida, _ = proceso.communicate()

    if not salida:  # La imagen no existe, construirla
        subprocess.run(['docker', 'build', '-t', 'honeypot1:v1', '.'])
        print("Imagen de Docker construida exitosamente.")
    else:
        print("La imagen de Docker ya existe.")

def ejecutar_o_iniciar_docker_container():
    # Comprobar si el contenedor ya existe
    proceso = subprocess.run(['docker', 'ps', '-a', '--filter', 'ancestor=honeypot1:v1','--format', '{{.ID}}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proceso.stdout:  # El contenedor ya existe, iniciar
        contenedor_id = proceso.stdout.decode().strip() # Obtener el ID del contenedor
        subprocess.run(['docker', 'start', contenedor_id])
        print("Contenedor Docker iniciado.")
    else:  # El contenedor no existe, ejecutar
        subprocess.run(['docker', 'run', '-itd', '--network=honeypot-network', 'honeypot1:v1', '--name', 'cowrie'])
        print("Contenedor Docker ejecutado.")

# Llamar a las funciones en orden
crear_docker_network()
construir_docker_image()
ejecutar_o_iniciar_docker_container()

