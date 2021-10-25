import boto3
import os
import botocore
import pandas as pd
import json
import pprint
from src.s3_bucket import Bucket
from src.s3_object import s3Obj
from src.search import Search
from src.utils import convert_unit, SIZE_UNIT
from src.cli import *
from src.config import *
from src.core import *
from tabulate import tabulate
from PyInquirer import prompt


class S3:
    
    def __init__(self, client):
        
        self.client = client
        self.buckets = []
        self.totalNbObjects = 0
        self.totalVolume_bytes = 0
        self.totalVolume_MB = 0
        self.searches = []
    
    
    def listBuckets(self):
        
        buckets = []
           
        response = self.client.list_buckets()
        for bucket in response['Buckets']:
                
            #bucket not whitelisted by default
            NOT_WHITELISTED = True
            bucket_name = bucket['Name']
                
            for whitelist_bucket in WHITELIST_BUCKETS:                   
                
                if whitelist_bucket in bucket_name:
                        
                    NOT_WHITELISTED = False                        
                    break
                
            if NOT_WHITELISTED ==  True:
                    
                #creating Bucket object and adding to the list of buckets
                bucket = Bucket(bucket['Name'])
                buckets.append(bucket)
                    
                try:
                    
                    self.getObjects(bucket)
                    self.getBucketPolicy(bucket)
                    self.getBucketACL(bucket)
                    
            
                except botocore.exceptions.ClientError as error:
                    if error.response['Error']['Code'] == "NoSuchBucket":  
                            print_error("Bucket does not exist.. skipping it..")
                            buckets.remove(bucket)
                            pass
                    else:
                        print(error.response)
                        pass
        
        self.buckets = buckets
        
    def getBucketPolicy(self, bucket):
        '''
        Get S3 bucket policy
        '''
        
        try:
        
            response = self.client.get_bucket_policy(Bucket=bucket.name)
            bucket.bucket_policy = response['Policy']
            bucket.bucket_policy_status = True
            #print(response['Policy'])
            
        except botocore.exceptions.ClientError as e:

            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                bucket.bucket_policy_status = False
            
            else:
                
                raise
    
    def getBucketACL(self, bucket):
        '''
        Get ACL associated with a bucket
        '''
        
        try:
        
            response = self.client.get_bucket_acl(Bucket=bucket.name)
            for permission in response['Grants']:
                bucket.bucket_acl.append(permission['Permission'])
            
        except botocore.exceptions.ClientError as e:
                
                raise

    
    def getObjects(self, bucket):
        
        print(f'Retrieving  objects for bucket: { bucket.name }')
        
        NB_OBJ_IN_BUCKET = 0
        
        response = self.client.list_objects_v2(Bucket=bucket.name, MaxKeys=MAX_KEYS) 
        
        if response.get('Contents'):
            
            #store the objects
        
            for obj in response['Contents']: 
                
                
                o = s3Obj(obj['Key'], bucket.name, obj['Size'], obj['LastModified'], obj['StorageClass'])
                
                
                if PER_OBJECT_ACL == True:
                
                    #getACL
                    o.getACL(self.client)
                
                #store the object info
                bucket.objects.append(o)
                
                NB_OBJ_IN_BUCKET += 1
                
        else:
            
            #set this bucket to empty
            
            bucket.nb_objects = 0
        
        #check if we got all the results
        
        if TEST_MODE is not True:
        
            while response['IsTruncated']:
                
                t = response['NextContinuationToken']
                
                #print(f'There is more in this bucket!! Next Token { t }')
                
                response = self.client.list_objects_v2(Bucket=bucket.name, MaxKeys=1000, ContinuationToken=response['NextContinuationToken'])
                
                #store the next round of objects
            
                for obj in response['Contents']: 
                    
                    #o= s3Obj(obj['Key'], size=obj['Size'], last_modified=obj['LastModified'], storage_class=obj['StorageClass'])
                    
                    o= s3Obj(obj['Key'], bucket.name, obj['Size'], obj['LastModified'], obj['StorageClass'])
                    #store the object info
                    bucket.objects.append(o)
                    
                    NB_OBJ_IN_BUCKET += 1
            
            
        #store the fetched set objects
        bucket.nb_objects = NB_OBJ_IN_BUCKET
        
    def generateStats(self):
        '''
        generate stats for each bucket and total
        '''
        
        TOTAL_VOLUME_bytes = 0
        TOTAL_NB_OBJECTS = 0
        
        for b in self.buckets:
            
            bucket_size = b.computeTotalVolume()
            
            TOTAL_VOLUME_bytes += bucket_size
            TOTAL_NB_OBJECTS += b.nb_objects
            
        self.totalVolume_bytes = TOTAL_VOLUME_bytes
        self.totalVolume_MB  = round(convert_unit(TOTAL_VOLUME_bytes,SIZE_UNIT.MB),2)
        self.totalNbObjects = TOTAL_NB_OBJECTS
        
    @staticmethod
    def printResults(list_objects, volume=None):
        '''
        print a list of object
        :param list list_objects: List of objects to print on the screen
        :param int volume: Size of all objects
        '''
        
        if len(list_objects) == 0:
            
            print_warning('No match')
            return
             
           
        table_result = []
        
        for obj in list_objects:
            
            table_result.append([obj.name, obj.bucket_name, obj.size, obj.storage_class])
        
        print(f'\n{ bcolors.DARKCYAN }Interesting Objects found:{ bcolors.ENDC }\n')             
        print(tabulate(table_result, headers=["Object", "Bucket Name", "size","Storage Class"]))
        print(f'\n')
        print(f'{ bcolors.DARKCYAN }Number of results:{ bcolors.ENDC } {len(list_objects)}')
        if volume is not None:
            print(f'{ bcolors.DARKCYAN }Volume:{ bcolors.ENDC } { volume }') 
        print(f'\n')
        
        
        
        
    def searchloot(self):
        '''
        Search for loot based on keywords in wordlists/
        '''
        
        wordlist = 'wordlists/'+selectWordlists()
        
        file = open(wordlist, "r")
        
        keywords = []
        interresting_objects = []
       
        for word in file:
            
            keywords.append(word.strip())
            
        # print('keywords of interest:')
        # for k in keywords:    
        #     print(k)
           
        for bucket in self.buckets:
        
            #print(f'Analyzing { bucket.nb_objects } objects within bucket { bucket.name }')
            for o in bucket.objects:
                
                for k in keywords:
                
                    if k in o.name :
                        
                        interresting_objects.append(o)
                
               
        self.printResults(interresting_objects) 
           
        # table_result = []
        
        # for obj in interresting_objects:
            
        #     table_result.append([obj.name, obj.bucket_name, obj.size, obj.storage_class])
        
        # print(f'\n{ bcolors.DARKCYAN }Interesting Objects found:{ bcolors.ENDC }\n')             
        # print(tabulate(table_result, headers=["Object", "Bucket Name", "size","Storage Class"]))
        # print(f'\n')
        
        #return list of matching objects
        return  interresting_objects
    
    
    def downloadBucket(self, bucket, directory):
        '''
        Download the entire bucket
        '''
        
        print('\n')
        print_warning('Exfiltrating l00ts!')
        print('\n')
        
        for o in bucket.objects:
            
            try:   
                
                name = o.name.replace('/','_')    
                path_download = directory + name
                response = self.client.download_file(Bucket=o.bucket_name, Key=o.name, Filename=path_download)
                     
                print(f'=> { o.name } in { o.bucket_name } { bcolors.GREEN }{ bcolors.BOLD }downloaded!{ bcolors.ENDC }')
                
            except botocore.exceptions.ClientError as e:
                
                if e.response['Error']['Code'] == "404":
                    
                    print_error("The object does not exist.")
                    
                elif e.response['Error']['Code'] == "403":
                    print(f'=> { o.name } in { o.bucket_name } { bcolors.RED }{ bcolors.BOLD }Access DENIED!{ bcolors.ENDC }')
            
                else:
                
                    raise
       
        print('\n')
        print_status('Download completed!')
        menu_back(self)
        
    def downloadObject(self, object, directory):
        '''
        Download a single object
        :param s3Obj object: object to be downloaded
        :param str directory: the diretcory name where the object would be downloaded
        '''
        
        print('\n')
        print_warning('Exfiltrating l00ts!')
        print('\n')
        
            
        try:   
                
            name = object.name.replace('/','_')
            new_dir_bucket = directory+object.bucket_name+'/'
            #create dir
            if os.path.isdir(new_dir_bucket) == False:
                os.mkdir(new_dir_bucket)
                
            path_download = new_dir_bucket + name
            response = self.client.download_file(Bucket=object.bucket_name, Key=object.name, Filename=path_download)
                    
            print(f'=> { o.name } in { o.bucket_name } { bcolors.GREEN }{ bcolors.BOLD }downloaded!{ bcolors.ENDC }')
                
        except botocore.exceptions.ClientError as e:
                
            if e.response['Error']['Code'] == "404":
                
                print_error("The object does not exist.")
                
            elif e.response['Error']['Code'] == "403":
                
                print(f'=> { o.name } in { o.bucket_name } { bcolors.RED }{ bcolors.BOLD }Access DENIED!{ bcolors.ENDC }')
            
            else:
                
                raise
       
        print('\n')
        print_status('Download completed!')
        menu_back(self)
        

            
    def downloadObjects(self, listOfObjects, directory):
        '''
        Download objects in the list
        :param list listOfObjects: list of S3 object to be downloaded
        :param str directory: the diretcory name where objects would be downloaded
        '''
        
        for o in listOfObjects: 
            
            try:   
                
                name = o.name.replace('/','_')
                new_dir_bucket = directory+o.bucket_name+'/'
                #create dir
                if os.path.isdir(new_dir_bucket) == False:
                    os.mkdir(new_dir_bucket)
                
                path_download = new_dir_bucket + name
                response = self.client.download_file(Bucket=o.bucket_name, Key=o.name, Filename=path_download)
                 
                print(f'=> { o.name } in { o.bucket_name } { bcolors.GREEN }{ bcolors.BOLD }downloaded!{ bcolors.ENDC }')
                
            except botocore.exceptions.ClientError as e:
                
                if e.response['Error']['Code'] == "404":
                    
                    print("The object does not exist.")
                    
                elif e.response['Error']['Code'] == "403":
                
                    print(f'=> { o.name } in { o.bucket_name } { bcolors.RED }{ bcolors.BOLD }Access DENIED!{ bcolors.ENDC }')
            
                else:
                
                    raise
       
        print('\n')
        print_status('Download completed!')
        menu_back(self)
        
    
    def downloadAll(self):
        '''
        Download all buckets
        '''
        
        print(f'\nNumber of objects to be downloaded: { len(self.totalNbObjects) }')
        print(f'Total size in MB: { self.total_size_MB }\n')
                    
        user_prompt2 = prompt(CONFIRM_DOWNLOAD)
        action_confirmation = user_prompt2['CONFIRM_DOWNLOAD']
                
        if action_confirmation == True:
                
                
            folder = input('Enter the name of the folder where objects would be downloaded: ')
                    
            download_folder = os.getcwd()+'/downloads/'+folder+'/'
                
            while os.path.isdir(download_folder) == True:
                    
                print_error('This folder already exist. Choose a different name!')
                folder = input('Enter a new folder name: ') 
                download_folder = os.getcwd()+'/downloads/'+folder+'/'
                
                
                full_path_download_folder = os.getcwd()+'/downloads/'+folder
                os.mkdir(full_path_download_folder)
                
                print_warning('\nExfiltrating l00ts!\n')
                    
                for b in self.buckets:   
                    
                    s3.downloadObjects(b.objects, download_folder)
                 
        
    def bucketExists(self, name):
        '''
        Check if a bucket exist and return True if is does.
        '''
        
        for b in self.buckets:
        
            if b.name == name:
            
                return True
                
        return False
    
    def objectExists(self, bucket, name):
        '''
        check if an object exist within a bucket
        '''
        
        for o in bucket.objects:
            
            if o.name == name:
                
                return True
            
        return False
    
    def findObject(self, bucket, name):
        '''
        Search for an object within in bucket and return it
        '''
        
        for o in bucket.objects:
            
            if o.name == name:
                
                return o
           
           
    def searchBucketbyName(self, name):
        '''
        Search for a specific bucket and return the bucket object
        '''
        
        for b in self.buckets:
        
            if b.name == name:
            
                return b
                
        print_error(f'\nbucket { name } not found')
  
           
    def showBucketPolicies(self):
        '''
        Show Bucket policy for each bucket which has one
        '''
        
        for b in self.buckets:
            
            if b.bucket_policy_status == True:
                
                print(f'\n{ bcolors.DARKCYAN }S3 Bucket Policy for{ bcolors.ENDC } { bcolors.BOLD }{ b.name }{ bcolors.ENDC }\n')
                policy_json = json.loads(b.bucket_policy)
                print(json.dumps(policy_json, indent=4))
                
        print(f'\n{ bcolors.DARKCYAN }done.{ bcolors.ENDC }\n')
        
    def DisplaySummary(self):
        '''
        display Summary of S3
        '''
        
        table = []
        
        for b in self.buckets:        
            
            table.append([b.name, b.nb_objects, b.total_size_MB, b.bucket_policy_status, ','.join(str(x) for x in b.bucket_acl)])
            
        print('\n')
        print(tabulate(table, headers=['Bucket', 'object count', 'Total volume (MB)', 'Bucket Policy', 'Bucket ACL']))
        print('\n')  
        menu_back(self)
        
        
    def display(self):
        for attribute, value in self.__dict__.items():
            print(attribute, '=', value)
        
        
        
    def search(self, search_string):
        '''
        search a string
        :param str search_string: string to search
        :resturn Search: resturn search object
        '''
        
        s = Search(self)
        s.searchbyName(search_string)
        self.printResults(s.results,volume=s.total_volume)
        self.searches.append(s)
        
        return s
        
        
        
        
        

    
    
    
    