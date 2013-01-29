/*
	This SQL script creates the main server's database.
	Author: Adrian Fernandez Hernandez
	Author: Luis Barrios Hernandez
	Version: 2.0
*/


# Create the database (if necessary)
CREATE DATABASE IF NOT EXISTS MainServerDB;

# Choose the database to user
USE MainServerDB;

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