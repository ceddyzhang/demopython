import configparser
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

mycredentials = configparser.ConfigParser()
mycredentials.read(os.path.expanduser("~/.aws/credentials"))

my_aws_access_key_id = mycredentials.get("default", "aws_access_key_id")
my_aws_secret_access_key = mycredentials.get("default", "aws_secret_access_key")

s3 = boto3.client(
    "s3",
    aws_access_key_id=my_aws_access_key_id,
    aws_secret_access_key=my_aws_secret_access_key
)

s3.head_bucket(Bucket="bucket-nhx-main")

myresponse = s3.list_objects_v2(
    Bucket="bucket-nhx-main",
    Prefix="project-usgs/staging/"
)

all_objects = myresponse.get("Contents", [])
##print(all_objects)
sorted_objects = sorted(all_objects, key=lambda obj: obj["LastModified"], reverse=True)


for obj in sorted_objects[:2]:
    print("File:", obj["Key"])
    print("LastModified:", obj["LastModified"])
    obj_file = s3.get_object(Bucket="bucket-nhx-main", Key=obj["Key"])
    obj_file_content = obj_file["Body"].read().decode("utf-8")
    print(obj_file_content)


