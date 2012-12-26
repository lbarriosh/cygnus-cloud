/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de la web. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBWebServer ;

#Abrimos la base de datos
USE DBWebServer;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS Users(userId INTEGER PRIMARY KEY, name VARCHAR(20),pass VARCHAR(20));

CREATE TABLE IF NOT EXISTS UserGroup(groupId INTEGER ,yearGroup INTEGER,Subject  VARCHAR(15),curse INTEGER,
	 curseGroup VARCHAR(1),PRIMARY KEY(groupId,yearGroup));

CREATE TABLE IF NOT EXISTS ClassGroup(userId INTEGER, groupId INTEGER, 
	  PRIMARY KEY(UserId,GroupId),
	  FOREIGN KEY(userId) REFERENCES Users(userId) ON DELETE CASCADE ON UPDATE CASCADE,
	  FOREIGN KEY(groupId) REFERENCES UserGroup(groupId) ON DELETE CASCADE ON UPDATE CASCADE);



CREATE TABLE IF NOT EXISTS VMByGroup(groupId INTEGER,VMName VARCHAR(20),
	 PRIMARY KEY(groupId,VMName),
	 FOREIGN KEY(groupId) REFERENCES UserGroup(groupId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS TypeOf (userId INTEGER,typeId INTEGER,
	 PRIMARY KEY(userId,typeId),
	 FOREIGN KEY(userId) REFERENCES Users(userId) ON DELETE CASCADE ON UPDATE CASCADE,
	 FOREIGN KEY(typeId) REFERENCES UserType(typeId) ON DELETE CASCADE ON UPDATE CASCADE);
	 
CREATE TABLE IF NOT EXISTS UserType(typeId INTEGER PRIMARY KEY,name VARCHAR(20));

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla de usuarios
INSERT INTO Users VALUES (0,"Admin1","0000");
INSERT INTO Users VALUES (1,"Admin2","1234");
INSERT INTO Users VALUES (2,"Student1","1111");
INSERT INTO Users VALUES (3,"Student2","2222");
INSERT INTO Users VALUES (4,"Student3","1122");
INSERT INTO Users VALUES (5,"Teacher1","4321");
INSERT INTO Users VALUES (6,"Teacher2","3333");
INSERT INTO Users VALUES (7,"Teacher3","4567");

# Tabla de tipos
INSERT INTO UserType VALUES (0,"Administrator");
INSERT INTO UserType VALUES (1,"Teacher");
INSERT INTO UserType VALUES (2,"Student");

# Tabla de tipos de
INSERT INTO TypeOf VALUES (0,0);
INSERT INTO TypeOf VALUES (1,0);
INSERT INTO TypeOf VALUES (2,2);
INSERT INTO TypeOf VALUES (3,2);
INSERT INTO TypeOf VALUES (4,2);
INSERT INTO TypeOf VALUES (5,1);
INSERT INTO TypeOf VALUES (6,1);
INSERT INTO TypeOf VALUES (7,1);

# Tabla de grupos
INSERT INTO UserGroup VALUES (0,2012,"Subject1","Curse1","a");
INSERT INTO UserGroup VALUES (1,2012,"Subject2","Curse1","b");
INSERT INTO UserGroup VALUES (2,2012,"Subject3","Curse2","a");
INSERT INTO UserGroup VALUES (3,2012,"Subject4","Curse2","a");

# Tabla de grupos de clase
INSERT INTO ClassGroup VALUES (2,0);
INSERT INTO ClassGroup VALUES (2,1);
INSERT INTO ClassGroup VALUES (3,0);
INSERT INTO ClassGroup VALUES (4,2);
INSERT INTO ClassGroup VALUES (4,1);
INSERT INTO ClassGroup VALUES (4,3);
INSERT INTO ClassGroup VALUES (5,0);
INSERT INTO ClassGroup VALUES (6,1);
INSERT INTO ClassGroup VALUES (6,3);
INSERT INTO ClassGroup VALUES (7,2);
INSERT INTO ClassGroup VALUES (7,3);

# Tabla de MV por Grupo
INSERT INTO VMByGroup VALUES (0,"VMName1");
INSERT INTO VMByGroup VALUES (1,"VMName2");
INSERT INTO VMByGroup VALUES (3,"VMName3");




