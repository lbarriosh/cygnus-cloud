/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
CREATE DATABASE IF NOT EXISTS VMServerDB;

USE VMServerDB;

CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), imagePath VARCHAR(100),osImagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY,VMId INTEGER,VNCPortAdress INTEGER, userId INTEGER, VMPid INTEGER, imageCopyPath VARCHAR(200), 
	osImagePath  VARCHAR(200),macAdress VARCHAR(20),uuid VARCHAR(40), VNCPass VARCHAR(65),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(100) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActualVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;

INSERT IGNORE INTO VirtualMachine VALUES 
	(1, 'Debian', 'DebianSqueezeAMD64/Data.qcow2', 'DebianSqueezeAMD64/SqueezeAMD64.qcow2', 'DebianSqueezeAMD64/Squeeze_AMD64.xml');
