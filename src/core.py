import boto3
import botocore
import os
from src.utils import convert_unit, SIZE_UNIT

# version information
version = "0.1.0"

# color scheme for core
class bcolors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERL = '\033[4m'
    ENDC = '\033[0m'
    backBlack = '\033[40m'
    backRed = '\033[41m'
    backGreen = '\033[42m'
    backYellow = '\033[43m'
    backBlue = '\033[44m'
    backMagenta = '\033[45m'
    backCyan = '\033[46m'
    backWhite = '\033[47m'
    
# main status calls for print functions
def print_status(message):
    print((bcolors.GREEN) + (bcolors.BOLD) + \
        ("[*] ") + (bcolors.ENDC) + (str(message)))
    
def print_warning(message):
    print((bcolors.YELLOW) + (bcolors.BOLD) + \
        ("[!] ") + (bcolors.ENDC) + (str(message)))
    
def print_error(message):
    print((bcolors.RED) + (bcolors.BOLD) + \
        ("[!] ") + (bcolors.ENDC) + (bcolors.RED) + \
        (str(message)) + (bcolors.ENDC))
    
    
banner = bcolors.GREEN + r'''
  ████████   █████████ 
 ███░░░░███ ███░░░░░███
░░░    ░███░███    ░░░ 
   ██████░ ░░█████████ 
  ░░░░░░███ ░░░░░░░░███
 ███   ░███ ███    ░███
░░████████ ░░█████████ 
 ░░░░░░░░   ░░░░░░░░░  
                       
'''

banner += '''		 '''  + bcolors.backBlue + \
    ''' Version: %s''' % (version) + bcolors.ENDC + '\n'


banner += '''		 Written by: ''' + bcolors.BOLD + \
    '''fgu ''' + bcolors.ENDC + '\n'
    

def displayBanner():
    
    print(banner)
    
def displayOverview(s3):
          
    print(f'\n\nTotal number of buckets analyzed:{ bcolors.GREEN } { len(s3.buckets) }{ bcolors.ENDC }') 
    print(f'Total number of objects:  { bcolors.GREEN }{ s3.totalNbObjects }{ bcolors.ENDC }')
    print(f'Total volume of data:  { bcolors.GREEN }{ s3.totalVolume_MB } MB{ bcolors.ENDC }\n\n') 
        

def create_aws_client(profile, service):
    '''
    create client to specified AWS service.
    
    '''
    
    print(f'{ bcolors.BLUE }Connecting to service { service } with profile { profile }{ bcolors.ENDC }')
    session = boto3.session.Session(profile_name=profile)  
    client = session.client(service)
    
    if client is None:
        print_error('Could not connect to S3... Exiting')
        exit()
    
    
    return client 


def checkS3Permissions(client):
    '''
    check S3 permission for this profile
    '''
    
    list_calls = ['list_buckets','list_objects_v2','get_object','download_file','get_bucket_policy','get_bucket_acl','get_object_acl']
    
    print('\n')
    print_status('Check S3 permissions used by this tool\n') 
    for call in list_calls:
    
        try:
            getattr(client, call)
            print(f'=> { call }: { bcolors.RED }{ bcolors.GREEN } Worked!{ bcolors.ENDC }')
        except botocore.exceptions.ClientError:
            print(f'=> { call }: { bcolors.RED }{ bcolors.BOLD } Denied!{ bcolors.ENDC }')
    
    print('\n')
    print_status('Check S3 permission completed! Exiting')
    exit()
    
    
def selectWordlists():
    '''
    Show a lit of all wordlist available with an associated number.
    :return: the name of the file selected
    '''
    
    id = 0
    wordlists = []

    for file_ in os.listdir('./wordlists/'):
        
        wordlists.append(file_)
    
    
    print(f'\n{ bcolors.DARKCYAN }Choose the word list to use: { bcolors.ENDC }')
    
    for file_ in wordlists:
        
        print(f'[{ id }] - { file_ }')
        id += 1
        
    print('\n')
    selection = input(f'Enter your choice: ')
    while int(selection) not in range (1, id):
             
        selection = input('Wrong input, enter your choice again: ')
        
    return wordlists[int(selection)]
        
        
def calculateVolumeObjects(objects):
    '''
    Calculate total volume of object list in parameter
    :param list: list of S3 bject
    :return int: size in MB
    '''
    
    TOTAL_SIZE_OBJECT_LIST = 0
    
    for o in objects:
    
        TOTAL_SIZE_OBJECT_LIST += o.size
            
            
    TOTAL_SIZE_OBJECT_LIST_MB  = round(convert_unit(TOTAL_SIZE_OBJECT_LIST, SIZE_UNIT.MB),2)
    
    return TOTAL_SIZE_OBJECT_LIST_MB
        

def exit_3S():
    print_status("Exiting #S.. bye bye")
