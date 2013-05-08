# -*- coding: utf8 -*-
'''
Lector para los ficheros de configuración

@author: Luis Barrios Hernández
@version: 1.0
'''
from invalidConfigurationFileException import InvalidConfigurationFileException

class ConfigurationFileReader(object):
    """
    Las instancias de esta clase leen ficheros de configuración
    """
    def __init__(self):
        """
        Inicializa el estado del lector
        Argumentos:
            Ninguno
           
        """        
        self.__parsedData = {}
        
    def parseConfigurationFile(self, configurationFilePath):
        """
        Lee el fichero de configuración
        Argumentos:
            configurationFilePath: la ruta del fichero de configuración
        Devuelve:
            Nada
        Lanza:
            InvalidConfigurationFileException: se lanza cuando 
             - el formato del fichero de configuración no coincide con el esperado.
        """
        try :
            self.__parsedData = {}
            
            f = open(configurationFilePath, "r")
            multilineString = False
            key, value = None, None
            
            for line in f :
                if (not (line.startswith("#") or len(line) == 0 or line == "\n")) :
                    if not (multilineString) :
                        [key, value] = line.split("=")
                        key = ConfigurationFileReader.__removeWhitespace(key)
                        
                        quotesCount = value.count('\"')
                        if (quotesCount == 1) :
                            multilineString = True
                        elif (quotesCount == 0):                            
                            value = ConfigurationFileReader.__removeWhitespace(value)
                        else :
                            raise Exception("Nested strings are not supported")
                        self.__parsedData[key] = value 
                    else :
                        value += line
                        quotesCount = line.count('\"')
                        if (quotesCount == 1) :
                            value = value.replace("\"", "")
                            value = ConfigurationFileReader.__removeWhitespace(value)                            
                            self.__parsedData[key] = value      
                            multilineString = False   
                        elif (quotesCount > 0) :
                            raise Exception("Nested strings are not supported")
            f.close()
            
        except Exception as e :
            self.__parsedData = {}
            raise InvalidConfigurationFileException(e.message)
        
    def getParsedData(self):
        """
        Devuelve los datos leídos del fichero de configuración
        Argumentos:
            Ninguno
        Devuelve:
            Un diccionario con los datos leídos del fichero de configuración
        """
        return self.__parsedData
    
    @staticmethod
    def __removeWhitespace(string):
        """
        Elimina los espacios en blanco de un string
        Argumentos:
            String: el string del que queremos eliminar los espacios en blanco
        Devuelve:
            Nada
        """
        return ' '.join(string.split())
    
if __name__ == "__main__" :
    reader = ConfigurationFileReader()
    try :
        reader.parseConfigurationFile("/home/luis/settings.conf")
    except Exception as e:
        print e
        
    print reader.getParsedData()
        