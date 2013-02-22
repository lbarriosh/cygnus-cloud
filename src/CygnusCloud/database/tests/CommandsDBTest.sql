DROP DATABASE IF EXISTS CommandsDBTest;

CREATE DATABASE CommandsDBTest;

USE CommandsDBTest;

CREATE TABLE Command(
	userID INT,
	time BIGINT UNSIGNED,
	commandType TINYINT NOT NULL,
	commandArgs VARCHAR(100),
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
	
CREATE TABLE CommandOutput(
	userID INT,
	time BIGINT UNSIGNED,
	outputType TINYINT NOT NULL,
	commandOutput VARCHAR(100),
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;
