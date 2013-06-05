#coding=utf-8

from ccutils.configurationFiles.configurationFileParser import ConfigurationFileParser

class VMServerConfigurationFileParser(ConfigurationFileParser):
    """
    Parser del fichero de configuración del repositorio
    """
    
    def __init__(self):
        """
        Inicializa el estado del parser
        Argumentos:
            Ninguno
        """
        ConfigurationFileParser.__init__(self)
        
    def _getExpectedSections(self):
        return ['Database configuration', 'Virtual Network Configuration', 'VNC server configuration', 
                'FTP Client Configuration', 'Paths']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'databaseUserName', 'databasePassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readBoolean('Virtual Network Configuration', 'createVirtualNetworkAsRoot')
        keys = ['vnName', 'gatewayIP', 'netMask', 'dhcpStartIP', 'dhcpEndIP']
        for key in keys:
            self._readString('Virtual Network Configuration', key)
            
        self._readString('VNC server configuration', 'vncNetworkInterface')
        self._readInt('VNC server configuration', 'listenningPort')
        self._readString('VNC server configuration', 'passwordLength')
        
        self._readInt('FTP Client Configuration', 'FTPTimeout')
        
        keys = ['certificatePath', 'configFilePath', 'sourceImagePath', 'executionImagePath', 'TransferDirectory']
        for key in keys:
            self._readString('Paths', key)