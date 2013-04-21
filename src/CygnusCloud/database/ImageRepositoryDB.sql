/*
 * Base de datos del repositorio. En ella se guardará la información de 
 * las imagenes del sistema, tal como ruta de los archivos de la imagen,
 * y datos de identificación.
 */
CREATE DATABASE IF NOT EXISTS ImageRepositoryDB;

USE ImageRepositoryDB;

CREATE TABLE IF NOT EXISTS Image(
	imageID INTEGER PRIMARY KEY AUTO_INCREMENT, 
	compressedFilePath VARCHAR(100),
	imageStatus TINYINT, 
	groupId INTEGER, UNIQUE(compressedFilePath));
