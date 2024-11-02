import boto3
from dotenv import load_dotenv
import os
load_dotenv()

client = boto3.client("bedrock", region_name="us-west-2", aws_access_key_id="ASIAYUGGS4MQOJ3HQLBC", aws_secret_access_key="huf6gqM+0sAOULWQ73gwGQMuiTWnD3eqNCElEwoc")

def invoke_bedrock_model(prompt):
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Remplacez par le modèle souhaité
        contentType="text/plain",
        accept="application/json",
        body=prompt.encode("utf-8")
    )
    result = response['body'].read().decode('utf-8')
    return result