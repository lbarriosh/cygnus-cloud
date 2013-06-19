# coding=utf-8

import threading
import libvirt
try :
    import xml.etree.cElementTree as ET
except ImportError:
    import etree.ElementTree as ET
    
"""
Clase del conector con libvirt
"""
class LibvirtConnector(object):
     
    KVM = "qemu"
    Xen = "xen"  
    
    def __init__(self, hypervisor, startCallback, shutdownCallback):
        """
        Inicializa el estado del conector.
        Argumentos:
            hypervisor: el nombre del hipervisor a utilizar
            startCallback: función que se invocará cuando un dominio arranque
            shutdownCallback: función que se invocará cuando se apague un dominio.
        """
        # Inicializar el hilo de procesamiento de eventos
        self.__startVirEventLoop()            
        
        self.__startCallback = startCallback
        self.__shutdownCallback = shutdownCallback
        # Crear la URI del hipervisor
        uri = ""
        uri += hypervisor
        uri += "://"
        uri += "/system"
        # Conectarnos al hipervisor y procesar los eventos que se generen
        self.__libvirtConnection = libvirt.open(uri)
        self.__libvirtConnection.domainEventRegisterAny(None,
                                              libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                              self.__createDomainEventHandlers, None) 
           
    def __createDomainEventHandlers(self, conn, domain, eventID, detail, data):
        """
        Instala los handlers para los eventos que genera libvirt.
        Argumentos utilizados:
            domain: el dominio asociado al evento
            eventID: el identificador del evento
        Devuelve:
            Nada
        """
        eventHandler = {
         libvirt.VIR_DOMAIN_EVENT_DEFINED: self.__onDomainDefined,
         libvirt.VIR_DOMAIN_EVENT_UNDEFINED: self.__onDomainUndefined,
         libvirt.VIR_DOMAIN_EVENT_STARTED: self.__onDomainStarted,
         libvirt.VIR_DOMAIN_EVENT_SUSPENDED: self.__onDomainSuspended,
         libvirt.VIR_DOMAIN_EVENT_RESUMED: self.__onDomainResumed,
         libvirt.VIR_DOMAIN_EVENT_STOPPED: self.__onDomainStopped,
         libvirt.VIR_DOMAIN_EVENT_SHUTDOWN: self.__onDomainShutDown}
        eventHandler[eventID](domain)
        
    def __onDomainDefined(self, domain):
        """
        Handler para el evento de definición de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        pass    
    
    def __onDomainSuspended(self, domain):
        """
        Handler para el evento de suspensión de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        pass    
    
    def __onDomainResumed(self, domain):
        """
        Handler para el evento de reactivación de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        pass    
    
    def __onDomainUndefined(self, domain):
        """
        Handler para el evento de borrado de un dominio
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        pass    
   
    def __onDomainStopped(self, domain):
        """
        Handler para el evento de detención de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        self.__shutdownCallback.onDomainStop(domain.name())
        pass    
    
    def __onDomainShutDown(self, domain):
        """
        Handler para el evento de apagado de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        pass    
    
    def __onDomainStarted(self, domain):
        """
        Handler para el evento de arranque de un dominio.
        Argumentos:
            domain: el dominio asociado al evento
        Devuelve:
            Nada
        """
        xmlTree = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
        graphics_element = xmlTree.find('.//graphics')
        vnc_port = graphics_element.attrib['port']
        vnc_password = graphics_element.attrib['passwd']
        listen_element = graphics_element.find('.//listen')
        vnc_server_ip = listen_element.attrib['address']
        domainInfo = {"name" : domain.name(),
                      "VNCport" : int(vnc_port),
                      "VNCip" : vnc_server_ip,
                      "VNCpassword" : vnc_password}
        self.__startCallback.onDomainStart(domainInfo)    
    
    def startDomain(self, definitionFile):
        """
        Arranca un dominio
        Argumentos:
            definitionFile: el fichero .xml que define el dominio
        Devuelve:
            Nada
        Lanza:
            libvirtError: se lanza cuando surge algún problema al arrancar el dominio
        """
        self.__libvirtConnection.createXML(definitionFile, libvirt.VIR_DOMAIN_NONE)        
    
    def destroyAllDomains(self):
        """
        Destruye todos los dominios
        Argumentos:
            Ninguno
        Devuelve:
            Nada    
        """
        domainIDs = self.__libvirtConnection.listDomainsID()
        for domainID in domainIDs:
            domain = self.__libvirtConnection.lookupByID(domainID)
            domain.destroy()    
           
    def destroyDomain(self, domainName):
        """
        Destruye el dominio cuyo nombre se nos proporciona como argumento.
        Argumentos:
            domainName: el nombre del dominio a destruir
        Devuelve:
            Nada
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.destroy()
        
    def shutdownDomain(self, domainName):
        """
        Destruye el dominio cuyo nombre se nos proporciona como argumento.
        Argumentos:
            domainName: el nombre del dominio a destruir
        Devuelve:
            Nada
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.shutdown()
        
    def rebootDomain(self, domainName):
        """
        Destruye el dominio cuyo nombre se nos proporciona como argumento.
        Argumentos:
            domainName: el nombre del dominio a destruir
        Devuelve:
            Nada
        """             
        targetDomain = self.__libvirtConnection.lookupByName(domainName)
        targetDomain.reset(0) # Flags seguros. No se usan.  
            
    def getActiveDomainNames(self):
        """
        Permite consultar los nombres de los dominios activos.
        Argumentos:
            ninguno
        Devuelve:
            Una lista con los nombres de los dominios activos
        """
        domainIDs = self.__libvirtConnection.listDomainsID()
        result = []
        for domainID in domainIDs:
            domain = self.__libvirtConnection.lookupByID(domainID)
            xmlTree = ET.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
            domainName = xmlTree.find('.//name').text
            result.append(domainName)
        return result   
    
    def getNumberOfDomains(self):
        """
        Devuelve el número de dominios activos
        Argumentos:
            Ninguno
        Devuelve:
            El número de dominios activos
        """
        return self.__libvirtConnection.numOfDomains()
    
    def getStatusInfo(self):
        """
        Da información sobre los recursos usados por las máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve:
            Un diccionario con dos claves:
            - memory: El tamaño de la RAM de la máquina virtual (en KB)
            - #vcpus: Número total de cpus virtuales de las máquinas virtuales
        """
        idsMV = self.__libvirtConnection.listDomainsID()
        vcpus = 0
        for idVM in idsMV :
            domain = self.__libvirtConnection.lookupByID(idVM)
            info = domain.info()
            vcpus += info[3]
        return {"#domains" : self.__libvirtConnection.numOfDomains(),
                "#vcpus" : vcpus}    
    
    """
    Crea el hilo de procesamiento de eventos generados por libvirt
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def __startVirEventLoop(self):
        def runVirEventLoop():
            while True:
                libvirt.virEventRunDefaultImpl()
        libvirt.virEventRegisterDefaultImpl()
        self.__eventLoopThread = threading.Thread(target=runVirEventLoop, name="libvirt event loop")
        self.__eventLoopThread.setDaemon(True)
        self.__eventLoopThread.start()