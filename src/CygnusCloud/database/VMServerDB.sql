/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS VMServerDB;

#Abrimos la base de datos
USE VMServerDB;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), imagePath VARCHAR(100),osImagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(domainName VARCHAR(30) PRIMARY KEY,VMId INTEGER,VNCPortAdress INTEGER, userId INTEGER, VMPid INTEGER, imageCopyPath VARCHAR(200), 
	osImagePath  VARCHAR(200),macAdress VARCHAR(20),uuid VARCHAR(40), VNCPass VARCHAR(65),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine

INSERT IGNORE INTO VirtualMachine VALUES 
	(1, 'Debian', 'DebianSqueezeAMD64/Data.qcow2', 'DebianSqueezeAMD64/SqueezeAMD64.qcow2', 'DebianSqueezeAMD64/Squeeze_AMD64.xml');

#Tabla ActualVM => no hay maquinas virtuales activas. No insertamos nada

# TODO: borrar basura

INSERT IGNORE INTO ActualVM VALUES("VMName11",1,1,1,1,"./VMNameCopy1","./OSImagePath1","2C:00:00:00:00:00","fce02cff-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
INSERT IGNORE INTO ActualVM VALUES("VMName22",1,2,1,2,"./VMNameCopy1","./OSImagePath2","2C:00:00:00:00:01","fce04938-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
INSERT IGNORE INTO ActualVM VALUES("VMName33",1,3,2,3,"./VMNameCopy2","./OSImagePath3","2C:00:00:00:00:02","fce0707c-5d6d-11e2-a3f0-001f16b99e1d","1234567890Test");
INSERT IGNORE INTO ActualVM VALUES("VMName44",1,4,3,4,"./VMNameCopy3","./OSImagePath4","2C:00:00:00:00:03","fce083a2-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
