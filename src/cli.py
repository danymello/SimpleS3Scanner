from PyInquirer import prompt
from src.core import *
from src.cli import *
from PyInquirer import prompt


MAIN_MENU = [ {
    'type': 'list',
    'name': 'MAIN_MENU',
    'message': 'SSS Main Menu',
    'choices': ['S3 Summary','List objects in a bucket','search for l00t','Free Search', 'Download All','Bucket Policies','Quit']
    }]   

DOWNLOAD_MENU = [ {
    'type': 'list',
    'name': 'DOWNLOAD_MENU',
    'message': 'What do you want to do?',
    #'choices': ['Download objects','Save the results','back']
    'choices': ['Download objects','Save the results','back']
    }]

confirm = [
    {
        'type': 'confirm',
        'message': 'Do you want to continue?',
        'name': 'continue',
        'default': True,
    }
]

CONFIRM_DOWNLOAD = [
    {
        'type': 'confirm',
        'message': 'Do you really want to donwload those objects?',
        'name': 'CONFIRM_DOWNLOAD',
        'default': True,
    }
]

MENU_BACK = [
    {
        'type': 'list',
        'message': 'What is next?',
        'name': 'MENU_BACK',
        'choices': ['Back to main menu']
    }
]

MENU_DOWNLOAD_BUCKET_OR_OBJECT = [
    {
        'type': 'list',
        'message': 'What is next?',
        'name': 'MENU_DOWNLOAD_BUCKET_OR_OBJECT',
        'choices': ['Download the entire bucket','Download an object','Back to main menu']
    }
]

MENU_DOWNLOAD_BUCKET = [
    {
        'type': 'list',
        'message': 'What is next?',
        'name': 'MENU_DOWNLOAD_BUCKET',
        'choices': ['Download the entire bucket','Back to main menu']
    }
]
  


def main_menu(s3):
    
    while True:       
        
        answers = prompt(MAIN_MENU)
        action = answers['MAIN_MENU']
            
        if action == 'S3 Summary':
            
            s3.DisplaySummary()
            
        elif action == 'List objects in a bucket':
            
            print('\n')
            target_bucket = input(f'Enter the bucket name: ')
            
            while s3.bucketExists(target_bucket) == False:
                
                print('\n')
                print_error('This bucket does not exist. Enter a valid bucket name!')
                target_bucket = input(f'Enter the bucket name: ')
                
            bucket_obj = s3.searchBucketbyName(target_bucket)
            bucket_obj.displayBucketContent(bucket_obj)
            
            menu_list_bucket(s3, bucket_obj)
            
        elif action == 'search for l00t':
            
            objects = s3.searchloot()
            download_prompt(s3, objects)
            
            
        elif action == 'Free Search':
            
            print('\n')
            search_string = ''
            
            while True:
                
                search_string = input(f'Search > ')
                
                if search_string == '!action' or search_string == 'exit':
                    download_prompt(s3, s.results)
                    break
                
                elif search_string == '':
                        continue
                
                else:               
                    
                    s = s3.search(search_string)
            
        
        elif action == 'Download All':
            
            s3.downloadAll()
            
        elif action == 'Bucket Policies':
            
            s3.showBucketPolicies()           
            
        elif action == "Quit":
            
            print("Bye Bye")
            exit()
            
        else:
            
            print(f"Action: { action } invalid")  



def download_prompt(s3, objects):
    
    user_prompt1 = prompt(DOWNLOAD_MENU)
    action = user_prompt1['DOWNLOAD_MENU']
    
    
    if action == "Download objects":
        
        total_size = calculateVolumeObjects(objects)
        print(f'\nNumber of objects to be downloaded: { len(objects) }')
        print(f'\nTotal size in MB: { total_size }\n')
                  
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
                
            #download objects
            s3.downloadObjects(objects, download_folder)
                
        else:
                
            main_menu(s3)
                                     
    elif action == "Save the results":
        
        #to do
        main_menu(s3)
    
    elif action == "back":
            
            main_menu(s3)
          
    else:
            
        print(f'Action: { action } invalid')
        
def menu_back(s3):
    
    user_prompt1 = prompt(MENU_BACK)
    action = user_prompt1['MENU_BACK']
    
    if action == 'Back to main menu':
        
        main_menu(s3)
        
    else:
            
        print(f'Action: { action } invalid')
        
        
def menu_list_bucket(s3, bucket):
    
    user_prompt1 = prompt(MENU_DOWNLOAD_BUCKET_OR_OBJECT)
    action = user_prompt1['MENU_DOWNLOAD_BUCKET_OR_OBJECT']
    
    if action == 'Download the entire bucket':
            
        download_folder = os.getcwd()+'/downloads/'+bucket.name+'/'    
        if os.path.isdir(download_folder) == True:
                
            print_error('This folder already exist! This bucket must have been already downloaded')
            return

        else:
                
            os.mkdir(download_folder)
                
        #download objects
        s3.downloadBucket(bucket, download_folder)
        
        
        
    elif action == 'Download an object':
        
                 
        download_folder = os.getcwd()+'/downloads/'
        
        print('\n')
        obj_name = input(f'Enter the object name: ')
            
        while s3.objectExists(bucket, obj_name) == False:
                
            print('\n')
            print_error('This object does not exist within this bucket. Enter a valid object name!')
            obj_name = input(f'Enter the object name: ')
                
        #download object
        obj = s3.findObject(bucket, obj_name)
        print(f'Object would be saved in Downloads folder')
        s3.downloadObject(obj, download_folder)
        
    elif action == 'Back to main menu':
        
        main_menu(s3)
        
    else:
            
        print(f'Action: { action } invalid')
    
    
    