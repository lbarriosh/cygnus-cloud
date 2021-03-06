'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
   
    File: main.py   
    Version: 1.5
    Description: public pages access controller
   
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

# coding: utf8
from gluon import *

#Método encargado de iniciar sesión de un usuario
def login():
    #Iniciamos los valores, si procede
    initValues() 
    #Creamos la barra de direcciones
    createAdressBar() 
    #Si ya hay sesión registrada redireccionar
    if auth.user_id:
            loginAccess(0)
    #Gestionamos los usuarios ya logueados
    auth.settings.controller = 'main'
    auth.settings.login_onaccept = loginAccess 
    
    #Creamos el formulario de inicio de sesión
    form = auth.login()  
    form.element("input",_type="submit")['_class'] = "button button-blue"
    form.element("input",_type="submit")['_style'] = "width:120px;height:25px;"
    form.element(_name="email")['_style'] = "width:250px;"
    form.element(_name="password")['_style'] = "width:250px;"
    form.element(_name="password")['_class'] = "inputText"
    form.element("td")['_style'] = "padding: 0px;text-align:center;"
    #Creamos el menú con direcciones externas
    infoLinks = LOAD(url=URL('static', 'externLinks.html', scheme='http'),ajax=False)
    return dict(form=form,infoLinks=infoLinks)
    
#Metodo encargado de la página "Acerca de"
def about():
    #Creamos la barra de direcciones
    createAdressBar()    
    #Cargamos el fichero con la información
    info = LOAD(url=URL('static', 'info.html', scheme='http'),ajax=False)
    return dict(info = info)

#Página encargada de crear el menu de direcciones    
def createAdressBar():
    response.menu=[[T('Iniciar sesión'),False,URL('login')],
                   [T('Acerca de'),False,URL('about')]]

def initValues():
    if(userDB(userDB.auth_group.role == 'Student').count() == 0):
        #Añadimos los grupos
        userDB.auth_group.insert(role = 'Student',description =  'Only run virtual machines available')
        userDB.auth_group.insert(role = 'Teacher',description =  'Run, create and edit virtual machines privilages avaible')
        userDB.auth_group.insert(role = 'Administrator',description =  'All privilages available')
        #Usuario de prueba
        u1 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Admin1@ucm.es',first_name='Bertoldo',last_name='Pedralbes')
        u2 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Student1@ucm.es',first_name='Robert',last_name='Neville')
        u3 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Teacher01@ucm.es',first_name='Charles',last_name='Xavier')
        #Enlazamos los usuarios a los grupos
        auth.add_membership('Administrator',u1)
        auth.add_membership('Student',u2)
        auth.add_membership('Teacher',u3)
        userDB.userImage.import_from_csv_file(open(os.path.join(request.folder,'static','imageUserCSV/userDB_userImage.csv'),'r'))
    if userDB(userDB.osPictures.osPictureId > 0).count() == 0:
        userDB.osPictures.insert(osPictureId= 1,picturePath='images/OS/windows7Icon.png')
        userDB.osPictures.insert(osPictureId= 2,picturePath='images/OS/DebianIcon.png')
        userDB.pictureByOSId.insert(osId= 1,variantId=1 ,pictureId=2)
        userDB.pictureByOSId.insert(osId= 2,variantId=1 ,pictureId=1)


        
               
        

# Método encargado de evaluar la redirección según el tipo de usuario
@auth.requires_login()                                      
def loginAccess(state):
    if(auth.has_membership(role='Student')):
        redirect(URL(c='student',f='runVM'))
    elif(auth.has_membership(role='Administrator')):
        redirect(URL(c='administrator',f='runVM',args = ['run']))
    elif(auth.has_membership(role='Teacher')):
        redirect(URL(c='teacher',f='runVM',args = ['run']))

# Método que redirecciona a la página de inicio de sesión una vez cerrada
@auth.requires_login()          
def logoutUser():
     auth.logout(URL(c='main',f='login'))
