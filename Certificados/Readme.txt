Certificados firmados por CygnusCloud
=====================================

Para que el tráfico viaje cifrado, hay que utilizar los ficheros server.key y server.crt.

server_original.key y server_original.crt son casi idénticos a estos, pero en ellos la clave
está cifrada, siendo necesario introducir la contraseña (CygnusCloud).

server.csr es la petición del certificado. Para obtener un certificado de otro organismo,
habría que enviarles este fichero.