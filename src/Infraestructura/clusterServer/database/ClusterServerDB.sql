/*
 *  ========================================================================
 *                                   CygnusCloud
 *  ======================================================================== 
 *
 *  File: ClusterServerDB.sql    
 *  Version: 5.0
 *  Description: cluster server database repository schema 
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


CREATE DATABASE IF NOT EXISTS ClusterServerDB;

USE ClusterServerDB;

CREATE TABLE IF NOT EXISTS VMServer(serverId INTEGER PRIMARY KEY AUTO_INCREMENT, 
	serverName VARCHAR(30) NOT NULL, serverStatus INTEGER, serverIP VARCHAR(15), serverPort INTEGER,
	isEditionServer BIT, UNIQUE(serverName), UNIQUE(serverIP, serverPort));

CREATE TABLE IF NOT EXISTS ImageOnServer(serverId INTEGER, imageId INTEGER, status TINYINT,
	PRIMARY KEY(serverId,imageId),
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS VMServerStatus(serverId INTEGER PRIMARY KEY, hosts INTEGER,
	ramInUse INTEGER, ramSize INTEGER, freeStorageSpace INTEGER, availableStorageSpace INTEGER,
	freeTemporarySpace INTEGER, availableTemporarySpace INTEGER, activeVCPUs TINYINT,
	physicalCPUs TINYINT, 
	FOREIGN KEY(serverId) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DELETE FROM VMServerStatus;
	
CREATE TABLE IF NOT EXISTS AllocatedVMServerResources(commandID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	ramInUse INTEGER, freeStorageSpace INTEGER, freeTemporarySpace INTEGER, activeVCPUs TINYINT, activeHosts TINYINT, remove BOOL, 
	FOREIGN KEY(serverID) REFERENCES VMServer(serverId) ON DELETE CASCADE ON UPDATE CASCADE)
	ENGINE=MEMORY;
	
DELETE FROM AllocatedVMServerResources;
	
CREATE TABLE IF NOT EXISTS VMFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(20),
    ramSize INTEGER, vCPUs TINYINT, osDiskSize INTEGER, dataDiskSize INTEGER,
    UNIQUE(familyName));
    
CREATE TABLE IF NOT EXISTS VMFamilyOf(imageID INTEGER, familyID SMALLINT,
	PRIMARY KEY(familyID, imageID),
	FOREIGN KEY(familyID) REFERENCES VMFamily(familyID));
	
CREATE TABLE IF NOT EXISTS VMFamilyOfNewVM(temporaryID VARCHAR(70) PRIMARY KEY, familyID SMALLINT,
	FOREIGN KEY(familyID) REFERENCES VMFamily(familyID));
	
DROP TABLE IF EXISTS ImageRepository;
CREATE TABLE ImageRepository(repositoryIP VARCHAR(15), repositoryPort INTEGER,
	freeDiskSpace INTEGER, availableDiskSpace INTEGER, connection_status TINYINT, PRIMARY KEY(repositoryIP, repositoryPort))
	ENGINE=MEMORY;
		
CREATE TABLE IF NOT EXISTS AllocatedImageRepositoryResources(
	commandID VARCHAR(70) PRIMARY KEY, 
	repositoryIP VARCHAR(15), 
	repositoryPort INTEGER, 
	allocatedDiskSpace INTEGER, 
	remove BOOL, 
	FOREIGN KEY(repositoryIP, repositoryPort) REFERENCES ImageRepository(repositoryIP, repositoryPort) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
		
DELETE FROM AllocatedImageRepositoryResources;
	
DROP TABLE IF EXISTS VMBootCommand;

CREATE TABLE VMBootCommand(commandID VARCHAR(70), dispatchTime double, VMID INT,
    PRIMARY KEY(commandID)) ENGINE=MEMORY;
    
DROP TABLE IF EXISTS ActiveVMDistribution;
    
CREATE TABLE ActiveVMDistribution(vmID VARCHAR(70) PRIMARY KEY, serverID INTEGER,
	FOREIGN KEY(serverID) REFERENCES VMServer(serverID) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
	
CREATE TABLE IF NOT EXISTS ImageEditionCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, UNIQUE(imageID));

CREATE TABLE IF NOT EXISTS ImageDeletionCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, UNIQUE(imageID));

CREATE TABLE IF NOT EXISTS AutoDeploymentCommand(commandID VARCHAR(70) PRIMARY KEY, imageID INTEGER, remainingMessages SMALLINT, error BOOL)
	ENGINE=MEMORY;
	
/*
 * Vanilla image features.
 */
INSERT IGNORE INTO VMFamily VALUES (1, 'Linux-Small', 1048576, 1, 5242880, 3145728); 
INSERT IGNORE INTO VMFamily VALUES (2, 'Linux-Medium', 2097152, 2, 10485760, 6291456);
INSERT IGNORE INTO VMFamily VALUES (3, 'Linux-Big', 3145728, 4, 15728640, 12582912);

INSERT IGNORE INTO VMFamily VALUES (4, 'Windows7-Small',  1048576, 1, 20971520, 4194304);
INSERT IGNORE INTO VMFamily VALUES (5, 'Windows7-Medium', 2097152, 2, 31457280, 8388608);
INSERT IGNORE INTO VMFamily VALUES (6, 'Windows7-Big', 3145728, 4, 41943040, 16777216);

/*
 * Registered virtual machines. The following line is provided as an example.	
INSERT IGNORE INTO VMFamilyOf VALUES (1, 1);
 */
