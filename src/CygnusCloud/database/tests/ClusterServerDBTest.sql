/*
	Creación de la base de datos del servidor de cluster (modificada para las pruebas unitarias)
	Autores: Adrián Fernández, Luis Barrios
	Versión: 4.0
*/

DROP DATABASE IF EXISTS ClusterServerDBTest;

CREATE DATABASE ClusterServerDBTest;

USE ClusterServerDBTest;

CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER,
	isVanillaServer BOOL, UNIQUE(serverName), UNIQUE(serverIP, serverPort));

CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER, status TINYINT,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER PRIMARY KEY, hosts INTEGER,
	ramInUse INTEGER, ramSize INTEGER, freeStorageSpace INTEGER, availableStorageSpace INTEGER,
	freeTemporarySpace INTEGER, availableTemporarySpace INTEGER, activeVCPUs TINYINT,
	physicalCPUs TINYINT, 
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
CREATE TABLE IF NOT EXISTS VanillaImageFamily(familyID SMALLINT PRIMARY KEY AUTO_INCREMENT, familyName VARCHAR(20),
    ramSize INTEGER, vCPUs TINYINT, osDiskSize INTEGER, dataDiskSize INTEGER,
    UNIQUE(familyName));
    
CREATE TABLE IF NOT EXISTS VanillaImageFamilyOf(imageID INTEGER, familyID SMALLINT,
	PRIMARY KEY(familyID, imageID),
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamily(familyID));
	
CREATE TABLE VanillaImageFamilyOfNewVM(temporaryID VARCHAR(70) PRIMARY KEY, familyID SMALLINT,
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamily(familyID));
	
DROP TABLE IF EXISTS ImageRepository;

CREATE TABLE ImageRepository(repositoryIP VARCHAR(15), repositoryPort INTEGER,
	freeDiskSpace INTEGER, availableDiskSpace INTEGER, PRIMARY KEY(repositoryIP, repositoryPort))
	ENGINE=MEMORY;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70), dispatchTime double, VMID INT,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;
    
DROP TABLE IF EXISTS ActiveVMDistribution;
    
CREATE TABLE ActiveVMDistribution(vmID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	FOREIGN KEY(serverID) REFERENCES VMServer(serverID) ON DELETE CASCADE ON UPDATE CASCADE);
	
CREATE TABLE ImageEditionCommands(commandID VARCHAR(70) PRIMARY KEY);

/*
 * Características de las familias de imágenes vanilla
 */
INSERT IGNORE INTO VanillaImageFamily VALUES (1, 'Windows7-Small',  1, 1, 20, 4);
INSERT IGNORE INTO VanillaImageFamily VALUES (2, 'Windows7-Medium', 2, 2, 30, 8);
INSERT IGNORE INTO VanillaImageFamily VALUES (3, 'Windows7-Big', 3, 4, 40, 16);
INSERT IGNORE INTO VanillaImageFamily VALUES (4, 'Linux-Small', 1, 1, 5, 3);
INSERT IGNORE INTO VanillaImageFamily VALUES (5, 'Linux-Medium', 2, 2, 10, 6);
INSERT IGNORE INTO VanillaImageFamily VALUES (6, 'Linux-Big', 3, 4, 15, 12);

/*
 * Servidores de máquinas virtuales
 */

INSERT INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort, isVanillaServer) VALUES 
	(1, 'Server1', 0, '1.2.3.4', 8080, 1),	
	(2, 'Server2', 1, '1.2.3.5', 8080, 0),
	(3, 'Server3', 1, '1.2.3.6', 8080, 0),
	(4, 'Server4', 1, '1.2.3.7', 8080, 0);
	
INSERT INTO ImageOnServer VALUES
	(1, 1, 0),
	(1, 2, 0),
	(1, 3, 1),
	(2, 1, 1),
	(2, 2, 0),
	(3, 1, 2),
	(3, 3, 2);
	
INSERT INTO VanillaImageFamilyOf VALUES
	(1, 3), (2, 1), (3, 5);
	
INSERT INTO VMServerStatus VALUES
	(1, 0, 100, 101, 102, 103, 104, 105, 106, 107), 
	(2, 10, 200, 201, 202, 203, 204, 205, 206, 207),
	(3, 5, 300, 301, 302, 303, 304, 305, 306, 307),
	(4, 0, 400, 401, 402, 403, 404, 405, 406, 407);