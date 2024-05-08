import docker
import os

def crear_cowrie():
	client = docker.from_env()
	# mirar si existe el contenedor
	container = client.containers.list(all=True, filters={'name': 'cowrie'})
	# si existe:
	if container:
		# Si el contenedor ya existe, intenta iniciarlo
		container = container[0] # (si hay mas d uno)
		if container.status != 'running':
			print("Starting container...")
			container.start()
		return

	# mirar si existe la network
	networks = client.networks.list(names=['honeypot-network'])
	if not networks:
		# Si el contenedor no existe, crea la red si no existe
		print("Creando network...")
		client.networks.create('honeypot-network', driver='bridge')

	images = client.images.list(name='cowrie')
	if not images:
		# Construye la imagen si no existe
		print("Creando imagen...")
		directorio_actual = os.path.abspath(os.path.dirname(__file__))
		ruta_dockerfile = os.path.join(directorio_actual, 'machines', 'cowrie')
		client.images.build(path=ruta_dockerfile, tag='cowrie', rm=True)
	
	# Ejecuta el contenedor con el nombre especificado
	print("Run container...")
	client.containers.run('cowrie', stdin_open=True, tty=True, detach=True, network='honeypot-network', name='cowrie')


crear_cowrie()


