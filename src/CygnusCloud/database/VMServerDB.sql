/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
CREATE DATABASE IF NOT EXISTS VMServerDB;

USE VMServerDB;

CREATE TABLE IF NOT EXISTS VirtualMachine(ImageID INTEGER PRIMARY KEY, 
	osImagePath VARCHAR(100), dataImagePath VARCHAR(100),
	definitionFilePath VARCHAR(100), bootable BOOL);
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY, ImageID INTEGER, 
	VNCPort INTEGER, VNCPass VARCHAR(65),
	userId INTEGER, webSockifyPID INTEGER, 
	osImagePath VARCHAR(100), dataImagePath VARCHAR(100),
	macAddress VARCHAR(20), uuid VARCHAR(40));

CREATE TABLE IF NOT EXISTS ActiveDomainUIDs(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(70) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActualVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE);
	
CREATE TABLE IF NOT EXISTS CompressionQueue(position INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, data VARCHAR(401) NOT NULL);
						
CREATE TABLE IF NOT EXISTS TransferQueue(position INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, data VARCHAR(216) NOT NULL);
						
CREATE TABLE IF NOT EXISTS ConnectionDataDictionary(dict_key VARCHAR(70) PRIMARY KEY, value VARCHAR(100) NOT NULL);
	

