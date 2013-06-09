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
                'FTP Client Configuration', 'Network configuration', 'Paths']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'databaseUserName', 'databasePassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readBoolean('Virtual Network Configuration', 'createVirtualNetworkAsRoot')
        keys = ['vnName', 'gatewayIP', 'netMask', 'dhcpStartIP', 'dhcpEndIP']
        for key in keys:
            self._readString('Virtual Network Configuration', key)
            
        self._readString('VNC server configuration', 'vncNetworkInterface')
        self._readString('VNC server configuration', 'passwordLength')
        
        self._readBoolean('Network configuration', 'useSSL')
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'listenningPort')
        
        keys = ['FTPTimeout', 'MaxTransferAttempts']
        for key in keys:
            self._readInt('FTP Client Configuration', key)
        
        keys = ['configFilePath', 'sourceImagePath', 'executionImagePath', 'TransferDirectory']
        for key in keys:
            self._readString('Paths', key)