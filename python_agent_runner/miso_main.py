# miso_main.py
import boto3
import json
import time
import os
from agents.genesis_agent import GenesisAgent

class MisoOrchestrator:
    """
    The main orchestrator for the MISO ecosystem.
    It polls the SQS queue for new project proposals and initiates the agent workflow.
    """
    def __init__(self):
        self.queue_name = 'MISO-Project-Proposals'
        self.sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        print("? MISO Orchestrator initializing...")
        try:
            # Dynamically get the queue URL instead of hardcoding it
            response = self.sqs_client.get_queue_url(QueueName=self.queue_name)
            self.queue_url = response['QueueUrl']
            print(f"?? Successfully found queue: {self.queue_url}")
        except Exception as e:
            print(f"FATAL: Could not find SQS queue '{self.queue_name}'. Please check the queue name and AWS permissions.")
            print(f"Error details: {e}")
            exit() # Exit if we can't find the queue

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

            genesis = GenesisAgent()
            genesis.create_codebase(proposal_data)

            print("? Processing complete.")
        except Exception as e:
            print(f"Error processing proposal: {e}")

if __name__ == '__main__':
    # Diagnostic code to verify AWS identity
    import boto3
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"--- [AWS DIAGNOSTIC] Running as: {identity['Arn']} ---")
    except Exception as e:
        print(f"--- [AWS DIAGNOSTIC] FAILED to get AWS identity: {e} ---")
    
    orchestrator = MisoOrchestrator()
    orchestrator.start_polling()
