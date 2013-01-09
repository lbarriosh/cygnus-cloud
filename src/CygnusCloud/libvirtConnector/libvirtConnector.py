#coding=utf-8

import threading
import libvirt

class libvirtConnector():
     
    KVM = "qemu"
    Xen = "xen"
    
    def __init__(self, hypervisor, eventCallbacks):
        # Creamos la uri para conectarnos 
        uri = ""
        uri += hypervisor
        uri += "://"
        uri += "/system"
        # Nos conectamos a libvirt con esa uri
        self.connector = libvirt.open(uri)
        self.connector.domainEventRegisterAny(None, 
                                              libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE, 
                                              self.__eventDomain, 
                                              None)

    def __eventDomain(self, conn, domain, eventID, detail, data):
        eventHandler = {
         libvirt.VIR_DOMAIN_EVENT_DEFINED: self.__definedHandler,
         libvirt.VIR_DOMAIN_EVENT_UNDEFINED: self.__undefinedHandler,
         libvirt.VIR_DOMAIN_EVENT_STARTED: self.__startedHandler,
         libvirt.VIR_DOMAIN_EVENT_SUSPENDED: self.__suspendedHandler,
         libvirt.VIR_DOMAIN_EVENT_RESUMED: self.__resumedHandler,
         libvirt.VIR_DOMAIN_EVENT_STOPPED: self.__stoppedHandler,
         libvirt.VIR_DOMAIN_EVENT_SHUTDOWN: self.__shutdownHandler}
        eventHandler[eventID](domain)
        #data[eventID](domain)
        
    def __definedHandler(self, domain):
        pass
    def __undefinedHandler(self, domain):
        '''
        Mark as free the resources in the database
        TODO
        '''
        pass
    def __startedHandler(self, domain):
        '''
        Start websockify for noVNC (vnc web client)
        TODO
        '''
        pass
    def __suspendedHandler(self, domain):
        pass
    def __resumedHandler(self, domain):
        pass
    def __stoppedHandler(self, domain):
        '''
        Undefine the domain when it is shutdown
        '''
        domain.undefine()
        
    def __shutdownHandler(self, domain):
        '''
        Undefine the domain when it is shutdown
        '''
        domain.undefine()
    
    def startDomain(self, xmlConfig):
        '''
        Define a domain and start it
        Args:
            xmlConfig: Config to create domain in xml format
        Returns:
            Nothing
        Raises:
            libvirtError: if an error ocurred defining or starting the domain
        '''
        domain = self.connector.defineXML(xmlConfig)
        domain.create()
        
    @staticmethod
    def virEventLoopNativeRun():
        while True:
            libvirt.virEventRunDefaultImpl()
            
    @staticmethod
    def virEventLoopNativeStart():
        libvirt.virEventRegisterDefaultImpl()
        eventLoopThread = threading.Thread(target=libvirtConnector.virEventLoopNativeRun, name="libvirtEventLoop")
        eventLoopThread.setDaemon(True)
        eventLoopThread.start()

if __name__ == "__main__" :
    libvirtConnector.virEventLoopNativeStart()
    con = libvirtConnector(libvirtConnector.KVM,{})
    con.startDomain(open("/home/saguma/Documentos/Universidad/config.xml", "r").read())
    raw_input()