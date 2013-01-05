#coding=utf-8

import libvirt

class libvirtConnector():
     
    KVM = "qemu"
    Xen = "xen"
    ESX = "esx"
    
    def __init__(self, hypervisor, connectionMethod = "", userName = "", host = "", password = ""):
        # Creamos la uri para conectarnos 
        # según las opciones que haya introducido
        uri = ""
        uri += hypervisor
        if (connectionMethod != ""):
            uri += "+"+connectionMethod
        uri += "://"
        if (userName != ""):
            uri += userName + "@" + host
        uri += "/system"
        # Nos conectamos a libvirt con esa uri
        self.connector = libvirt.openAuth(uri, [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], self.putPassword, None], 0)
    
    #No se llama 
    def putPassword(self, credentials, user_data):
        print("eh!")
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME or credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                # prompt the user to input a authname. display the provided message
                credential[4] = raw_input(credential[1] + ": ")
    
                # if the user just hits enter raw_input() returns an empty string.
                # in this case return the default result through the last item of
                # the list
                if len(credential[4]) == 0:
                    credential[4] = credential[3]
            elif credential[0] == libvirt.VIR_CRED_NOECHOPROMPT:
                # use the getpass module to prompt the user to input a password.
                # display the provided message and return the result through the
                # last item of the list
                return 0
            else:
                return -1
    
        return 0
    
    def listDomains(self):
        """
        TODO: Solo devuelde los dominios definidos que no estan activos,
        se debería usar listAllDomains, pasandole todos los flags interesantes
        http://www.libvirt.org/html/libvirt-libvirt.html#virConnectListAllDomainsFlags
        """
        return self.connector.listDefinedDomains()
        

    def listStartedDomains(self):
        startedDomains = []
        for domain in self.listDomains():
            if (domain.state in self.connector.listDom):
                startedDomains = [startedDomains, domain]
        
    """
    Create a domain from a xml config file and start it
    """
    def startDomain(self, name, xmlDef = None):
        if (xmlDef != None):
            # TODO: Definir el dominio con el nombre que se me pasa
            pass
        if (name not in self.listDomains()):
            raise 
        
        if (name in self.listStartedDomains()):
            pass
def main():
    #Si se quita el comentario te pide la contraseña en vez de llamar al callback para que la devuelva
    con = libvirtConnector(libvirtConnector.KVM #, "ssh", "saguma", "192.168.1.3"
                           )
    con.listDomains()
    raw_input()
    
main() 