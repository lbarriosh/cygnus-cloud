# coding: utf8

#Método encargado de manejar la página de arranque de máquinas para el usuario
@auth.requires_membership('Student')
def runVM():
    #actualizamos la barra
    createAdressBar()
    return dict()
    
   
def createAdressBar():
    response.menu=[[T('Arrancar máquina'),False,URL('runVM')]]
