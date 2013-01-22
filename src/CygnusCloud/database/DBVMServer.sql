/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/
# Borramos la base de datos si ya existia previamente
DROP DATABASE IF EXISTS  DBVMServer;

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBVMServer;

#Abrimos la base de datos
USE DBVMServer;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY, name VARCHAR(20), imagePath VARCHAR(100),osImagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(VMId INTEGER PRIMARY KEY,VNCPortAdress INTEGER, userId INTEGER, VMPid INTEGER, imageCopyPath VARCHAR(100), 
	osImagePath  VARCHAR(100),macAdress VARCHAR(20),uuid VARCHAR(40), VNCPass VARCHAR(64),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine
INSERT IGNORE INTO VirtualMachine VALUES(1,"VMName1","./VMName1/","./VMName1/","./VMName1/");
INSERT IGNORE INTO VirtualMachine VALUES(2,"VMName2","./VMName2/","./VMName2/","./VMName2/");
INSERT IGNORE INTO VirtualMachine VALUES(3,"VMName3","./VMName3/","./VMName3/","./VMName3/");
INSERT IGNORE INTO VirtualMachine VALUES(4,"VMName4","./VMName4/","./VMName4/","./VMName4/");

#Tabla ActualVM
INSERT IGNORE INTO ActualVM VALUES(1,1,1,1,"./VMNameCopy1","./OSImagePath1","2C:00:00:00:00:00","fce02cff-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
INSERT IGNORE INTO ActualVM VALUES(2,2,1,2,"./VMNameCopy1","./OSImagePath2","2C:00:00:00:00:01","fce04938-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
INSERT IGNORE INTO ActualVM VALUES(3,3,2,3,"./VMNameCopy2","./OSImagePath3","2C:00:00:00:00:02","fce0707c-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
INSERT IGNORE INTO ActualVM VALUES(4,4,3,4,"./VMNameCopy3","./OSImagePath4","2C:00:00:00:00:03","fce083a2-5d6d-11e2-a3f0-001f16b99e1d","1234567890");
