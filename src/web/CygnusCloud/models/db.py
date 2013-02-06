# -*- coding: utf-8 -*-
from configuration import DBConfigurator
from gluon.tools import Auth

conf = DBConfigurator('170590ucm')
conf.createDatabase('UseresDB')
#conf.addUser('CygnusCloud','cygnuscloud2012', 'UserDB')
userDB = DAL('mysql://CygnusCloud:cygnuscloud2012@localhost/UseresDB',migrate_enabled=True, pool_size=0)


# Autentication
auth = Auth(userDB)
auth.define_tables(migrate = True)




#userDB.auth_user.email.requires = IS_NOT_IN_DB(userDB, userDB.auth_user.email)




userDB.define_table('UserGroup',
   Field('yearGroup','integer', 'reference Users'),
   Field('cod','integer','reference subjects'),
   Field('curse','integer'),
   Field('curseGroup', length=1),
   primarykey=['cod','curseGroup'],migrate= True)

userDB.define_table('ClassGroup',
   Field('userId','integer', 'reference auth_user' ),
   Field('cod','integer','reference UserGroup'),
   Field('curseGroup','reference UserGroup',length=1 ),
   primarykey=['cod','curseGroup','userId'],migrate= True)

userDB.define_table('Subjects',
   Field('code','integer'),
   Field('name',length=15),migrate= True)



userDB.define_table('VMByGroup',
   Field('VMName',length=20),
   Field('cod','integer','reference UserGroup'),
   Field('curseGroup','reference UserGroup',length=1 ),
   primarykey=['cod','curseGroup','VMName'],migrate= True)

#Añadimos los grupos
userDB.auth_group.insert(role = 'Student',description =  'Only run virtual machines available')
userDB.auth_group.insert(role = 'Administrator',description =  'All privilages available')
#auth.add_group('Administrator', 'All privilages available')
#Usuario de prueba
u1 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Admin1@ucm.es',first_name='Bertoldo',last_name='Pedralbes')

#Enlazamos los usuarios a los grupos
auth.add_membership('Student',u1)
print userDB.tables
