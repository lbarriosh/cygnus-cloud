#coding=utf-8
import libvirt
import os.path

class GestorLibvirt:
    def __init__(self, uriConexion):
        self.conexion = libvirt.open(uriConexion)
    
    #Inicia el dominio con nombre 'dominioBase'. 
    #Si no existe, lo crea a partir de un archivo de configuración con el nombre del dominio 
    def iniciarDominio(self,dominio):
        
        if (not self.estaDominioDefinido(dominio)):
            if os.path.isfile(dominio + '.xml'):
                self.conexion.defineXML(dominio+'.xml')
            else:
                print("El dominio no está definido y el no existe el archivo de configuracion "+dominio+".xml")
                return
        dominio = self.conexion.lookupByName(dominio)
        dominio.create()
        
    # Dice si un dominio dado está definido o no
    def estaDominioDefinido(self, dominio):
        return dominio in self.conexion.listDefinedDomains()
    
    def estadoDominio(self,dominio):
        if (not self.estaDominioDefinido(dominio)):
            print("El dominio no está definido")
            return
        dominio = self.conexion.lookupByName(dominio)
        return dominio.state(0)
    
    def dominiosDefinidos(self):
        return self.conexion.listDefinedDomains()
    
    def dominiosIniciados(self):
        ret = []
        for dominio in self.dominiosDefinidos():
            estado, razon = self.conexion.lookupByName(dominio).state(0)
            if (estado == libvirt.VIR_DOMAIN_RUNNING):
                ret = [ret, estado]
        return ret
        
## Funcion de entrada del programa
def main():
    salir = False
    gestor = GestorLibvirt('qemu:///system')
    while not salir:
        print("1. Iniciar un dominio")
        print("2. Conocer el estado de un dominio")
        print("3. Listar dominios definidos")
        print("4. Listar dominios arrancados")
        opcion = raw_input()
        if opcion == '1':
            print('Nombre del dominio a iniciar')
            dominio = raw_input()
            gestor.iniciarDominio(dominio)
        elif opcion == '2':
            print('Nombre del dominio')
            dominio = raw_input()
            print(gestor.estadoDominio(dominio))
        elif opcion == '3':
            print(gestor.dominiosDefinidos())
        elif opcion == '4':
            print(gestor.dominiosIniciados())
        elif opcion == 's':
            break
        else:
            print("Opcion no implementada")
       
    
    
    
    
main()