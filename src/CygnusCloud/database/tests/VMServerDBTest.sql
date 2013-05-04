/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

DROP DATABASE IF EXISTS VMServerDBTest;

CREATE DATABASE VMServerDBTest;

USE VMServerDBTest;

CREATE TABLE IF NOT EXISTS VirtualMachine(ImageID INTEGER PRIMARY KEY,
	osImagePath VARCHAR(100), dataImagePath VARCHAR(100),
	definitionFilePath VARCHAR(100), bootable BOOL);
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY, ImageID INTEGER, 
	VNCPort INTEGER, VNCPass VARCHAR(65),
	userId INTEGER, webSockifyPID INTEGER, 
	osImagePath  VARCHAR(100), dataImagePath VARCHAR(100),
	macAddress VARCHAR(20), uuid VARCHAR(40));

CREATE TABLE ActiveDomainUIDs(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(70) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActualVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE);
	
CREATE TABLE IF NOT EXISTS CompressionQueue(position INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, data VARCHAR(100) NOT NULL);
						
CREATE TABLE IF NOT EXISTS TransferQueue(position INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, data VARCHAR(216) NOT NULL);
						
CREATE TABLE IF NOT EXISTS ConnectionDataDictionary(dict_key VARCHAR(70) PRIMARY KEY, value VARCHAR(100) NOT NULL);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine
INSERT IGNORE INTO VirtualMachine VALUES(1,"./VMName1/OS.qcow2","./VMName1/Data.qcow2","./VMName1/Definition.xml", 0);
INSERT IGNORE INTO VirtualMachine VALUES(2,"./VMName2/OS.qcow2","./VMName2/Data.qcow2","./VMName2/Definition.xml", 1);
INSERT IGNORE INTO VirtualMachine VALUES(3,"./VMName3/OS.qcow2","./VMName3/Data.qcow2","./VMName3/Definition.xml", 1);
INSERT IGNORE INTO VirtualMachine VALUES(4,"./VMName4/OS.qcow2","./VMName4/Data.qcow2","./VMName4/Definition.xml", 0);

#Tabla ActualVM
INSERT IGNORE INTO ActualVM VALUES("1_1", 1,
	1, "12134567890", 
	1,1,
	"./OSImagePath1", "./DataImagePath1",
	"2C:00:00:00:00:00","fce02cff-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("2_2",1,
	2, "1234567890", 
	1,2,
	"./OSImagePath2", "./DataImagePath2",
	"2C:00:00:00:00:01","fce04938-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("3_3",1,
	3, "1234567890Test", 
	2,3,
	"./OSImagePath3", "./DataImagePath3",
	"2C:00:00:00:00:02","fce0707c-5d6d-11e2-a3f0-001f16b99e1d");
INSERT IGNORE INTO ActualVM VALUES("4_4",1,
	4, "1234567890",
	3,4,
	"./OSImagePath4", "./DataImagePath4",
	"2C:00:00:00:00:03","fce083a2-5d6d-11e2-a3f0-001f16b99e1d");
	
INSERT IGNORE INTO ActiveDomainUIDs VALUES ("1_1", "Command1"), ("2_2", "Command2"),
	("3_3", "Command3"), ("4_4", "Command4");