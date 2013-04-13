/*
 * Base de datos del repositorio. En ella se guardará la información de 
 * las imagenes del sistema, tal como ruta de los archivos de la imagen,
 * y datos de identificación.
 */
CREATE DATABASE IF NOT EXISTS RepositoryDB;

USE RepositoryDB;

CREATE TABLE IF NOT EXISTS Images(
	imageID INTEGER PRIMARY KEY, 
	compressImagePath VARCHAR(100),
	groupId INTEGER);
