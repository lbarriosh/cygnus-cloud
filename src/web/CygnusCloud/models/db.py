'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
   
    File: db.py   
    Version: 1.3
    Description: tables definitions
   
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández, 
                      Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

'''

# -*- coding: utf-8 -*-
from gluon import *


from configuration import DBConfigurator
from gluon.tools import Auth
from userInputConstants import rootPassword
import os





conf = DBConfigurator(rootPassword)
conf.createDatabase('CygnusCloudUserDB')
conf.addUser('CygnusCloud','cygnuscloud2012', 'CygnusCloudUserDB')
userDB = DAL('mysql://CygnusCloud:cygnuscloud2012@localhost/CygnusCloudUserDB',migrate_enabled=True, pool_size=0)


# Autentication
auth = Auth(userDB)
auth.define_tables(migrate = True)




#userDB.auth_user.email.requires = IS_NOT_IN_DB(userDB, userDB.auth_user.email)


userDB.define_table('ClassGroup',
   Field('yearGroup','integer', 'reference auth_user'),
   Field('cod','integer','reference Subjects'),
   Field('curseGroup', length=1),
   Field('placesNumber','integer'),
   Field('career',length=100),
   primarykey=['cod','curseGroup'],migrate= True)

userDB.define_table('UserGroup',
   Field('userId',length = 512 ),
   Field('cod','integer','reference ClassGroup'),
   Field('curseGroup',length=1 ),
   primarykey=['cod','curseGroup','userId'],migrate= True)

userDB.define_table('Subjects',
   Field('code','integer'),
   Field('name',length=50),
   primarykey=['code'],migrate= True)



userDB.define_table('VMByGroup',
   Field('VMId','integer'),
   Field('cod','integer','reference UserGroup'),
   Field('curseGroup',length=1 ),
   primarykey=['cod','curseGroup','VMId'],migrate= True)
   
userDB.define_table('osPictures',
   Field('osPictureId','integer'),
   Field('picturePath',length=100 ),
   primarykey=['osPictureId'],migrate= True)
   
userDB.define_table('pictureByOSId',
   Field('osId','integer'),
   Field('variantId','integer'),
   Field('pictureId','integer','reference osPictures'),
   primarykey=['osId','variantId'],migrate= True)
   
userDB.define_table('userImage',
    Field('userId',length = 512 ),
    Field('file', 'upload'),
    primarykey=['userId',],migrate= True)
    
userDB.define_table('careerPictures',
   Field('careerName',length=100),
   Field('picturePath',length=100 ),
   primarykey=['careerName'],migrate= True)
