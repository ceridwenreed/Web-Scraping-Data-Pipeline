#%%
'''
This file contains the data storage credentials to connect to
AWS s3 bucket and RDS inside the web scraper.

'''

import boto3
from sqlalchemy import create_engine
from secrets import(access_key_id,
                    secret_access_key,
                    region, 
                    database_type,
                    dbapi,
                    endpoint,
                    user,
                    password,
                    database,
                    port)


#connect to s3 bucket
s3_client = boto3.client('s3', 
                        aws_access_key_id=access_key_id, 
                        aws_secret_access_key=secret_access_key, 
                        region_name=region)


DATABASE_TYPE = database_type
DBAPI = dbapi
ENDPOINT = endpoint
USER = user
PASSWORD = password
DATABASE = database
PORT = port

# connect to RDS
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}").connect() 


#%%