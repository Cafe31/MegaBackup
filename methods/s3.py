# coding: utf-8
import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_aws(credentials, target_path, backup_path, backup_name):
    s3 = boto3.client('s3', aws_access_key_id=credentials['access_key'],
                      aws_secret_access_key=credentials['secret_key'])

    try:
        s3.upload_file(backup_path + backup_name, credentials['bucket'], target_path + backup_name)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
