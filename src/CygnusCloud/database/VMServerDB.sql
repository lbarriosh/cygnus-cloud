/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
# Borramos la base de datos si ya existia previamente
DROP DATABASE IF EXISTS  VMServerDB;

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS VMServerDB;

#Abrimos la base de datos
USE VMServerDB;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), imagePath VARCHAR(100),osImagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY,VMId INTEGER,VNCPortAdress INTEGER, userId INTEGER, VMPid INTEGER, imageCopyPath VARCHAR(200), 
	osImagePath  VARCHAR(200),macAdress VARCHAR(20),uuid VARCHAR(40), VNCPass VARCHAR(64),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine

INSERT IGNORE INTO VirtualMachine VALUES 
	(1, 'Debian', 'DebianSqueezeAMD64/Data.qcow2', 'DebianSqueezeAMD64/SqueezeAMD64.qcow2', 'DebianSqueezeAMD64/Squeeze_AMD64.xml');

#Tabla ActualVM => no hay maquinas virtuales activas. No insertamos nada
