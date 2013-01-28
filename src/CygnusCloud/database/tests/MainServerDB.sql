/*
	This SQL script creates the main server's database.
	Author: Adrian Fernandez Hernandez
	Author: Luis Barrios Hernandez
	Version: 2.0
*/

# Drop the database (if exists)

DROP DATABASE IF EXISTS MainServerDB;

# Create the database (if necessary)
CREATE DATABASE IF NOT EXISTS MainServerDB;

# Choose the database to user
USE MainServerDB;

# Create the VMServer table.
CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER, 
	UNIQUE(serverName), UNIQUE(serverIP, serverPort));

# Create the Image table
CREATE TABLE IF NOT EXISTS Image(imageId INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20) NOT NULL,
	description VARCHAR(200), UNIQUE(name));

# Create the ImageOnServer table
CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(imageId) REFERENCES Image(imageId) ON DELETE CASCADE ON UPDATE CASCADE);
	
# This table will never exist: it's a memory table
CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER, hosts INTEGER,
	PRIMARY KEY(serverId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
# Insert some stuff in the tables

INSERT INTO VMServer(serverId, serverName, serverStatus, serverIP, serverPort) VALUES 
	(1, 'Server1', 0, '1.2.3.4', 8080),	
	(2, 'Server2', 1, '1.2.3.5', 8080),
	(3, 'Server3', 1, '1.2.3.6', 8080),
	(4, 'Server4', 1, '1.2.3.7', 8080);
	
INSERT INTO Image(imageId, name, description) VALUES
	(1, 'Ubuntu', 'Ubuntu GNU/Linux x64'),
	(2, 'Windows 7', 'Windows 7 Professional x64'),
	(3, 'Slackware', 'Slackware GNU/Linux i686');
	
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