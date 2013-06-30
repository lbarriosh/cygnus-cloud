/*
 *  ========================================================================
 *                                   CygnusCloud
 *  ======================================================================== 
 *
 *  File: CommandsDB.sql    
 *  Version: 2.0
 *  Description: commands database schema 
 *
 *  Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
 *      Samuel Guayerbas Martín       
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
DROP DATABASE IF EXISTS CommandsDB;

CREATE DATABASE CommandsDB;
USE CommandsDB;


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
	commandOutput VARCHAR(200),
	isNotification BOOL,
	PRIMARY KEY(userID, time))
	ENGINE=MEMORY;

ALTER DATABASE CommandsDB CHARACTER SET utf8 COLLATE utf8_general_ci;
