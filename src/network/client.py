'''
Created on Dec 29, 2012

@author: luis
'''

from twistedconnector import TwistedConnector
from time import sleep
from protocols import SimpleProtocol, SimpleProtocolFactory
import sys

if __name__ == '__main__':
    data = sys.argv[1]
    connector = TwistedConnector()    
    connector.start()
    factory = SimpleProtocolFactory('client')
    connector.createClient('127.0.0.1', 8080, 20, factory)
    while factory.getInstance() is None:
        sleep(1)
    factory.getInstance().sendData(data)    
    connector.stop()
    connector.join(100)
    print 'Done!'