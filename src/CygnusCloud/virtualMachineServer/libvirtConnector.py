#coding=utf-8

import threading
import libvirt
try :
    import xml.etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET
    
class libvirtConnector():
     
    KVM = "qemu"
    Xen = "xen"
    
    __eventLoopThread = None
    
    def __init__(self, hypervisor, startCallback, shutdownCallback):
        # Initialization of event thread
        if self.__eventLoopThread == None:
            self.virEventLoopNativeStart()
        
        self.__startCallback = startCallback
        self.__shutdownCallback = shutdownCallback
        # Create the uri 
        uri = ""
        uri += hypervisor
        uri += "://"
        uri += "/system"
        # Connect to lbvirt and register the events
        self.__connector = libvirt.open(uri)
        self.__connector.domainEventRegisterAny(None, 
                                              libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE, 
                                              self.__eventDomain, None)

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
        
    def __definedHandler(self, domain):
        pass
    def __suspendedHandler(self, domain):
        pass
    def __resumedHandler(self, domain):
        pass
    def __undefinedHandler(self, domain):
        pass
    def __stoppedHandler(self, domain):
        domainInfo = {"name" : domain.name()}
        self.__shutdownCallback(domainInfo)
        pass
    def __shutdownHandler(self, domain):
        pass
    def __startedHandler(self, domain):
        xml = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        graphic_element = xml.find('.//graphics')
        port = graphic_element.attrib['port']
        password = graphic_element.attrib['passwd']
        listen_element = graphic_element.find('.//listen')
        ip = listen_element.attrib['address']
        domainInfo = {"name" : domain.name(),
                      "VNCport" : int(port),
                      "VNCip" : ip,
                      "VNCpassword" : password}
        self.__startCallback(domainInfo)
    
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
        self.__connector.createXML(xmlConfig, libvirt.VIR_DOMAIN_NONE)
        
    def stopAllDomains(self):
        idsMV = self.__connector.listDomainsID()
        for vmID in idsMV:
            domain = self.__connector.lookupByID(vmID)
            domain.destroy()
            
    def getActiveDomainNames(self):
        idsMV = self.__connector.listDomainsID()
        result = []
        for vmID in idsMV:
            domain = self.__connector.lookupByID(vmID)
            xml = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
            domainName = xml.find('.//name').text
            result.append(domainName)
        return result
    
    def getNumberOfDomains(self):
        return self.__connector.numOfDomains()
        
    @staticmethod
    def virEventLoopNativeRun():
        while True:
            libvirt.virEventRunDefaultImpl()
    

    @staticmethod
    def virEventLoopNativeStart():
        libvirt.virEventRegisterDefaultImpl()
        __eventLoopThread = threading.Thread(target=libvirtConnector.virEventLoopNativeRun, name="libvirt event loop")
        __eventLoopThread.setDaemon(True)
        __eventLoopThread.start()

def dummy(domain):
    pass

if __name__ == "__main__" :
    libvirtConnector.virEventLoopNativeStart()
    con = libvirtConnector(libvirtConnector.KVM,dummy, dummy)
    raw_input()