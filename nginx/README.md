# Configuración HTTPS (Certificado SSL autofirmado)

Este proyecto utiliza HTTPS con un certificado autofirmado generado con OpenSSL para entornos de desarrollo.


# Generar certificado SSL (OpenSSL)

Desde la raíz del proyecto, primero crea la carpeta donde se guardarán los certificados:

```bash
mkdir -p ssl
````

Luego genera el certificado:

```bash id="sslgen1"
openssl req -x509 -nodes -days 365 \
-newkey rsa:2048 \
-keyout ssl/nginx.key \
-out ssl/nginx.crt
```


# Información que te pedirá OpenSSL

Al ejecutar el comando, OpenSSL solicitará los siguientes datos:

```text id="sslfields"
País (2 letras)
Estado o provincia
Ciudad
Organización
Unidad organizacional
Nombre común (Common Name)
Correo electrónico
```

# Esto genera:

* nginx.key → clave privada
* nginx.crt → certificado autofirmado


