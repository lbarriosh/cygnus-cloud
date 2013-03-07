/*
	This SQL script creates the main server's database.
	Author: Adrian Fernandez Hernandez
	Author: Luis Barrios Hernandez
	Version: 2.0
*/

DROP DATABASE IF EXISTS ClusterServerDBTest;

CREATE DATABASE ClusterServerDBTest;

USE ClusterServerDBTest;

CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER, 
	UNIQUE(serverName), UNIQUE(serverIP, serverPort));

CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE);
	
CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER, hosts INTEGER,
	PRIMARY KEY(serverId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70), dispatchTime double, VMID INT,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;

INSERT INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES 
	(1, 'Server1', 0, '1.2.3.4', 8080),	
	(2, 'Server2', 1, '1.2.3.5', 8080),
	(3, 'Server3', 1, '1.2.3.6', 8080),
	(4, 'Server4', 1, '1.2.3.7', 8080);
	
INSERT INTO ImageOnServer VALUES
	(1, 1),
	(1, 2),
	(1, 3),
	(2, 1),
	(2, 2),
	(3, 1),
	(3, 3);
	
INSERT INTO VMServerStatus VALUES
	(1, 0), (2, 10), (3, 5), (4, 0);
