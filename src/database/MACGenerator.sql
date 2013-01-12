# Script encargado de generar una tabla con una secuencia de direcciones MAC libres de forma automática

#Abrimos la base de datos
USE prueba1;

#Creamos la tabla necesaria
CREATE TABLE IF NOT EXISTS freeMacs(MAC VARCHAR(20) PRIMARY KEY);



 #Creamos la secuencia
 SET @v = 0;

 #Generamos el bucle
 WHILE @v < 256 DO
    SET @x = HEX("'" + @v + "'");
    INSERT INTO freeMacs VALUES ("2C:00:00:00:00:" + @x);
    SET @v = @v + 1;
 END WHILE;
