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
	
CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER, hosts INTEGER,
	PRIMARY KEY(serverId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70) NOT NULL, time double,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;

INSERT IGNORE INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES
    (1, 'Server1', 2, '127.0.0.1', 15800);

INSERT IGNORE INTO ImageOnServer VALUES
	(1, 1);
