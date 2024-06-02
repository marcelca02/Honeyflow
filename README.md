# Honeyflow

#### Introducción
HoneyFlow es una plataforma de seguridad informática diseñada para orquestar honeypots de diferentes características y objetivos. Esta herramienta permite exponer honeypots al exterior, capturar información sobre posibles ataques y presentar dicha información mediante tablas y gráficos para facilitar su análisis.

#### Honeypots

- **Cowrie:** Honeypot de interacción media para SSH y Telnet.
- **Mailoney:** Honeypot de baja interacción para SMTP.
- **Heralding:** Honeypot de baja interacción para la recolección de credenciales.

#### Instrucciones de Utilización

1. **Clonar el Repositorio:**

   ```sh
   git clone https://github.com/marcelca02/Honeyflow.git
   ```

2. **Moverse al Directorio del Servidor:**

   ```sh
   cd Honeyflow/server
   ```

3. **Crear el Entorno Virtual:**

   ```sh
   python -m venv .venv
   ```

4. **Activar el Entorno Virtual:**

   En Linux/MacOS:

   ```sh
   . .venv/bin/activate
   ```

   En Windows:

   ```sh
   .venv\Scripts\activate
   ```

5. **Instalar las Dependencias:**

   ```sh
   pip install -r requirements.txt
   ```

6. **Ejecutar el Servidor:**

   ```sh
   flask run --port 8080 --host=0.0.0.0
   ```

#### Notas Adicionales
- Asegúrate de que `python`, `pip`, y `flask` estén correctamente instalados en tu sistema.
- Si encuentras algún problema o tienes preguntas, por favor revisa la documentación del proyecto o abre un issue en el repositorio.

#### Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor haz un fork del repositorio, crea una rama con tus cambios y envía un pull request para revisión.

¡Gracias por usar HoneyFlow!
