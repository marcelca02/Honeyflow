import docker
import os

def crear_heralding():
	client = docker.from_env()
	# mirar si existe el contenedor
	container = client.containers.list(all=True, filters={'name': 'heralding'})
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

	images = client.images.list(name='heralding')
	if not images:
		# Construye la imagen si no existe
		print("Creando imagen...")
		directorio_actual = os.path.abspath(os.path.dirname(__file__))
		ruta_dockerfile = os.path.join(directorio_actual, 'machines', 'heralding')
		client.images.build(path=ruta_dockerfile, tag='heralding', rm=True)
	
	# Ejecuta el contenedor con el nombre especificado
	print("Run container...")
	client.containers.run('heralding', stdin_open=True, tty=True, detach=True, network='honeypot-network', name='heralding')


crear_heralding()


