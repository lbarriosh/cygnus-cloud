# coding: utf8
from gluon import *
# Método encargado de la página de inicio de sesión



def login():
    #Iniciamos los valores, si procede
    initValues() 
    #iniciamos el arranque con el mainserver
    #initMainServerConnection()
    #Creamos la barra de direcciones
    createAdressBar()
    #Gestionamos los usuarios ya logueados
    auth.settings.controller = 'main'
    auth.settings.login_onaccept = loginAccess
    #auth.settings.login_next = URL(c='main',f='login')  
    return dict(form=auth.login())
    
#Metodo encargado de la página "Acerca de"
def about():
    #Creamos la barra de direcciones
    createAdressBar()    
    #Cargamos el fichero html
    info = LOAD(url=URL('static', 'info.html', scheme='http'),ajax=False)
    print info
    return dict(info = info)

#Página encargada de crear el menu de direcciones    
def createAdressBar():
    response.menu=[[T('Iniciar sesión'),False,URL('login')],
                   [T('Acerca de'),False,URL('about')]]

def initValues():
    if(userDB(userDB.auth_user.email == 'Admin1@ucm.es').count() == 0):
        #Añadimos los grupos
        userDB.auth_group.insert(role = 'Student',description =  'Only run virtual machines available')
        userDB.auth_group.insert(role = 'Administrator',description =  'All privilages available')
        #auth.add_group('Administrator', 'All privilages available')
        #Usuario de prueba
        u1 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Admin1@ucm.es',first_name='Bertoldo',last_name='Pedralbes')
        u2 = userDB.auth_user.insert(password = userDB.auth_user.password.validate('1234')[0],email = 'Student1@ucm.es',first_name='Robert',last_name='Neville')
        
        #Enlazamos los usuarios a los grupos
        auth.add_membership('Administrator',u1)
        auth.add_membership('Student',u2)
        print userDB.tables
        
               
        
        
@auth.requires_login()                                      
def loginAccess(state):
    #rows = userDB(userDB.auth_membership.user_id==auth.user_id).select(userDB.auth_membership.group_id)
    print auth.user_id
    if(auth.has_membership(role='Student')):
        redirect(URL(c='student',f='runVM'))
    elif(auth.has_membership(role='Administrator')):
        redirect(URL(c='administrator',f='runVM'))

@auth.requires_login()          
def logoutUser():
     auth.logout(URL(c='main',f='login'))
