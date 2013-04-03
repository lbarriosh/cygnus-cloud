/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
CREATE DATABASE IF NOT EXISTS VMServerDB;

USE VMServerDB;

CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), 
	dataImagePath VARCHAR(100),osImagePath VARCHAR(100),
	definitionFilePath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY, VMId INTEGER, 
	VNCPort INTEGER, VNCPass VARCHAR(65),
	userId INTEGER, webSockifyPID INTEGER, 
	dataImagePath VARCHAR(100), osImagePath  VARCHAR(100),
	macAddress VARCHAR(20), uuid VARCHAR(40), 
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS ActiveDomainUIDs(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(70) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActualVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT IGNORE INTO VirtualMachine VALUES 
	(1, 'Debian', 'DebianSqueezeAMD64/Data.qcow2', 'DebianSqueezeAMD64/SqueezeAMD64.qcow2', 'DebianSqueezeAMD64/Squeeze_AMD64.xml');
