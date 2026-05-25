# Observatorio de Gestión y Análisis de Indicadores para la Ciencia y la Innovación

Sitio web oficial del Observatorio de Gestión y Análisis de Indicadores para la Ciencia y la Innovación, Facultad de Ciencias, Universidad Nacional de Colombia. La plataforma combina una interfaz web pública, una API, una base de datos PostgreSQL y componentes analíticos para visualizar y administrar indicadores relacionados con ciencia, tecnología e innovación.

## Resumen del Proyecto

El repositorio está organizado como una aplicación de múltiples servicios:

- `backend/`: servicio API en Python construido con Flask y ejecutado con Gunicorn en producción.
- `frontend/`: aplicación React construida con Vite.
- `db/`: recursos de esquema y semillas de PostgreSQL para configuraciones locales de base de datos.
- `shiny/`: aplicaciones analíticas en R/Shiny y configuración del servidor.
- `nginx/`: proxy inverso HTTPS que enruta el tráfico hacia los servicios de la aplicación.
- `shared_files/`: almacenamiento compartido usado por el backend y Shiny en producción.

## Archivos de Entorno con `gen_envs.py`

El script `gen_envs.py` administra los archivos de entorno del repositorio.

Soporta dos modos:

- `build`: recorre el repositorio buscando archivos `.env`, `.env.dev` y `.env.prod`, guarda la estructura recopilada como JSON plano y la cifra en `config.gpg`.
- `decrypt`: descifra `config.gpg` y recrea los archivos `.env` correspondientes en sus carpetas originales.

Uso típico desde la raíz del repositorio:

```bash
python gen_envs.py build --root . --output config.gpg
python gen_envs.py decrypt --root . --output config.gpg
```

Opciones útiles:

- `--force-scan` con `build` ignora un `config.json` existente y vuelve a escanear el sistema de archivos.
- `--force` con `decrypt` sobrescribe los archivos de entorno existentes sin pedir confirmación.
- `--dry-run` con `decrypt` muestra una vista previa de los archivos que se escribirían.

El script requiere que `gpg` esté instalado y disponible en `PATH`.

## Ejecutar en Desarrollo

El entorno de desarrollo usa [docker-compose.dev.yml](docker-compose.dev.yml). Monta el código fuente, ejecuta el frontend con el servidor de desarrollo de Vite, inicia el backend en modo depuración y expone Adminer para inspección de la base de datos.

```bash
docker compose -f docker-compose.dev.yml up --build
```

Servicios principales en desarrollo:

- Base de datos PostgreSQL en la red privada de Docker.
- API del backend en el puerto `5000`.
- Servidor de desarrollo del frontend en el puerto `5173`.
- Servidor Shiny para analítica interactiva.
- Proxy inverso Nginx exponiendo la aplicación en `80` y `443`.
- Adminer en el puerto `8080` para acceso a la base de datos.

## Ejecutar en Producción

Producción usa [docker-compose.prod.yml](docker-compose.prod.yml). Construye las imágenes de la aplicación, ejecuta el backend con Gunicorn, sirve el frontend en modo preview después de construirlo y enruta el tráfico externo a través de Nginx. El stack de producción no inicia un contenedor de base de datos; el backend se conecta a una instancia externa de PostgreSQL.

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Diferencias principales en producción:

- El backend se ejecuta con Gunicorn en lugar del servidor de depuración de Flask.
- El frontend se construye antes de ser servido.
- Los recursos compartidos se montan desde `shared_files/`.
- Las credenciales de base de datos deben apuntar a un servidor PostgreSQL externo, no a un contenedor dentro del stack de compose.
- No se incluye el servicio Adminer.

Antes de iniciar producción, asegúrate de que la configuración del backend en `backend/.env.prod` apunte `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` a la base de datos externa.

## Resumen de Componentes

- Backend: API y lógica de negocio.
- Frontend: interfaz web para el usuario.
- Base de datos: capa de persistencia en PostgreSQL.
- Shiny: aplicaciones de análisis y visualización.
- Nginx: punto de entrada HTTPS y enrutador de solicitudes.
- Archivos compartidos: almacenamiento común para archivos generados o cargados.
