
import MySQLdb

def aniadirUsuario(cursor,table,user,con):
    """Metodo que anniade un usuario a una tabla"""
    comand = 'INSERT INTO ' + table + ' VALUES ("' + user + '","' + con + '");'
    cursor.execute(comand)

def mostrarUsuarios(cursor):
    sql='Select * From Usuarios'
    cursor.execute(sql)
    resultado=cursor.fetchall()
    print('Datos de Usuarios')
    for registro in resultado:
        print(registro[0] , '->' , registro[1])

# Nos conectamos a MySql y accedemos a la base de datos
#  creandola en caso de que no exista
db=MySQLdb.connect(host='localhost',user='root',
                   passwd='')
cursor=db.cursor()

#Creamos la base de datos
sql = 'CREATE DATABASE IF NOT EXISTS GestorUsuarios'
cursor.execute(sql)
#Pasamos a usar la BD
sql = 'USE GestorUsuarios'
cursor.execute(sql)
#Creamos una tabla para la BD
sql = 'CREATE TABLE IF NOT EXISTS Usuarios(Nombre VARCHAR(20),Contrasenna VARCHAR(20))'
cursor.execute(sql)
#Anniadimos algun elemento a la tabla
aniadirUsuario(cursor,'Usuarios','Adri','123')
aniadirUsuario(cursor,'Usuarios','Luis','456')
aniadirUsuario(cursor,'Usuarios','Samuel','789')

#Mostramos los resultados
mostrarUsuarios(cursor)

#Cerramos la BD
db.close()