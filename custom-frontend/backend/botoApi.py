import boto3
from dotenv import load_dotenv
import os
import json
load_dotenv()

client = boto3.client("bedrock", region_name="us-west-2", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

def invoke_bedrock_model(prompt):
    client = boto3.client("sagemaker-runtime", region_name="votre_region")

    payload = {
        "input_text": prompt
    }
    
    response = client.invoke_endpoint(
        EndpointName="votre_nom_de_point_d_acces_bedrock",
        ContentType="application/json",
        Body=json.dumps(payload)
    )

    result = json.loads(response['Body'].read().decode())
    return result["output_text"]