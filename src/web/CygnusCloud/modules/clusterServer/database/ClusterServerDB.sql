/*
 *	Script de creación de la base de datos del servidor de cluster
 *	Autores: Adrian Fernandez, Luis Barrios, Samuel Guayerbas
 *	Version: 4.0
*/


CREATE DATABASE IF NOT EXISTS ClusterServerDB;

USE ClusterServerDB;

CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER,
	isVanillaServer BIT, UNIQUE(serverName), UNIQUE(serverIP, serverPort));

CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER, status TINYINT,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER PRIMARY KEY, hosts INTEGER,
	ramInUse INTEGER, ramSize INTEGER, freeStorageSpace INTEGER, availableStorageSpace INTEGER,
	freeTemporarySpace INTEGER, availableTemporarySpace INTEGER, activeVCPUs TINYINT,
	physicalCPUs TINYINT, 
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DELETE FROM VMServerStatus;
	
CREATE TABLE IF NOT EXISTS AllocatedVMServerResources(commandID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	ramInUse INTEGER, freeStorageSpace INTEGER, freeTemporarySpace INTEGER, activeVCPUs TINYINT, activeHosts TINYINT, remove BOOL, 
	FOREIGN KEY(serverID) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DELETE FROM AllocatedVMServerResources;
	
CREATE TABLE IF NOT EXISTS VanillaImageFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(20),
    ramSize INTEGER, vCPUs TINYINT, osDiskSize INTEGER, dataDiskSize INTEGER,
    UNIQUE(familyName));
    
CREATE TABLE IF NOT EXISTS VanillaImageFamilyOf(imageID INTEGER, familyID SMALLINT,
	PRIMARY KEY(familyID, imageID),
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamily(familyID));
	
CREATE TABLE IF NOT EXISTS VanillaImageFamilyOfNewVM(temporaryID VARCHAR(70) PRIMARY KEY, familyID SMALLINT,
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamily(familyID));
	
DROP TABLE IF EXISTS ImageRepository;
CREATE TABLE ImageRepository(repositoryIP VARCHAR(15), repositoryPort INTEGER,
	freeDiskSpace INTEGER, availableDiskSpace INTEGER, connection_status TINYINT, PRIMARY KEY(repositoryIP, repositoryPort))
	ENGINE=MEMORY;
		
CREATE TABLE IF NOT EXISTS AllocatedImageRepositoryResources(
	commandID VARCHAR(70) PRIMARY KEY, 
	repositoryIP VARCHAR(15), 
	repositoryPort INTEGER, 
	allocatedDiskSpace INTEGER, 
	remove BOOL, 
	FOREIGN KEY(repositoryIP, repositoryPort) REFERENCES ImageRepository(repositoryIP, repositoryPort) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
		
DELETE FROM AllocatedImageRepositoryResources;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70), dispatchTime double, VMID INT,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;
    
DROP TABLE IF EXISTS ActiveVMDistribution;
    
CREATE TABLE ActiveVMDistribution(vmID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	FOREIGN KEY(serverID) REFERENCES VMServer(serverID) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
	
CREATE TABLE IF NOT EXISTS ImageEditionCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, UNIQUE(imageID));

CREATE TABLE IF NOT EXISTS ImageDeletionCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, UNIQUE(imageID));

CREATE TABLE IF NOT EXISTS AutoDeploymentCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, remainingMessages SMALLINT, error BOOL)
	ENGINE=MEMORY;
	
/*
 * Características de las familias de imágenes vanilla
 */
INSERT IGNORE INTO VanillaImageFamily VALUES (1, 'Linux-Small', 1048576, 1, 5242880, 3145728); 
INSERT IGNORE INTO VanillaImageFamily VALUES (2, 'Linux-Medium', 2097152, 2, 10485760, 6291456);
INSERT IGNORE INTO VanillaImageFamily VALUES (3, 'Linux-Big', 3145728, 4, 15728640, 12582912);

INSERT IGNORE INTO VanillaImageFamily VALUES (4, 'Windows7-Small',  1048576, 1, 20971520, 4194304);
INSERT IGNORE INTO VanillaImageFamily VALUES (5, 'Windows7-Medium', 2097152, 2, 31457280, 8388608);
INSERT IGNORE INTO VanillaImageFamily VALUES (6, 'Windows7-Big', 3145728, 4, 41943040, 16777216);

/*
 * Imágenes activas
 */
	
INSERT IGNORE INTO VanillaImageFamilyOf VALUES (1, 1);