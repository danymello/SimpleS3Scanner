import logging
import argparse
from src.core import *
from src.s3 import S3
from src.cli import *
from PyInquirer import prompt


__version__    = "0.1."
__date__       = "09.22.2021"
__author__     = "Fabien Guillot"
__email__      = "fguillot@vectra.ai"
__description__= "Simple S3 Scanner aka 3S"



def main(args):
    
    displayBanner()
    client = create_aws_client(args.profile,'s3')
    s3 = S3(client)
    s3.listBuckets()
    s3.generateStats()
    displayOverview(s3)
    
    #go to main menu
    main_menu(s3)

if __name__ == '__main__':
    
    
    parser = argparse.ArgumentParser(description='A set of tools for S3')
    parser.add_argument('-p', '--profile', dest = "profile", action = "store", required = True, help='Specificy the profile to use from ~/.aws/credentials')
    parser.add_argument('-c', '--check', dest = "check", action = "store_true", default = False, help='Brute Force some S3 permissions to check if credentails have access to it')
    parser.add_argument("-v", "--debug", dest="debug", action  = "store_true", default = False, help    = "Print debug information to the screen.")
     
        
    try:

        args = parser.parse_args()
        
        if args.check:
            
            displayBanner()
            client = create_aws_client(args.profile,'s3')
            
            checkS3Permissions(client)
    
        
        main(args)
        
    except Exception as e:
        logging.exception("Exception: {0!s}".format(e))
        exit(1)
  
    