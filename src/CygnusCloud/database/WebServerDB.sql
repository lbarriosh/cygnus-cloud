/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de la web. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

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