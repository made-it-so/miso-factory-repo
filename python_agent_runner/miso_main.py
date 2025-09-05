# miso_main.py
import boto3
import json
import time
import os
from agents.genesis_agent import GenesisAgent # Import the Genesis Agent

class MisoOrchestrator:
    """
    The main orchestrator for the MISO ecosystem.
    It polls the SQS queue for new project proposals and initiates the agent workflow.
    """
    def __init__(self):
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/356206423360/MISO-Project-Proposals'
        self.sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        print("? MISO Orchestrator initialized.")
        print(f"?? Listening for proposals on SQS queue: {self.queue_url}")

    def start_polling(self):
        """
        Starts the main infinite loop to poll for SQS messages.
        """
        while True:
            try:
                print("\nPolling for messages...")
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=20 
                )
                if 'Messages' in response:
                    message = response['Messages'][0]
                    receipt_handle = message['ReceiptHandle']
                    print(f"?? Message received. ID: {message['MessageId']}")
                    
                    self.process_proposal(message['Body'])

                    self.sqs_client.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=receipt_handle
                    )
                    print(f"??? Message deleted from queue.")
                else:
                    print("...No messages received. Waiting.")
            except KeyboardInterrupt:
                print("\n?? Shutting down Orchestrator.")
                break
            except Exception as e:
                print(f"?? An error occurred: {e}")
                time.sleep(10)

    def process_proposal(self, message_body: str):
        """
        Processes the proposal by invoking the Genesis Agent.
        """
        try:
            proposal_data = json.loads(message_body)
            print("\n--- PROCESSING PROPOSAL ---")
            print(f"  Project Name: {proposal_data.get('project_name')}")
            print(f"  Objective: {proposal_data.get('objective')}")
            print("---------------------------")
            
            # Invoke the Genesis Agent with the proposal data
            genesis = GenesisAgent()
            genesis.create_codebase(proposal_data)

            print("? Processing complete.")
        except Exception as e:
            print(f"Error processing proposal: {e}")

if __name__ == '__main__':
    orchestrator = MisoOrchestrator()
    orchestrator.start_polling()
