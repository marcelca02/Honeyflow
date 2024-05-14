import subprocess
import os

def verificar_pod_existente():
    # Comando para verificar si el Pod ya existe
    get_pod_command = "kubectl get pod cowrie"

    # Ejecutar el comando para obtener información sobre el Pod
    try:
        subprocess.run(get_pod_command, shell=True, check=True)
        return True  # El Pod existe
    except subprocess.CalledProcessError:
        return False  # El Pod no existe

def verificar_service_existente():
    # Comando para verificar si el Service ya existe
    get_service_command = "kubectl get service cowrie"

    # Ejecutar el comando para obtener información sobre el Service
    try:
        subprocess.run(get_service_command, shell=True, check=True)
        return True  # El Service existe
    except subprocess.CalledProcessError:
        return False  # El Service no existe

def crear_cowrie():
    if verificar_pod_existente():
        print("El Pod de Cowrie ya existe.")
        return
    
    # Obtener la ruta completa del directorio donde se encuentra el script
    directorio_actual = os.path.abspath(os.path.dirname(__file__))
    # Construir la ruta completa del archivo YAML del Pod
    ruta_pod_yaml = os.path.join(directorio_actual, 'machines', 'cowrie', 'pod_cowrie.yaml')

    # Verificar si el archivo YAML del Pod existe
    if not os.path.exists(ruta_pod_yaml):
        print("Error: El archivo YAML del Pod no existe.")
        return

    # Comando para aplicar el archivo YAML del Pod
    apply_pod_command = f"kubectl apply -f {ruta_pod_yaml}"
    
    # Ejecutar el comando para crear el Pod
    try:
        print("Creando el Pod de Cowrie...")
        subprocess.run(apply_pod_command, shell=True, check=True)
        print("Cowrie ha sido creado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear Cowrie: {e}")

    # Verificar si el Service ya existe
    if not verificar_service_existente():
        # Si el Service no existe, aplicar el archivo YAML del Service
        ruta_service_yaml = os.path.join(directorio_actual, 'machines', 'cowrie', 'service_cowrie.yaml')
        if os.path.exists(ruta_service_yaml):
            apply_service_command = f"kubectl apply -f {ruta_service_yaml}"
            try:
                print("Creando el Service para exponer el Pod de Cowrie...")
                subprocess.run(apply_service_command, shell=True, check=True)
                print("Service de Cowrie ha sido creado exitosamente.")
            except subprocess.CalledProcessError as e:
                print(f"Error al crear el Service de Cowrie: {e}")
        else:
            print("Error: El archivo YAML del Service no existe.")

# Llamar a la función para crear Cowrie
crear_cowrie()