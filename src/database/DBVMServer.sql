/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

# Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBVMServer;

#Abrimos la base de datos
USE DBVMServer;

#Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20), imagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(VNCPortAdress INTEGER PRIMARY KEY, userId INTEGER, VMId INTEGER, imageCopyPath VARCHAR(100),
	FileConfigCopyPath VARCHAR(100),macAdress VARCHAR(12), VNCPass VARCHAR(64),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

# Comenzamos a rellenar las tablas con los valores por defecto
# ____________________________________________________________

# Tabla VirtualMachine
INSERT IGNORE INTO VirtualMachine VALUES(0,"VMName1","./VMName1/","./VMName1/");
INSERT IGNORE INTO VirtualMachine VALUES(1,"VMName2","./VMName2/","./VMName2/");
INSERT IGNORE INTO VirtualMachine VALUES(2,"VMName3","./VMName3/","./VMName3/");
INSERT IGNORE INTO VirtualMachine VALUES(3,"VMName4","./VMName4/","./VMName4/");

#Tabla ActualVM
INSERT IGNORE INTO ActualVM VALUES(0,0,0,"./VMNameCopy1","./VMNameCopy1","000000","1234567890");
INSERT IGNORE INTO ActualVM VALUES(1,1,0,"./VMNameCopy1","./VMNameCopy1","111111","1234567890");
INSERT IGNORE INTO ActualVM VALUES(2,2,1,"./VMNameCopy2","./VMNameCopy2","222222","1234567890");
INSERT IGNORE INTO ActualVM VALUES(3,3,2,"./VMNameCopy3","./VMNameCopy3","333333","1234567890");
INSERT IGNORE INTO ActualVM VALUES(4,4,3,"./VMNameCopy4","./VMNameCopy4","444444","1234567890");