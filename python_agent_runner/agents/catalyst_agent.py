# agents/catalyst_agent.py
import boto3
import json
import os

class CatalystAgent:
    """
    The Catalyst Agent is the entry point for all new user-defined projects.
    It takes a raw proposal, validates it, and places it onto the SQS queue
    for the MISO Orchestrator.
    """
    def __init__(self):
        # SQS Queue URL is now hardcoded
        self.queue_url = 'https://sqs.us-east-1.amazonaws.com/356206423360/MISO-Project-Proposals'
        
        # For local dev, Boto3 will use your configured AWS CLI credentials.
        # In ECS, it will automatically use the task's IAM role.
        self.sqs_client = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        print("Catalyst Agent initialized and connected to SQS.")

    def initiate_proposal(self, proposal_data: dict):
        """
        Sends the project proposal to the SQS queue.

        Args:
            proposal_data (dict): A dictionary containing the project details.
        """
        if not self.queue_url or 'PASTE_YOUR' in self.queue_url:
            print("ERROR: SQS Queue URL is not configured in CatalystAgent.")
            return False

        try:
            print(f"Sending proposal '{proposal_data.get('project_name')}' to SQS queue...")
            
            # Convert the proposal dictionary to a JSON string for the message body
            message_body = json.dumps(proposal_data)

            # Send the message to the SQS queue
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body
            )

            print(f"Message sent successfully. Message ID: {response['MessageId']}")
            return True
        except Exception as e:
            print(f"ERROR sending message to SQS: {e}")
            return False
