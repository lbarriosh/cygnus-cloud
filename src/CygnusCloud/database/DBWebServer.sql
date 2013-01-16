/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de la web. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
# Borramos la base de datos si ya existia previamente
DROP DATABASE IF EXISTS  DBWebServer;

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBWebServer ;

#Abrimos la base de datos
USE DBWebServer;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS Users(userId INTEGER  PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20),pass VARCHAR(20));

CREATE TABLE IF NOT EXISTS UserGroup(groupId INTEGER AUTO_INCREMENT,yearGroup INTEGER,subject  VARCHAR(15),curse INTEGER,
	 curseGroup VARCHAR(1),PRIMARY KEY(groupId,yearGroup));

CREATE TABLE IF NOT EXISTS ClassGroup(userId INTEGER, groupId INTEGER, 
	  PRIMARY KEY(UserId,GroupId),
	  FOREIGN KEY(userId) REFERENCES Users(userId) ON DELETE CASCADE ON UPDATE CASCADE,
	  FOREIGN KEY(groupId) REFERENCES UserGroup(groupId) ON DELETE CASCADE ON UPDATE CASCADE);



CREATE TABLE IF NOT EXISTS VMByGroup(groupId INTEGER,VMName VARCHAR(20),
	 PRIMARY KEY(groupId,VMName),
	 FOREIGN KEY(groupId) REFERENCES UserGroup(groupId) ON DELETE CASCADE ON UPDATE CASCADE);
	 
CREATE TABLE IF NOT EXISTS UserType(typeId INTEGER  PRIMARY KEY AUTO_INCREMENT,name VARCHAR(20));

CREATE TABLE IF NOT EXISTS TypeOf (userId INTEGER,typeId INTEGER,
	 PRIMARY KEY(userId,typeId),
	 FOREIGN KEY(userId) REFERENCES Users(userId) ON DELETE CASCADE ON UPDATE CASCADE,
	 FOREIGN KEY(typeId) REFERENCES UserType(typeId) ON DELETE CASCADE ON UPDATE CASCADE);
	 


# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla de usuarios
INSERT IGNORE INTO Users VALUES (8,"Admin1","0000");
INSERT IGNORE INTO Users VALUES (1,"Admin2","1234");
INSERT IGNORE INTO Users VALUES (2,"Student1","1111");
INSERT IGNORE INTO Users VALUES (3,"Student2","2222");
INSERT IGNORE INTO Users VALUES (4,"Student3","1122");
INSERT IGNORE INTO Users VALUES (5,"Teacher1","4321");
INSERT IGNORE INTO Users VALUES (6,"Teacher2","3333");
INSERT IGNORE INTO Users VALUES (7,"Teacher3","4567");


# Tabla de tipos
INSERT IGNORE INTO UserType VALUES (1,"Administrator");
INSERT IGNORE INTO UserType VALUES (2,"Teacher");
INSERT IGNORE INTO UserType VALUES (3,"Student");

# Tabla de tipos de
INSERT IGNORE INTO TypeOf VALUES (1,1);
INSERT IGNORE INTO TypeOf VALUES (2,1);
INSERT IGNORE INTO TypeOf VALUES (2,3);
INSERT IGNORE INTO TypeOf VALUES (3,3);
INSERT IGNORE INTO TypeOf VALUES (4,3);
INSERT IGNORE INTO TypeOf VALUES (5,2);
INSERT IGNORE INTO TypeOf VALUES (6,2);
INSERT IGNORE INTO TypeOf VALUES (7,2);

# Tabla de grupos
INSERT IGNORE INTO UserGroup VALUES (1,2012,"Subject1",1,"a");
INSERT IGNORE INTO UserGroup VALUES (2,2012,"Subject2",1,"b");
INSERT IGNORE INTO UserGroup VALUES (3,2012,"Subject3",2,"a");
INSERT IGNORE INTO UserGroup VALUES (4,2012,"Subject4",3,"a");

# Tabla de grupos de clase
INSERT IGNORE INTO ClassGroup VALUES (2,1);
INSERT IGNORE INTO ClassGroup VALUES (2,2);
INSERT IGNORE INTO ClassGroup VALUES (3,1);
INSERT IGNORE INTO ClassGroup VALUES (4,3);
INSERT IGNORE INTO ClassGroup VALUES (4,2);
INSERT IGNORE INTO ClassGroup VALUES (4,4);
INSERT IGNORE INTO ClassGroup VALUES (5,1);
INSERT IGNORE INTO ClassGroup VALUES (6,2);
INSERT IGNORE INTO ClassGroup VALUES (6,4);
INSERT IGNORE INTO ClassGroup VALUES (7,3);
INSERT IGNORE INTO ClassGroup VALUES (7,4);

# Tabla de MV por Grupo
INSERT IGNORE INTO VMByGroup VALUES (1,"VMName1");
INSERT IGNORE INTO VMByGroup VALUES (2,"VMName2");
INSERT IGNORE INTO VMByGroup VALUES (4,"VMName3");




