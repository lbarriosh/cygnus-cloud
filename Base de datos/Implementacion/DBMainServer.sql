/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor principal. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBMainServer;

#Abrimos la base de datos
USE DBMainServer;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY, ip VARCHAR(20),portAdress VARCHAR(20),maxVM INTEGER);

CREATE TABLE IF NOT EXISTS Image(imageId INTEGER PRIMARY KEY, name VARCHAR(20),descripcion VARCHAR(200));

CREATE TABLE IF NOT EXISTS ServerImages(serverId INTEGER,imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(imageId) REFERENCES Image(imageId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla servidores de MV
INSERT INTO VMServer VALUES (0,"Ip1","Port1",5);
INSERT INTO VMServer VALUES (1,"Ip2","Port2",5);
INSERT INTO VMServer VALUES (2,"Ip3","Port3",5);

# Tabla Imagenes
INSERT INTO Image VALUES (0,"VMName1","A Virtual machine Image");
INSERT INTO Image VALUES (1,"VMName2","A Virtual machine Image");
INSERT INTO Image VALUES (2,"VMName3","A Virtual machine Image");
INSERT INTO Image VALUES (3,"VMName4","A Virtual machine Image");

# Tabla Imagenes en servidor
INSERT INTO ServerImages VALUES (0,0);
INSERT INTO ServerImages VALUES (0,2);
INSERT INTO ServerImages VALUES (1,2);
INSERT INTO ServerImages VALUES (2,0);
INSERT INTO ServerImages VALUES (2,1);
INSERT INTO ServerImages VALUES (2,2);
INSERT INTO ServerImages VALUES (2,3);
