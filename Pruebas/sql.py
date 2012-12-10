'''
Created on 09/12/2012

@author: adrian
'''
import MySQLdb
db=MySQLdb.connect(host='localhost',user='root',
                   passwd='',db='prueba')
cursor=db.cursor()
sql='Select * From usuarios'
cursor.execute(sql)
resultado=cursor.fetchall()
print('Datos de Usuarios')
for registro in resultado:
    print(registro[0] , '->' , registro[1])