'''
Created on May 11, 2013

@author: luis
'''
class CodesTranslator(object):
    def processVMServerSegment(self, data):
        raise NotImplementedError
    
    def processVMDistributionSegment(self, data):
        raise NotImplementedError
    
    def translateRepositoryStatusCode(self, code):
        raise NotImplementedError
    
    def translateErrorDescriptionCode(self, code):
        raise NotImplementedError
    
    def translateNotificationCode(self, code):
        raise NotImplementedError