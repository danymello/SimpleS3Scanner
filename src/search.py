from src.core import *

class Search:
    
    def __init__(self, s3):
        
        
        self.s3 = s3
        self.name = ''
        self.search_phrase = ''
        self.results = []
        self.total_objects = 0
        self.total_volume = 0
        
    def searchbyName(self, search_string):
        '''
        search object which contain the search_string
        :param str search_string: String to search
        :return list: list of objects 
        '''
        
        results = []
        
        for b in self.s3.buckets:
            
            for o in b.objects:
                
                if search_string in o.name:
                    
                    results.append(o)
                    
                    
        self.total_volume = calculateVolumeObjects(results)
        self.results = results
        self.total_objects = len(results)
        
        
    def setName(self, name):
        '''
        set a name for the search 
        :param str name: name for the search
        '''
        
        
        self.name = name