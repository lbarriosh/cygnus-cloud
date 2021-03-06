/*
 *  ========================================================================
 *                                   CygnusCloud
 *  ======================================================================== 
 *
 *  File: ImageRepositoryDB.sql    
 *  Version: 1.0
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
CREATE DATABASE IF NOT EXISTS ImageRepositoryDB;

USE ImageRepositoryDB;

CREATE TABLE IF NOT EXISTS Image(
	imageID INTEGER PRIMARY KEY AUTO_INCREMENT, 
	compressedFilePath VARCHAR(100),
	imageStatus TINYINT);

