/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

DROP DATABASE IF EXISTS VMServerDBTest;

CREATE DATABASE VMServerDBTest;

USE VMServerDBTest;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), 
	dataImagePath VARCHAR(100),osImagePath VARCHAR(100),
	definitionFilePath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY, VMId INTEGER, 
	VNCPort INTEGER, VNCPass VARCHAR(65),
	userId INTEGER, webSockifyPID INTEGER, 
	dataImagePath VARCHAR(100), osImagePath  VARCHAR(100),
	macAddress VARCHAR(20), uuid VARCHAR(40), 
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(70) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActualVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;


# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine
INSERT IGNORE INTO VirtualMachine VALUES(1,"VMName1","./VMName1/","./VMName1/","./VMName1/");
INSERT IGNORE INTO VirtualMachine VALUES(2,"VMName2","./VMName2/","./VMName2/","./VMName2/");
INSERT IGNORE INTO VirtualMachine VALUES(3,"VMName3","./VMName3/","./VMName3/","./VMName3/");
INSERT IGNORE INTO VirtualMachine VALUES(4,"VMName4","./VMName4/","./VMName4/","./VMName4/");

#Tabla ActualVM
INSERT IGNORE INTO ActualVM VALUES("VMName11", 1,
	1, "12134567890", 
	1,1,
	"./VMNameCopy1","./OSImagePath1",
	"2C:00:00:00:00:00","fce02cff-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("VMName22",1,
	2, "1234567890", 
	1,2,
	"./VMNameCopy1","./OSImagePath2",
	"2C:00:00:00:00:01","fce04938-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("VMName33",1,
	3, "1234567890Test", 
	2,3,
	"./VMNameCopy2","./OSImagePath3",
	"2C:00:00:00:00:02","fce0707c-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("VMName44",1,
	4, "1234567890",
	3,4,
	"./VMNameCopy3","./OSImagePath4",
	"2C:00:00:00:00:03","fce083a2-5d6d-11e2-a3f0-001f16b99e1d");
	
INSERT IGNORE INTO VMBootCommand VALUES ("VMName44", "123");
