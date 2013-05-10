from ccutils.threads import BasicThread
from clusterEndpoint.commands.commandsHandler import CommandsHandler

from time import sleep

class CommandMonitoringThread(BasicThread):
    def __init__(self, databaseConnector, commandTimeout, sleepTime):
        BasicThread.__init__(self, "Command monitoring thread")
        self.__dbConnector = databaseConnector
        self.__commandTimeout = commandTimeout
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            commandIDs = self.__dbConnector.removeOldCommands(self.__commandTimeout)
            (outputType, commandOutput) = CommandsHandler.createCommandTimeoutErrorOutput()
            for commandID in commandIDs :
                self.__dbConnector.addCommandOutput(commandID, outputType, commandOutput, True)
            sleep(self.__sleepTime)