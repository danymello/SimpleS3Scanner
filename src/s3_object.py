import botocore

class s3Obj:
    
    def __init__(self, name, bucket_name, size, last_modified, storage_class):
        
        self.name = name
        self.size = size
        self.last_modified = last_modified
        self.storage_class = storage_class
        self.bucket_name = bucket_name
        self.acl = []

    def getACL(self, client_s3):
        '''
        get ACL info and update the object
        '''
        
        try:
        
            response = client_s3.get_object_acl(Bucket=self.bucket_name, Key=self.name)
            
            for permission in response['Grants']:
                
                self.acl.append(permission['Permission'])
            
        except botocore.exceptions.ClientError as e:
                
                raise