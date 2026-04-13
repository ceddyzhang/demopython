
from pyspark.sql import SparkSession

# create Spark session
myspark = SparkSession.builder \
    .appName("spark-local-test") \
    .getOrCreate()

# sample dataset
data = [
    ("quake1", 5),
    ("quake2", 3),
    ("quake3", 6)
]

# create Spark dataframe
df = myspark.createDataFrame(data, ["earthquake_id", "magnitude"])

# show result
df.show()

# stop Spark
myspark.stop()

import configparser
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

mycredentials = configparser.ConfigParser()
#for windows
#mycredentials.read(os.path.expanduser("~/.aws/credentials"))
#for WSL Linux
mycredentials.read("/mnt/c/Users/lethi/.aws/credentials")

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
    Prefix="project-usgs/staging/",
    MaxKeys=5
)

for obj in myresponse.get("Contents", []):
    print(obj["Key"])

