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

# Create the VMServer table.
CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverStatus INTEGER, ip VARCHAR(15), port INTEGER);

# Create the Image table
CREATE TABLE IF NOT EXISTS Image(imageId INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20),description VARCHAR(200));

# Create the ServerImages table
CREATE TABLE IF NOT EXISTS ServerImages(serverId INTEGER,imageId INTEGER,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(imageId) REFERENCES Image(imageId) ON DELETE CASCADE ON UPDATE CASCADE);
	
# This table will never exist: it's a memory table
CREATE TABLE VMServerStatus(serverId INTEGER, hosts INTEGER,
	PRIMARY_KEY(serverId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;