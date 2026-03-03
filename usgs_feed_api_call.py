import requests, pandas as pd

# Grab data from USGS feed https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
def get_earthquake_data():
    myurl = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    myresponse = requests.get(myurl)
    if myresponse.status_code == 200:
        return myresponse.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    
earthquake_feed = get_earthquake_data()
#print(earthquake_feed['type'])
#print(earthquake_feed['metadata'])
#print(earthquake_feed['features'])
#print(earthquake_feed['bbox'])

earthquakes_list = earthquake_feed['features']
#print(earthquakes_list[0])  # Print the first earthquake entry to see its structure

#Nested JSON treatment
from pandas import json_normalize

earthquakes_df = json_normalize(earthquakes_list)
#print(earthquakes_df.columns)

#Only keep relevant columns
earthquakes_final_df = earthquakes_df[[
    'id', 'properties.time', 'properties.mag', 'properties.place', 'geometry.coordinates'
]].copy()
earthquakes_final_df.rename(columns={
    'id': 'earthquake_id',
    'properties.time': 'earthquake_time',
    'properties.mag': 'magnitude',
    'properties.place': 'place',
    'geometry.coordinates': 'coordinates'
}, inplace=True)
earthquakes_final_df[['longitude', 'latitude', 'depth']] = pd.DataFrame(earthquakes_final_df['coordinates'].tolist(), index=earthquakes_final_df.index)
earthquakes_final_df.drop(columns=['coordinates'], inplace=True)
print(earthquakes_final_df)

import boto3, sys
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb',
    region_name='us-east-1')
mydynamodb_table = dynamodb.Table('usgs_feed_pipeline_state')
myrecord = mydynamodb_table.get_item(Key={'pipeline_name': 'usgs_feed_all_hour'})['Item']
previous_last_processed_time_epoch = int(myrecord['last_processed_time'])
print(f"Previous last processed time (epoch) was: {previous_last_processed_time_epoch}")

new_earthquakes_df = earthquakes_final_df[earthquakes_final_df['earthquake_time'] > previous_last_processed_time_epoch]
if new_earthquakes_df.empty == True:
    print("No new earthquakes to process.")
    sys.exit(0)

from kafka import KafkaProducer
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
import boto3
import ssl

bootstrap_servers = 'boot-7w793zck.c3.kafka-serverless.us-east-1.amazonaws.com:9098'
topic_name = 'usgs-feed'

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    security_protocol='SASL_SSL',
    sasl_mechanism='AWS_MSK_IAM',
    sasl_plain_username='AWS_MSK_IAM',
    ssl_context=ssl.create_default_context()
)

#otherwise there is new data to process
new_last_processed_time_epoch = new_earthquakes_df['earthquake_time'].max()
for index, row in new_earthquakes_df.iterrows():
    myevent = row.to_dict()
    print(f"Processing earthquake {myevent}")

print(f"New last processed time (epoch) is: {new_last_processed_time_epoch}")
mydynamodb_table.update_item(
    Key={'pipeline_name': 'usgs_feed_all_hour'},
    UpdateExpression='SET last_processed_time = :new_time_val',
    ExpressionAttributeValues={':new_time_val': new_last_processed_time_epoch})
print("DynamoDB table updated with new last processed time.")

#MSK Bootstrap servers for IAM: boot-7w793zck.c3.kafka-serverless.us-east-1.amazonaws.com:9098