'''
Created on Dec 29, 2012

@author: luis
'''

from twistedconnector import TwistedConnector
from time import sleep
from protocols import SimpleProtocol, SimpleProtocolFactory

if __name__ == '__main__':
    connector = TwistedConnector()    
    connector.start()
    connector.createServer(8080, SimpleProtocolFactory('server'))
    sleep(1000)
    connector.stop()
    connector.join(100)
    print 'Done!'