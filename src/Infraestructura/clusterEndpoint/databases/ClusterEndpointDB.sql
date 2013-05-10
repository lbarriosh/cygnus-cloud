/*
 This SQL script creates the system status database.
 Author: Luis Barrios Hernandez
 Version: 1.0
 */
 
CREATE DATABASE IF NOT EXISTS ClusterEndpointDB;

USE ClusterEndpointDB;
 
CREATE TABLE IF NOT EXISTS VirtualMachineServer(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
    serverStatus VARCHAR(20) NOT NULL, serverIP VARCHAR(15) NOT NULL,
    serverPort INTEGER NOT NULL, isVanillaServer TINYINT, UNIQUE(serverIP, serverPort)) ENGINE=MEMORY;
    
DELETE FROM VirtualMachineServer;

CREATE TABLE IF NOT EXISTS VirtualMachineDistribution(
    serverName VARCHAR(30),
    imageID INTEGER,
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
	
CREATE TABLE IF NOT EXISTS Image(imageID INTEGER PRIMARY KEY, name VARCHAR(20), description VARCHAR(200), bootable BOOL,
	edited BOOL, ownerID INTEGER, isBaseImage BOOL);

INSERT IGNORE INTO Image VALUES
	(1, "Debian-Squeeze", "Imagen vanilla", 0, 0, 0, 1),
	(2, "Windows 7", "Imagen vanilla", 0, 0, 0, 1),
	(3, "Debian-AISO", "Imagen de AISO", 1, 0, 0, 0),
	(4, "Windows-LEC", "Imagen de LEC", 1, 0, 0, 0),
	(5, "Windows-Xilinx", "Imagen de Windows con Xilinx", 0, 1, 2, 0); 
	
CREATE TABLE IF NOT EXISTS NewImage(temporaryID VARCHAR(70) PRIMARY KEY, imageID INTEGER, name VARCHAR(20), description VARCHAR(200),
	ownerID INTEGER, vanillaImageFamilyID SMALLINT, FOREIGN KEY(vanillaImageFamilyID) REFERENCES VanillaImageFamily(familyID));
	
INSERT IGNORE INTO NewImage VALUEs
	("Command1", -1, "Debian-LSO", "Imagen LSO", 1, 1),
	("Command10", 2, "Ubuntu-SO", "Imagen SO", 2, 1);

CREATE TABLE IF NOT EXISTS VanillaImageFamilyOf(imageID INTEGER, familyID SMALLINT,
	PRIMARY KEY(familyID, imageID),
	FOREIGN KEY(imageID) REFERENCES Image(imageID) ON DELETE CASCADE,
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamily(familyID) ON DELETE CASCADE);
	
INSERT IGNORE INTO VanillaImageFamilyOf VALUES (1, 1), (2, 5), (3, 2), (4, 6), (5, 4);