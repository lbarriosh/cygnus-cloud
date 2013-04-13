#coding=utf-8

from repositoryServer.constans import RepositoryConstantsManager
from repositoryServer.repository import Repository
from database.utils.configuration import DBConfigurator
import sys

if __name__ == "__main__":
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        cm = RepositoryConstantsManager()
        cm.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
    configurator = DBConfigurator(cm.getConstant("mysqlRootsPassword"))
    configurator.runSQLScript(cm.getConstant("databaseName"), "../database/RepositoryDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(cm.getConstant("databaseUserName"), cm.getConstant("databasePassword"), cm.getConstant("databaseName"), True)
    
    repository = Repository(cm)
    repository.startListenning(cm.getConstant("certificatePath"),cm.getConstant("listenningPort"))
    