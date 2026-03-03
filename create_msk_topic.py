import boto3

# Replace with your Serverless MSK cluster ARN
cluster_arn = "arn:aws:kafka:us-east-1:248189941692:cluster/usgs-feed-msk/5660c33e-6d4e-41ab-a996-97b315e1c404-s3"
topic_name = "usgs-feed"

client = boto3.client("kafka", region_name="us-east-1")

response = client.create_topic(
    ClusterArn=cluster_arn,
    TopicName=topic_name,
    PartitionCount=1  # Serverless MSK manages replication automatically
)

print("Topic creation response:", response)