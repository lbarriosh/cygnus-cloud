/*
 *  ========================================================================
 *                                   CygnusCloud
 *  ======================================================================== 
 *
 *  File: VMServerDB.sql    
 *  Version: 6.0
 *  Description: image repository database schema 
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
CREATE DATABASE IF NOT EXISTS VMServerDB;

USE VMServerDB;

CREATE TABLE IF NOT EXISTS Image(ImageID INTEGER PRIMARY KEY, 
	osImagePath VARCHAR(100), dataImagePath VARCHAR(100),
	definitionFilePath VARCHAR(100), bootable BOOL);
	
CREATE TABLE IF NOT EXISTS ActiveVM(domainName VARCHAR(30) PRIMARY KEY, ImageID INTEGER, 
	VNCPort INTEGER, VNCPass VARCHAR(65),
	userId INTEGER, websockifyPID INTEGER,
	osImagePath VARCHAR(100), dataImagePath VARCHAR(100),
	macAddress VARCHAR(20), uuid VARCHAR(40));

CREATE TABLE IF NOT EXISTS ActiveDomainUIDs(domainName VARCHAR(30) PRIMARY KEY, commandID VARCHAR(70) NOT NULL,
	FOREIGN KEY (domainName) REFERENCES ActiveVM(domainName) ON DELETE CASCADE ON UPDATE CASCADE);
	
CREATE TABLE IF NOT EXISTS CompressionQueue(position INTEGER AUTO_INCREMENT PRIMARY KEY, data VARCHAR(420));
						
CREATE TABLE IF NOT EXISTS TransferQueue(position INTEGER AUTO_INCREMENT PRIMARY KEY, data VARCHAR(230));
						
CREATE TABLE IF NOT EXISTS ConnectionDataDictionary(dict_key VARCHAR(70) PRIMARY KEY, value VARCHAR(21));
