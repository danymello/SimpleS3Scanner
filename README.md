# SimpleS3Scanner (aka 3S)

## Introduction

3S is a tool to enumerate and find l00ts within S3 service. There is so many tools out there already available for S3.. so why this one? Most of them are focused on finding publicly availble S3 buckets by using brute force. In the context of an authenticated session where credenttials with full or patial access to S3 have been stolen, not much tool exists to enumerate S3 buckets and help to find some interesting stuffs to exfiltrate. The is what 3S is about.

## Installation

Use your favorite virtual environement application and install python's dependancies:

`
pip install -r requirements.txt
`

The app has been developped with python 3.8.x

## Usage

```
(fguillot) fguillot@ubuntu:~/aws/SimpleS3Scanner$ python sss.py -h
usage: sss.py [-h] -p PROFILE [-c] [-v]

A set of tools for S3

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Specificy the profile to use from ~/.aws/credentials
  -c, --check           Brute Force some S3 permissions to check if
                        credentails have access to it
  -v, --debug           Print debug information to the screen.
``` 

### AWS Permissions

S3 does not require any IAM permissions. It requires those following permissions for S3:

- list_buckets
- list_objects_v2
- get_object
- get_bucket_policy
- get_bucket_acl
- get_object_acl

The tool can validate what permissions your AWS credentials have access to from the above list.

### Features

- Enumerate all buckets and all objects
- Retreive S3 Bucket Policies
- Search for l00ts based on wordlists (predefined or add your own)
- Simple Free search (search keyword interactively)
- Exfiltrate (from wordlists or searches)
- Exfiltrate everything possible

### demo

[![asciicast](https://asciinema.org/a/v8ev8AnGK2vUbt6FrD80rpXUy.svg)](https://asciinema.org/a/v8ev8AnGK2vUbt6FrD80rpXUy)

### Roadmap

- [ ] Saved results of searches to do all the exfiltration at once.
- [ ] Document config file in README.