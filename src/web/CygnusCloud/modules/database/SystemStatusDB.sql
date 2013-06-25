/*
 This SQL script creates the system status database.
 Author: Luis Barrios Hernandez
 Version: 1.0
 */
 
DROP DATABASE IF EXISTS SystemStatusDB;

CREATE DATABASE SystemStatusDB;

USE SystemStatusDB;
 
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