import configparser
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max

mycredentials = configparser.ConfigParser()
mycredentials.read("/mnt/c/Users/lethi/.aws/credentials")

my_aws_access_key_id = mycredentials.get("default", "aws_access_key_id")
my_aws_secret_access_key = mycredentials.get("default", "aws_secret_access_key")

# create Spark session with S3 credentials
myspark = SparkSession.builder \
    .appName("spark-earthquake-s3") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.4.1,com.amazonaws:aws-java-sdk-bundle:1.12.762") \
    .config("spark.hadoop.fs.s3a.access.key", my_aws_access_key_id) \
    .config("spark.hadoop.fs.s3a.secret.key", my_aws_secret_access_key) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# read all earthquake JSON files directly from S3
mydf = myspark.read.json("s3a://bucket-nhx-main/project-usgs/staging/")

mydf.show(5)

# get the 2 latest earthquakes by event_time
latest_2 = mydf.orderBy(col("event_time").desc()).limit(2)

latest_2.show()

# find max magnitude among the 2 latest
max_magnitude = latest_2.agg(spark_max("magnitude").alias("max_magnitude"))

max_magnitude.show()

max_magnitude.write.mode("overwrite").parquet(
    "s3a://bucket-nhx-main/project-usgs/prod/max_magnitude/"
)

myspark.stop()
