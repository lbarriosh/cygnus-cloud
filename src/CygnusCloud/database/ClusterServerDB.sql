/*
 *	This SQL script creates the main server's database.
 *	Author: Adrian Fernandez Hernandez
 *	Author: Luis Barrios Hernandez
 *	Version: 2.0
*/


CREATE DATABASE IF NOT EXISTS ClusterServerDB;

USE ClusterServerDB;

CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER, 
	UNIQUE(serverName), UNIQUE(serverIP, serverPort));

CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE);


CREATE TABLE IF NOT EXISTS VanillaImageFamilies(familyID SMALLINT PRIMARY KEY, 
    RAMSize INTEGER, vCPUs BYTE, OSDiskSize INTEGER, dataDiskSize INTEGER);
    
CREATE TABLE IF NOT EXISTS VMfromVanilla(familyID SMALLINT, VMID INTEGER,
	PRIMARY KEY(familyID, VMID),
	FOREIGN KEY(familyID) REFERENCES VanillaImageFamilies(familyID));
	
CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER, hosts INTEGER,
	PRIMARY KEY(serverId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70), dispatchTime double, VMID INT,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;
    
DROP TABLE IF EXISTS ActiveVMDistribution;
    
CREATE TABLE ActiveVMDistribution(vmID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	FOREIGN KEY(serverID) REFERENCES VMServer(serverID) ON DELETE CASCADE ON UPDATE CASCADE);

INSERT IGNORE INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES
    (1, 'Server1', 2, '192.168.1.2', 15800);

INSERT IGNORE INTO ImageOnServer VALUES
	(1, 1);
	
/*
 * Datos de las imagenes vanillas
 */
INSERT IGNORE INTO VanillaImageFamilies(1, 1, 1, 20, 4)
INSERT IGNORE INTO VanillaImageFamilies(2, 2, 2, 30, 8)
INSERT IGNORE INTO VanillaImageFamilies(3, 3, 4, 40, 16)
INSERT IGNORE INTO VanillaImageFamilies(4, 1, 1, 5, 3)
INSERT IGNORE INTO VanillaImageFamilies(5, 2, 2, 10, 6)
INSERT IGNORE INTO VanillaImageFamilies(6, 3, 4, 15, 12)
