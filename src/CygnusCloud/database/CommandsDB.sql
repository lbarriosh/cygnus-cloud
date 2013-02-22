DROP DATABASE IF EXISTS CommandsDB;

CREATE DATABASE CommandsDB;

USE CommandsDB;

CREATE TABLE QueuedCommand(
	userID INT,
	time INT UNSIGNED,
	commandType TINYINT NOT NULL,
	commandArgs VARCHAR(100),
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;

CREATE TABLE PendingCommand(
	userID INT,
	time INT UNSIGNED,
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
	
CREATE TABLE RunCommandOutput(
	userID INT,
	time INT UNSIGNED,
	outputType TINYINT NOT NULL,
	commandOutput VARCHAR(100),
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
