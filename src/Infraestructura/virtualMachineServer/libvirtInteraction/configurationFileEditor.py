# -*- coding: utf8 -*-
'''
Editor de ficheros de configuración
@author: Luis Barrios Hernández
@version: 3.0
'''

try :
    import etree.cElementTree as ET
except ImportError:
    try :
        import xml.etree.cElementTree as ET
    except ImportError:
        try :
            import etree.ElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET
            
class ConfigurationFileEditorException(Exception):
    """
    Clase de excepción utilizada por el editor de ficheros de configuración
    """
    pass
    
class ConfigurationFileEditor(object):
    """
    Clase del editor de ficheros de configuración
    """
    def __init__(self, inputFilePath):
        """
        Inicializa el estado del editor de ficheros de configuración
        Argumentos:
            inputFilePath: ruta del fichero .xml cuyo contenido vamos a modificar
        """
        self.__inputFilePath = inputFilePath
        self.__name = None
        self.__uuid = None
        self.__virtualNetworkName = None
        self.__macAddress = None
        self.__vncServerIPAddress = None
        self.__vncServerPort = None
        self.__vncServerPassword = None
        self.__dataImagePath = None
        self.__osImagePath = None
        
    def setDomainIdentifiers(self, name, uuid):
        """
        Define los nuevos identificadores únicos del dominio que se van a utilizar.
        Argumentos:
            name: el nombre del dominio
            uuid: el UUID del dominio
        Devuelve:
            Nada
        """
        self.__name = name
        self.__uuid = uuid
        
    def setVirtualNetworkConfiguration(self, virtualNetwork, macAddress):
        """
        Define los parámetros de conexión a la red virtual.
        Argumentos:
            name: el nombre de la red virtual
            macAddress: la MAC del dominio
        Devuelve:
            Nada
        """
        self.__virtualNetworkName = virtualNetwork
        self.__macAddress = macAddress
        
    def setVNCServerConfiguration(self, ipAddress, port, password):
        """
        Define los parámetros de configuración del servidor VNC
        Argumentos:
            ip_address: la dirección IP del servidor VNC
            port: el puerto de escucha del servidor VNC
            password: la contraseña del servidor VNC
        """
        self.__vncServerIPAddress = ipAddress
        self.__vncServerPort = port
        self.__vncServerPassword = password
        
    def setImagePaths(self, osImagePath, dataImagePath):
        """
        Define las rutas de las imágenes del SO y de datos y paginación.
        Argumentos:
            osImagePath: la ruta de la imagen del SO
            dataImagePath: la ruta de la imagen que contiene los datos del usuario
            y el fichero de paginación.
        Devuelve:
            Nada
        """
        self.__osImagePath = osImagePath
        self.__dataImagePath = dataImagePath
        
    def generateConfigurationString(self):
        """
        Genera, a partir del fichero inicial, un string con el contenido del nuevo
        fichero de configuración.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        Lanza:
            ConfigurationFileEditorException: se lanza cuando no se han definido
            todos los parámetros de configuración del dominio.
        """
        self.__checkErrors()
        # Tenemos todo => procedemos
        # Parseamos el fichero base
        tree = ET.parse(self.__inputFilePath)
        root = tree.getroot()
        # Escribimos en él los valores de los parámetros de configuración que nos han pasado
        name = root.find("name")
        name.text = self.__name

        uuid = root.find("uuid")
        uuid.text = self.__uuid

        devices = root.find("devices")
        interface = devices.find("interface")
        mac = interface.find("mac")
        mac.set("address", self.__macAddress)
        source = interface.find("source")
        source.set("network", self.__virtualNetworkName)
        
        for disk in devices.iter("disk") :
            target = disk.find("target")
            source = disk.find("source")
            if (target.get("dev") == "vda") :
                # primer disco. Es el del SO
                source.set("file", self.__osImagePath)
            else :
                # Segundo disco. Es el de la partición de datos y paginación
                source.set("file", self.__dataImagePath)
        
        graphics = devices.find("graphics")
        graphics.set("port", str(self.__vncServerPort))
        graphics.set("websocket", str(self.__vncServerPort + 1))
        graphics.set("passwd", self.__vncServerPassword)
        listen = graphics.find("listen")
        listen.set("address", self.__vncServerIPAddress)
        
        # Generar el string y devolverlo
        return ET.tostring(root)
    
    def __checkErrors(self):
        """
        Comprueba que todos los parámetros de configuración del dominio han sido definidos.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        Lanza:
            ConfigurationFileEditorException: esta excepción se lanza cuando algún parámetro de 
            configuración del dominio no ha sido definido.
        """
        if (self.__name == None or self.__uuid == None) :
            raise ConfigurationFileEditorException("The domain identifiers have not been set")
        if (self.__virtualNetworkName == None or self.__macAddress == None) :
            raise ConfigurationFileEditorException("The network configuration parameters have not been set")
        if (self.__vncServerIPAddress == None or self.__vncServerPassword == None or self.__vncServerPort == None) :
            raise ConfigurationFileEditorException("The VNC server configuration parameters have not been set")
        if (self.__dataImagePath == None or self.__osImagePath == None) :
            raise ConfigurationFileEditorException("The data image path has not been set")    