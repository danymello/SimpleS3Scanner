from src.core import *

class saveResults:
    
    def __init__(self, results):
        
        #results is a list of objects from a search
        self.results = results
        self.downloaded = False
        
        
    def setDowloadStatus(status):
        
        if status == True:
            self.downloaded =  True
        elif status == False:
            self.downloaded =  False
        else:
            print_error("Invalid status")