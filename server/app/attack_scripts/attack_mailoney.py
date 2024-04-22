# scripts/attack_mailoney.py

import smtplib
from email.mime.text import MIMEText

def enviar_correo_malicioso(destinatario, asunto, cuerpo, servidor_smtp, puerto_smtp):
	remitente = "correo@falso.com"  # Dirección de correo electrónico falsa

	# Crear el mensaje de correo electrónico
	mensaje = MIMEText(cuerpo)
	mensaje['From'] = remitente
	mensaje['To'] = destinatario
	mensaje['Subject'] = asunto

	try:
		# Conectar al servidor SMTP y enviar el correo electrónico
		servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
		servidor.sendmail(remitente, [destinatario], mensaje.as_string())
		servidor.quit()
		print("Correo electrónico malicioso enviado con éxito.")
	except Exception as e:
		print(f"Error al enviar el correo electrónico: {e}")



def main():
	destinatario = "victima@gmail.com"
	asunto = "Su cuenta ha sido comprometida"
	cuerpo = "Estimado usuario,\n\nSu cuenta ha sido comprometida. Por favor, haga clic en el siguiente enlace para recuperar el acceso a su cuenta: http://sitio.malicioso.com/recuperar\n\nAtentamente,\nEl equipo de soporte"
	servidor_smtp = "172.18.0.2"
	puerto_smtp = 25  # Puerto SMTP utilizado por Mailoney

	enviar_correo_malicioso(destinatario, asunto, cuerpo, servidor_smtp, puerto_smtp)

if __name__ == "__main__":
    main()

