
from src.utils import convert_unit, SIZE_UNIT
from tabulate import tabulate
from src.core import *

class Bucket:
    
    def __init__(self, name):
        
        self.name = name
        self.nb_objects = 0
        self.objects = []
        self.total_size_bytes = 0
        self.total_size_MB = 0
        self.bucket_policy = {}
        self.bucket_policy_status = False
        self.bucket_acl = []
        
    def computeTotalVolume(self):
        '''
        Compute the volume of data in this bucket
        Returned the volume in bytes
        '''
        
        #in bytes
        TOTAL_SIZE = 0
        
        for o in self.objects:
            
            TOTAL_SIZE += o.size
            
            
        self.total_size = TOTAL_SIZE  
        self.total_size_MB  = round(convert_unit(TOTAL_SIZE, SIZE_UNIT.MB),2)
        
        return TOTAL_SIZE
    
    @staticmethod
    def  displayBucketContent(bucket):
        '''
        Display content of a bucket
        '''
        
        table = []
        
        for o in bucket.objects:
            
            size_KB = round(convert_unit(o.size, SIZE_UNIT.KB),2)  
            
            object_ACL = ','.join(str(x) for x in o.acl)
            
            table.append([o.name, size_KB, o.acl, o.storage_class])
            
        print('\n')
        print(f'Listing content for bucket: { bucket.name}')
        print('\n')
        print(tabulate(table, headers=['Name', 'Size (MB)', 'ACL', 'Storage class']))
        print('\n')
        print(f'Number of objects: { bucket.nb_objects }')  
        print(f'Volume: { bucket.total_size_MB }')  
        ACL = ','.join(str(x) for x in bucket.bucket_acl)
        print(f'ACL: { ACL } ')
        print(f'Bucket Policy: { bucket.bucket_policy_status }')
        print('\n')
        
        
        
            
            
            
        
            
        
        
    
    