DROP DATABASE IF EXISTS CommandsDBTest;

CREATE DATABASE CommandsDBTest;

USE CommandsDBTest;

CREATE TABLE QueuedCommand(
	userID INT,
	time DOUBLE,
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;

CREATE TABLE PendingCommand(
	userID INT,
	time DOUBLE,
	commandType TINYINT NOT NULL,
	commandArgs VARCHAR(100),
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
	
CREATE TABLE RunCommandOutput(
	userID INT,
	time DOUBLE,
	outputType TINYINT NOT NULL,
	commandOutput VARCHAR(100),
	isNotification BOOL,
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
