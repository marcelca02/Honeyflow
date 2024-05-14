import subprocess
import os

def verificar_pod_existente():
    # Comando para verificar si el Pod ya existe
    get_pod_command = "kubectl get pod heralding"

    # Ejecutar el comando para obtener información sobre el Pod
    try:
        subprocess.run(get_pod_command, shell=True, check=True)
        return True  # El Pod existe
    except subprocess.CalledProcessError:
        return False  # El Pod no existe

def verificar_service_existente():
    # Comando para verificar si el Service ya existe
    get_service_command = "kubectl get service heralding"

    # Ejecutar el comando para obtener información sobre el Service
    try:
        subprocess.run(get_service_command, shell=True, check=True)
        return True  # El Service existe
    except subprocess.CalledProcessError:
        return False  # El Service no existe

def crear_heralding():
    if verificar_pod_existente():
        print("El Pod de Heralding ya existe.")
        return
    
    # Obtener la ruta completa del directorio donde se encuentra el script
    directorio_actual = os.path.abspath(os.path.dirname(__file__))
    # Construir la ruta completa del archivo YAML del Pod
    ruta_pod_yaml = os.path.join(directorio_actual, 'machines', 'heralding', 'pod_heralding.yaml')

    # Verificar si el archivo YAML del Pod existe
    if not os.path.exists(ruta_pod_yaml):
        print("Error: El archivo YAML del Pod no existe.")
        return

    # Comando para aplicar el archivo YAML del Pod
    apply_pod_command = f"kubectl apply -f {ruta_pod_yaml}"
    
    # Ejecutar el comando para crear el Pod
    try:
        print("Creando el Pod de Heralding...")
        subprocess.run(apply_pod_command, shell=True, check=True)
        print("Heralding ha sido creado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear Heralding: {e}")

    # Verificar si el Service ya existe
    if not verificar_service_existente():
        # Si el Service no existe, aplicar el archivo YAML del Service
        ruta_service_yaml = os.path.join(directorio_actual, 'machines', 'heralding', 'service_heralding.yaml')
        if os.path.exists(ruta_service_yaml):
            apply_service_command = f"kubectl apply -f {ruta_service_yaml}"
            try:
                print("Creando el Service para exponer el Pod de Heralding...")
                subprocess.run(apply_service_command, shell=True, check=True)
                print("Service de Heralding ha sido creado exitosamente.")
            except subprocess.CalledProcessError as e:
                print(f"Error al crear el Service de Heralding: {e}")
        else:
            print("Error: El archivo YAML del Service no existe.")

# Llamar a la función para crear Heralding
crear_heralding()
