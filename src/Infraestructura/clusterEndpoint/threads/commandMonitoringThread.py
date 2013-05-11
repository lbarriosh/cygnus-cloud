from ccutils.threads import BasicThread

from time import sleep

class CommandsMonitoringThread(BasicThread):
    def __init__(self, databaseConnector, commandTimeout, commandsHandler, sleepTime):
        BasicThread.__init__(self, "Command monitoring thread")
        self.__dbConnector = databaseConnector
        self.__commandTimeout = commandTimeout
        self.__commandsHandler = commandsHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            commandIDs = self.__dbConnector.removeOldCommands(self.__commandTimeout)
            if (len(commandIDs) != 0) :
                (outputType, commandOutput) = self.__commandsHandler.createCommandTimeoutErrorOutput()
                for commandID in commandIDs :
                    self.__dbConnector.addCommandOutput(commandID, outputType, commandOutput, True)
            sleep(self.__sleepTime)