import boto3
import time
import json
import os

print("--- [Minimal SQS Receiver Test] ---")

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/356206423360/MISO-Project-Proposals'
REGION_NAME = os.environ.get('AWS_REGION', 'us-east-1')

try:
    # Verify identity first
    sts_client = boto3.client('sts', region_name=REGION_NAME)
    identity = sts_client.get_caller_identity()
    print(f"Successfully authenticated as: {identity['Arn']}")
    
    sqs_client = boto3.client('sqs', region_name=REGION_NAME)
    print(f"Client created. Polling queue: {QUEUE_URL}")

    while True:
        print("\nAttempting to receive messages...")
        response = sqs_client.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10 # Use a shorter wait time for faster feedback
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            print("\n--- ? MESSAGE RECEIVED! ---")
            print(f"Message ID: {message['MessageId']}")
            print("Body:")
            print(json.dumps(json.loads(message['Body']), indent=2))
            print("--------------------------\n")
            print("Test successful. Exiting.")
            break
        else:
            print("...No messages in queue. Waiting...")

except KeyboardInterrupt:
    print("\nExiting.")
except Exception as e:
    print(f"\n? An error occurred: {e}")

