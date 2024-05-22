# scripts/attack_mailoney.py

import smtplib
from email.mime.text import MIMEText

def enviar_correo_malicioso(remitente, destinatario, asunto, cuerpo, servidor_smtp, puerto_smtp):
	# Crear el mensaje de correo electrónico
	mensaje = MIMEText(cuerpo)
	mensaje['From'] = remitente
	mensaje['To'] = destinatario
	mensaje['Subject'] = asunto

	try:
		# (DATA not implemented)
		servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
		servidor.sendmail(remitente, [destinatario], mensaje.as_string())
		servidor.quit()
		print("Correo electrónico malicioso enviado con éxito.")
	except Exception as e:
		print(f"Error al enviar el correo electrónico: {e}")



import telnetlib3, traceback

async def enviar_correo_telnet(asunto, remitente, destinatario, cuerpo, servidor_smtp):
    try:
	# establecer conexion con telnet
        reader, writer = await telnetlib3.open_connection(servidor_smtp, 25)

	# read until -> esperar para asegurar que el servidor haya enviado respuesta ok
        await reader.readuntil(b"220")
        writer.write("HELO example.com\r\n")
        await writer.drain()
        await reader.readuntil(b"250")

	# remitente
        writer.write(f"MAIL FROM: <{remitente}>\r\n")
        await writer.drain()
        await reader.readuntil(b"250")

	# destinatario
        writer.write(f"RCPT TO: <{destinatario}>\r\n")
        await writer.drain()
        await reader.readuntil(b"250")

	# cuerpo
        writer.write(f"DATA + {cuerpo}\r\n")
        await writer.drain()
        #await reader.readuntil(b"354")

	# close connection
        writer.close()

        print("[+] Correo electrónico malicioso enviado con éxito.")
    except Exception as e:
        traceback.print_exc()
        print(f"Error al enviar el correo electrónico: {e}")



async def main():
	destinatario = "victima@gmail.com"
	asunto = "Su cuenta ha sido comprometida"
	cuerpo = "Estimado usuario, Su cuenta ha sido comprometida. Por favor, 
			haga clic en el siguiente enlace para recuperar el acceso a su cuenta: 
			http://sitio.malicioso.com/recuperar. Atentamente, El equipo de soporte"
	#servidor_smtp = "172.18.0.2"
	puerto_smtp = 25

	remitente = "correofalso@gmail.com"
	#enviar_correo_malicioso(remitente, destinatario, asunto, cuerpo, "172.18.0.3", puerto_smtp)

	await enviar_correo_telnet(asunto, remitente, destinatario, cuerpo, "172.18.0.2")

import asyncio

if __name__ == "__main__":
    asyncio.run(main())
