/*
 *	This SQL script creates the main server's database.
 *	Author: Adrian Fernandez Hernandez
 *	Author: Luis Barrios Hernandez
 *	Version: 2.0
*/


CREATE DATABASE IF NOT EXISTS MainServerDB;

USE MainServerDB;

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

INSERT IGNORE INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES
    (1, 'Server1', 2, '192.168.0.4', 15800);

INSERT IGNORE INTO ImageOnServer VALUES
	(1, 1);
