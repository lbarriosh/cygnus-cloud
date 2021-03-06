/*
 *  ========================================================================
 *                                   CygnusCloud
 *  ======================================================================== 
 *
 *  File: ClusterEndpointDB.sql    
 *  Version: 5.0
 *  Description: cluster endpoint database schema 
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
 
CREATE DATABASE IF NOT EXISTS ClusterEndpointDB;

USE ClusterEndpointDB;
 
CREATE TABLE IF NOT EXISTS VirtualMachineServer(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
    serverStatus VARCHAR(30) NOT NULL, serverIP VARCHAR(15) NOT NULL,
    serverPort INTEGER NOT NULL, isVanillaServer TINYINT, UNIQUE(serverIP, serverPort)) ENGINE=MEMORY;
    
DELETE FROM VirtualMachineServer;

CREATE TABLE IF NOT EXISTS VirtualMachineServerStatus(serverName VARCHAR(30) PRIMARY KEY NOT NULL, 
	hosts INTEGER, ramInUse INTEGER, ramSize INTEGER, freeStorageSpace INTEGER, availableStorageSpace INTEGER,
	freeTemporarySpace INTEGER, availableTemporarySpace INTEGER, activeVCPUs TINYINT,
	physicalCPUs TINYINT, 
	FOREIGN KEY(serverName) REFERENCES VirtualMachineServer(serverName) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=MEMORY;
	
DELETE FROM VirtualMachineServerStatus;

CREATE TABLE IF NOT EXISTS ImageRepositoryStatus(repositoryID TINYINT PRIMARY KEY, freeDiskSpace INTEGER,
	availableDiskSpace INTEGER, repositoryStatus VARCHAR(30)) ENGINE=MEMORY;
	
DELETE FROM ImageRepositoryStatus;

CREATE TABLE IF NOT EXISTS VirtualMachineDistribution(
    serverName VARCHAR(30),
    imageID INTEGER,
    imageStatus VARCHAR(25),
    PRIMARY KEY (serverName, imageID)) ENGINE=MEMORY;

DELETE FROM VirtualMachineDistribution;
        
CREATE TABLE IF NOT EXISTS ActiveVirtualMachines(
	serverName VARCHAR(30), domainUID VARCHAR(70) PRIMARY KEY, ownerID BIGINT, imageID INTEGER, virtualMachineName VARCHAR(30),
	port INTEGER, password VARCHAR(65),
	UNIQUE (serverName, ownerID, imageID)) ENGINE=MEMORY;
	
DELETE FROM ActiveVirtualMachines;

CREATE TABLE IF NOT EXISTS VanillaImageFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(20),
    ramSize INTEGER, vCPUs TINYINT, osDiskSize INTEGER, dataDiskSize INTEGER,
    UNIQUE(familyName));
    
INSERT IGNORE INTO VanillaImageFamily VALUES (1, 'Linux-Small', 1048576, 1, 5242880, 3145728); 
INSERT IGNORE INTO VanillaImageFamily VALUES (2, 'Linux-Medium', 2097152, 2, 10485760, 6291456);
INSERT IGNORE INTO VanillaImageFamily VALUES (3, 'Linux-Big', 3145728, 4, 15728640, 12582912);
INSERT IGNORE INTO VanillaImageFamily VALUES (4, 'Windows7-Small',  1048576, 1, 20971520, 4194304);
INSERT IGNORE INTO VanillaImageFamily VALUES (5, 'Windows7-Medium', 2097152, 2, 31457280, 8388608);
INSERT IGNORE INTO VanillaImageFamily VALUES (6, 'Windows7-Big', 3145728, 4, 41943040, 16777216);

CREATE TABLE IF NOT EXISTS OSFamily(familyID SMALLINT PRIMARY KEY, familyName VARCHAR(30));

/*
The following lines are provided as an example

INSERT IGNORE INTO OSFamily VALUES
	(1, 'Linux'),
	(2, 'Windows');
*/
	
CREATE TABLE IF NOT EXISTS OSVariant(familyID SMALLINT, variantID SMALLINT, variantName VARCHAR(30),
	PRIMARY KEY(familyID, variantID),
	FOREIGN KEY(familyID) REFERENCES OSFamily(familyID));

/*
The following lines are provided as an example

INSERT IGNORE INTO OSVariant VALUES
	(1, 1, 'Debian Squeeze AMD64'),
	(2, 1, 'Windows 7 Professional x86');
*/
	
CREATE TABLE IF NOT EXISTS Image(imageID INTEGER PRIMARY KEY, vanillaImageFamilyID SMALLINT, name VARCHAR(20), description VARCHAR(200), 
	osFamily SMALLINT, osVariant SMALLINT, isBaseImage BOOL, isBootable BOOL,
	FOREIGN KEY(vanillaImageFamilyID) REFERENCES VanillaImageFamily(familyID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(osFamily, osVariant) REFERENCES OSVariant(familyID, variantID) ON DELETE CASCADE ON UPDATE CASCADE);

/*
The following lines are provided as an example

INSERT IGNORE INTO Image VALUES
	(1, 1, 'Debian-Squeeze', 'Imagen vanilla', 1, 1, 1, 0);
*/
	
CREATE TABLE IF NOT EXISTS EditedImage(temporaryID VARCHAR(70) PRIMARY KEY, vanillaImageFamilyID SMALLINT, 
	imageID INTEGER, name VARCHAR(20), description VARCHAR(200),
	osFamily SMALLINT, osVariant SMALLINT, ownerID INTEGER, state TINYINT, editedImage BOOLEAN,
	FOREIGN KEY(vanillaImageFamilyID) REFERENCES VanillaImageFamily(familyID),
	FOREIGN KEY(osFamily, osVariant) REFERENCES OSVariant(familyID, variantID) ON DELETE CASCADE ON UPDATE CASCADE);
