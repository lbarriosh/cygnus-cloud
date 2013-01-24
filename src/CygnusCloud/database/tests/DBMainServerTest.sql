/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor principal. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
# Borramos la base de datos si ya existia previamente
DROP DATABASE IF EXISTS  DBMainServerTest;

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBMainServerTest;

#Abrimos la base de datos
USE DBMainServerTest;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, ip VARCHAR(20),portAdress VARCHAR(20),maxVM INTEGER);

CREATE TABLE IF NOT EXISTS Image(imageId INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20),description VARCHAR(200));

CREATE TABLE IF NOT EXISTS ServerImages(serverId INTEGER,imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(imageId) REFERENCES Image(imageId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla servidores de MV
INSERT IGNORE INTO VMServer VALUES (1,"Ip1","Port1",5);
INSERT IGNORE INTO VMServer VALUES (2,"Ip2","Port2",5);
INSERT IGNORE INTO VMServer VALUES (3,"Ip3","Port3",5);

# Tabla Imagenes
INSERT IGNORE INTO Image VALUES (1,"VMName1","A Virtual machine Image 1");
INSERT IGNORE INTO Image VALUES (2,"VMName2","A Virtual machine Image 2");
INSERT IGNORE INTO Image VALUES (3,"VMName3","A Virtual machine Image 3");
INSERT IGNORE INTO Image VALUES (4,"VMName4","A Virtual machine Image 4");

# Tabla Imagenes en servidor
INSERT IGNORE INTO ServerImages VALUES (1,1);
INSERT IGNORE INTO ServerImages VALUES (1,3);
INSERT IGNORE INTO ServerImages VALUES (2,3);
INSERT IGNORE INTO ServerImages VALUES (3,1);
INSERT IGNORE INTO ServerImages VALUES (3,2);
INSERT IGNORE INTO ServerImages VALUES (3,3);
INSERT IGNORE INTO ServerImages VALUES (3,4);
