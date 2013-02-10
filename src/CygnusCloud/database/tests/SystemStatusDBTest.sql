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
