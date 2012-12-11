import MySQLdb

def conectarMySQL(host,user,pasword):
    """Metodo que permite conectarnos a MySQL"""
    db=MySQLdb.connect(host,user,pasword)
    cursor=db.cursor()
    return cursor

def inspeccionarBD(cursor,bd):
    """Metodo que gestiona la BD"""
    #Creamos la base de datos
    sql = 'CREATE DATABASE IF NOT EXISTS ' + bd
    cursor.execute(sql)
    #Pasamos a usar la BD
    sql = 'USE ' + bd
    cursor.execute(sql)
    
def inspeccionarTabla(cursor,tabla):
    """Metodo que gestiona la tabla"""
    #Creamos una tabla para la BD
    sql = 'CREATE TABLE IF NOT EXISTS ' + tabla +'(Nombre VARCHAR(20),Contrasenna VARCHAR(20))'
    cursor.execute(sql)
    
def aniadirUsuario(cursor,table,user,con):
    """Metodo que anniade un usuario a una tabla"""
    comand = 'INSERT INTO ' + table + ' VALUES ("' + user + '","' + con + '");'
    cursor.execute(comand)

def mostrarUsuarios(cursor,tabla):
    """Metodo que muestra el resultado de una tabla"""
    sql='Select * From ' + tabla
    cursor.execute(sql)
    resultado=cursor.fetchall()
    print('Datos de Usuarios')
    for registro in resultado:
        print(registro[0] , '->' , registro[1])
        
def main():
    # Nos conectamos a mySQL
    cursor = conectarMySQL('localhost','root','')
    
    #Preguntamos por la base de datos
    print('Inserte el nombre de la Base de Datos')
    bd = raw_input()
    print(bd)
    #Creamos la BD si no existe y la abrimos
    inspeccionarBD(cursor,bd)
    
    #Preguntamos por la tabla
    print('Inserte el nombre de la Tabla')
    tabla = raw_input()
    print('La Tabla ha sido creada con los campos Nombre y Contrasenia') 
    
    #Creamos la Tabla si no existe y la abrimos
    inspeccionarTabla(cursor,tabla) 
    
    #Aceptamos usuarios mientras el usuario quiera
    while True:
       print('Quiere insertar un nuevo usuario?(s/n)')
       resp = raw_input()
       if resp == 's':
            print('Nombre de usuario:')
            nombre = raw_input()
            print('Contrasenia:')
            con = raw_input()
            aniadirUsuario(cursor,tabla,nombre,con)
       else:
            break
       
    #Una vez anniadidos los usuarios los mostramos
    mostrarUsuarios(cursor,tabla)



#CODIGO A EJECUTAR
main()
 
