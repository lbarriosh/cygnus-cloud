/*
 This SQL script creates the system status database.
 Author: Luis Barrios Hernandez
 Version: 1.0
 */
 
CREATE DATABASE IF NOT EXISTS ClusterEndpointDB;

USE ClusterEndpointDB;
 
CREATE TABLE IF NOT EXISTS VirtualMachineServer(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
    serverStatus VARCHAR(30) NOT NULL, serverIP VARCHAR(15) NOT NULL,
    serverPort INTEGER NOT NULL, isVanillaServer TINYINT, UNIQUE(serverIP, serverPort)) ENGINE=MEMORY;
    
DELETE FROM VirtualMachineServer;

CREATE TABLE IF NOT EXISTS VirtualMachineServerStatus(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
	hosts INTEGER, ramInUse INTEGER, ramSize INTEGER, freeStorageSpace INTEGER, availableStorageSpace INTEGER,
	freeTemporarySpace INTEGER, availableTemporarySpace INTEGER, activeVCPUs TINYINT,
	physicalCPUs TINYINT, 
	FOREIGN KEY(serverName) REFERENCES VirtualMachineServer(serverName) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
	
DELETE FROM VirtualMachineServerStatus;

CREATE TABLE IF NOT EXISTS ImageRepositoryStatus(repositoryID TINYINT PRIMARY KEY, freeDiskSpace INTEGER,
	availableDiskSpace INTEGER, repositoryStatus VARCHAR(30)) ENGINE=MEMORY;
	
DELETE FROM ImageRepositoryStatus;

CREATE TABLE IF NOT EXISTS VirtualMachineDistribution(
    serverName VARCHAR(30),
    imageID INTEGER,
    imageStatus VARCHAR(25),
    PRIMARY KEY (serverName, imageID)) ENGINE=MEMORY;

DELETE FROM VirtualMachineDistribution;
        
CREATE TABLE IF NOT EXISTS ActiveVirtualMachines(
	serverName VARCHAR(30), domainUID VARCHAR(70) PRIMARY KEY, ownerID BIGINT, imageID INTEGER, virtualMachineName VARCHAR(30),
	port INTEGER, password VARCHAR(65),
	UNIQUE (serverName, ownerID, imageID)) ENGINE=MEMORY;
	
DELETE FROM ActiveVirtualMachines;

CREATE TABLE IF NOT EXISTS VanillaImageFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(20),
    ramSize INTEGER, vCPUs TINYINT, osDiskSize INTEGER, dataDiskSize INTEGER,
    UNIQUE(familyName));
    
INSERT IGNORE INTO VanillaImageFamily VALUES (1, 'Linux-Small', 1048576, 1, 5242880, 3145728); 
INSERT IGNORE INTO VanillaImageFamily VALUES (2, 'Linux-Medium', 2097152, 2, 10485760, 6291456);
INSERT IGNORE INTO VanillaImageFamily VALUES (3, 'Linux-Big', 3145728, 4, 15728640, 12582912);
INSERT IGNORE INTO VanillaImageFamily VALUES (4, 'Windows7-Small',  1048576, 1, 20971520, 4194304);
INSERT IGNORE INTO VanillaImageFamily VALUES (5, 'Windows7-Medium', 2097152, 2, 31457280, 8388608);
INSERT IGNORE INTO VanillaImageFamily VALUES (6, 'Windows7-Big', 3145728, 4, 41943040, 16777216);

CREATE TABLE IF NOT EXISTS OSFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(30));

INSERT IGNORE INTO OSFamily VALUES
	(1, 'Linux'),
	(2, 'Windows');
	
CREATE TABLE IF NOT EXISTS OSVariant(familyID SMALLINT, variantID SMALLINT, variantName VARCHAR(30),
	PRIMARY KEY(familyID, variantID),
	FOREIGN KEY(familyID) REFERENCES OSFamily(familyID));

INSERT IGNORE INTO OSVariant VALUES
	(1, 1, 'Debian Squeeze AMD64'),
	(2, 1, 'Windows 7 Professional x86');
	
CREATE TABLE IF NOT EXISTS Image(imageID INTEGER PRIMARY KEY, vanillaImageFamilyID SMALLINT, name VARCHAR(20), description VARCHAR(200), 
	osFamily SMALLINT, osVariant SMALLINT, isBaseImage BOOL, isBootable BOOL,
	FOREIGN KEY(vanillaImageFamilyID) REFERENCES VanillaImageFamily(familyID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(osFamily, osVariant) REFERENCES OSVariant(familyID, variantID) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT IGNORE INTO Image VALUES
  (1, 1, 'Debian-Squeeze', 'Imagen vanilla', 1, 1, 1, 0),
  (2, 2, 'Debian-Squeeze', 'Imagen vanilla', 1, 1, 1, 0),
  (3, 3, 'Debian-Squeeze', 'Imagen vanilla', 1, 1, 1, 0),
  (4, 4, 'Windows 7', 'Imagen vanilla', 2, 1, 1, 0),
  (5, 5, 'Windows 7', 'Imagen vanilla', 2, 1, 1, 0),
  (6, 6, 'Windows 7', 'Imagen vanilla', 2, 1, 1, 0),
  (7, 1, 'Debian-AISO', 'Imagen de AISO', 1, 1, 0, 0),
  (8, 4, 'Windows-LEC', 'Imagen de LEC', 2, 1, 0, 0),
  (9, 5, 'Windows-Xilinx', 'Imagen de Windows con Xilinx', 2, 1, 0, 1);
	
CREATE TABLE IF NOT EXISTS EditedImage(temporaryID VARCHAR(70) PRIMARY KEY, vanillaImageFamilyID SMALLINT, 
	imageID INTEGER, name VARCHAR(20), description VARCHAR(200),
	osFamily SMALLINT, osVariant SMALLINT, ownerID INTEGER, state TINYINT,
	FOREIGN KEY(vanillaImageFamilyID) REFERENCES VanillaImageFamily(familyID),
	FOREIGN KEY(osFamily, osVariant) REFERENCES OSVariant(familyID, variantID) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT IGNORE INTO EditedImage VALUES	
	('command1',1,10, 'Debian-LRED', 'Imagen de LRED', 1, 1, 12, 0),
	('command2',1,11, 'Windows-LP2', 'Imagen de LP2', 2, 1, 12, 1),
	('command3',1,12, 'Windows-LTC', 'Imagen de LTC', 2, 1, 12, 2),
	('command4',1,13, 'Windows-POO', 'Imagen de POO', 2, 1, 12, 3),
	('command5',1,14, 'Windows-EDI', 'Imagen de EDI', 2, 1, 12, 4),
	('command6',1,15, 'Debian-LSO', 'Imagen de LSO', 1, 1, 12, 6),
	('command7',1,16, 'Windows-ISBC', 'Imagen de ISBC', 2, 1, 12, 6),
	('command8',1,17, 'Debian-SO', 'Imagen de SO', 1, 1, 12, 1);
