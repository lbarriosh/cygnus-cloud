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
    serverPort INTEGER NOT NULL, UNIQUE(serverIP, serverPort)) ENGINE=MEMORY;
    
DELETE FROM VirtualMachineServer;
    
CREATE TABLE IF NOT EXISTS Image(name VARCHAR(20) PRIMARY KEY NOT NULL, description VARCHAR(200))
    ENGINE=MEMORY;
    
DELETE FROM Image;
