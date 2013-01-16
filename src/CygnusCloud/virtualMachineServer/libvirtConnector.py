#coding=utf-8

import threading
import libvirt

class libvirtConnector():
     
    KVM = "qemu"
    Xen = "xen"
    
    __eventLoopThread = None
    
    def __init__(self, hypervisor, startCallback, undefineCallback):
        # Initialization of event thread
        if self.__eventLoopThread == None:
            self.virEventLoopNativeStart()
        # Create the uri 
        uri = ""
        uri += hypervisor
        uri += "://"
        uri += "/system"
        # Connect to lbvirt and register the events
        self.connector = libvirt.openReadOnly(uri)
        self.connector.domainEventRegisterAny(None, 
                                              libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE, 
                                              self.__eventDomain, 
                                              [startCallback, undefineCallback])

    def __eventDomain(self, conn, domain, eventID, detail, data):
        eventHandler = {
         libvirt.VIR_DOMAIN_EVENT_DEFINED: self.__definedHandler,
         libvirt.VIR_DOMAIN_EVENT_UNDEFINED: data[1],
         libvirt.VIR_DOMAIN_EVENT_STARTED: data[0],
         libvirt.VIR_DOMAIN_EVENT_SUSPENDED: self.__suspendedHandler,
         libvirt.VIR_DOMAIN_EVENT_RESUMED: self.__resumedHandler,
         libvirt.VIR_DOMAIN_EVENT_STOPPED: self.__stoppedHandler,
         libvirt.VIR_DOMAIN_EVENT_SHUTDOWN: self.__shutdownHandler}
        eventHandler[eventID](domain)
        
    def __definedHandler(self, domain):
        '''
        Create the domain defined
        '''
        domain.create()
        
    def __suspendedHandler(self, domain):
        pass
    def __resumedHandler(self, domain):
        pass
    def __stoppedHandler(self, domain):
        '''
        Undefine the domain when it is stopped (when an error ocurred)
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
        self.connector.defineXML(xmlConfig)
        
    def getNumberOfDomains(self):
        self.connector.numOfDomains()
        
    @staticmethod
    def virEventLoopNativeRun():
        while True:
            libvirt.virEventRunDefaultImpl()
            
    @staticmethod
    def virEventLoopNativeStart():
        libvirt.virEventRegisterDefaultImpl()
        __eventLoopThread = threading.Thread(target=libvirtConnector.virEventLoopNativeRun, name="libvirtEventLoop")
        __eventLoopThread.setDaemon(True)
        __eventLoopThread.start()

if __name__ == "__main__" :
    libvirtConnector.virEventLoopNativeStart()
    con = libvirtConnector(libvirtConnector.KVM,{})
    con.startDomain(open("/home/saguma/Documentos/Universidad/config.xml", "r").read())
    raw_input()