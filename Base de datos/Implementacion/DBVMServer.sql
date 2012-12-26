/*
  Este Script contiene todos los comandos sql necesarios para realizar la creación y rellenado de la base de datos y sus correspondientes
   tablas correspondientes al servidor de máquinas virtuales. La información de inicio permite crear un sistema inicial con el que poder realizar las 
   pruebas pertinentes y poder gestionar el sistema.
  Este script deberá ser cargado cada vez que sea necesario crear la base de datos
*/

-- Comenzamos creando la correspondiente base de datos
CREATE DATABASE IF NOT EXISTS DBVMServer;

--Abrimos la base de datos
USE DBVMServer;

--Creamos las tablas necesarias
CREATE TABLE IF NOT EXISTS VirtualMachine(VMId LONG PRIMARY KEY, name VARCHAR(20), imagePath VARCHAR(100),
	FileConfigPath VARCHAR(100));
	
CREATE TABLE IF NOT EXISTS ActualVM(VNCPortAdress LONG PRIMARY KEY, userId LONG, VMId LONG, imageCopyPath VARCHAR(100),
	FileConfigCopyPath VARCHAR(100),macAdress VARCHAR(12), VNCPass VARCHAR(64),
	FOREIGN KEY (VMId) REFERENCES VirtualMachine(VMId) ON DELETE CASCADE ON UPDATE CASCADE);

-- Comenzamos a rellenar las tablas con los valores por defecto
-- ____________________________________________________________

-- Tabla VirtualMachine
INSERT INTO VirtualMachine VALUES(0,"VMName1","./VMName1/","./VMName1/");
INSERT INTO VirtualMachine VALUES(1,"VMName2","./VMName2/","./VMName2/");
INSERT INTO VirtualMachine VALUES(2,"VMName3","./VMName3/","./VMName3/");
INSERT INTO VirtualMachine VALUES(3,"VMName4","./VMName4/","./VMName4/");

--Tabla ActualVM
INSERT INTO ActualVM VALUES(0,0,0,"./VMNameCopy1","./VMNameCopy1","000000","1234567890");
INSERT INTO ActualVM VALUES(0,1,0,"./VMNameCopy1","./VMNameCopy1","111111","1234567890");
INSERT INTO ActualVM VALUES(0,2,1,"./VMNameCopy2","./VMNameCopy2","222222","1234567890");
INSERT INTO ActualVM VALUES(0,3,2,"./VMNameCopy3","./VMNameCopy3","333333","1234567890");
INSERT INTO ActualVM VALUES(0,4,3,"./VMNameCopy4","./VMNameCopy4","444444","1234567890");