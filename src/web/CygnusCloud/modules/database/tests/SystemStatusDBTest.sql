/*
 This SQL script creates the system status database.
 Author: Luis Barrios Hernandez
 Version: 1.0
 */

DROP DATABASE IF EXISTS SystemStatusDBTest;

CREATE DATABASE SystemStatusDBTest;

USE SystemStatusDBTest;
 
CREATE TABLE IF NOT EXISTS VirtualMachineServer(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
    serverStatus VARCHAR(20) NOT NULL, serverIP VARCHAR(15) NOT NULL,
    serverPort INTEGER NOT NULL, UNIQUE(serverIP, serverPort)) ENGINE=MEMORY;
    
DELETE FROM VirtualMachineServer;

CREATE TABLE IF NOT EXISTS VirtualMachineDistribution(
    serverName VARCHAR(30),
    virtualMachineID INTEGER,
    PRIMARY KEY (serverName, virtualMachineID),
    FOREIGN KEY (serverName) REFERENCES VirtualMachineServer(serverName)
        ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
        
DELETE FROM VirtualMachineDistribution;

CREATE TABLE IF NOT EXISTS ActiveVirtualMachines(
	serverName VARCHAR(30), userID BIGINT, virtualMachineID INTEGER, virtualMachineName VARCHAR(30),
	port INTEGER, password VARCHAR(65),
	PRIMARY KEY (serverName, userID, virtualMachineID)) ENGINE=MEMORY;
	
DELETE FROM ActiveVirtualMachines;
