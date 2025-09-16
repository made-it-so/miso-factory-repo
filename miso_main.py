import boto3
import json
import requests
import sys
import time

# --- Configuration ---
API_BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USERNAME = 'miso_admin'
ADMIN_PASSWORD = 'madeitso'
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/356206423360/MISO-Dev-Queue'

def get_auth_token():
    """Authenticates with the API to get a JWT."""
    try:
        response = requests.post(
            f'{API_BASE_URL}/auth/token',
            data={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}
        )
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f'SQS_WORKER_ERROR: Authentication failed. Is the API running? Details: {e}', file=sys.stderr)
        return None

def trigger_genesis_job(token, prompt):
    """Submits a new job to the Genesis Pipeline via the API."""
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'prompt': prompt}
    try:
        response = requests.post(f'{API_BASE_URL}/genesis/create', headers=headers, json=payload)
        response.raise_for_status()
        print(f'SQS_WORKER_INFO: Successfully triggered job for prompt: ""{prompt}""')
        print(f'   -> API returned job details: {response.json()}')
    except requests.exceptions.RequestException as e:
        print(f'SQS_WORKER_ERROR: Could not trigger job via API. Details: {e}', file=sys.stderr)

def main():
    """Main loop to poll SQS and trigger the MISO Core API."""
    sqs = boto3.client('sqs')
    print('--- MISO SQS Worker ---')
    print(f'Polling queue: {SQS_QUEUE_URL}')
    print('Waiting for messages...')

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                AttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            if 'Messages' in response:
                message = response['Messages'][0]
                receipt_handle = message['ReceiptHandle']
                
                try:
                    prompt = message['Body']
                    print(f'\nSQS_WORKER_INFO: Received message. Prompt: ""{prompt}""')
                    
                    auth_token = get_auth_token()
                    
                    if auth_token:
                        trigger_genesis_job(auth_token, prompt)
                    
                    sqs.delete_message(
                        QueueUrl=SQS_QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                    print('SQS_WORKER_INFO: Message processed and deleted from queue.')

                except Exception as e:
                    print(f'SQS_WORKER_ERROR: Error processing message. It will not be deleted. Details: {e}', file=sys.stderr)
            
        except Exception as e:
            print(f'SQS_WORKER_ERROR: An error occurred in the main loop: {e}', file=sys.stderr)
            time.sleep(10)

if __name__ == '__main__':
    main()
