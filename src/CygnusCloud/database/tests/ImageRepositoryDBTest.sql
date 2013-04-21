/*
 * Base de datos del repositorio. En ella se guardará la información de 
 * las imagenes del sistema, tal como ruta de los archivos de la imagen,
 * y datos de identificación.
 */
CREATE DATABASE IF NOT EXISTS ImageRepositoryDBTest;

USE ImageRepositoryDBTest;

DROP TABLE IF EXISTS Image;

CREATE TABLE Image(
	imageID INTEGER PRIMARY KEY AUTO_INCREMENT, 
	compressedFilePath VARCHAR(100),
	imageStatus TINYINT, 
	groupId INTEGER, UNIQUE(compressedFilePath));
