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
