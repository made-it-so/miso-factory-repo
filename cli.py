import requests
import argparse
import os
import sys
import time

# --- Configuration ---
API_BASE_URL = 'http://127.0.0.1:8000'
# For simplicity, credentials are hardcoded. In production, use environment variables or a secure vault.
ADMIN_USERNAME = 'miso_admin'
ADMIN_PASSWORD = 'madeitso'

def get_auth_token():
    """Authenticates with the API and returns a JWT."""
    try:
        response = requests.post(
            f'{API_BASE_URL}/auth/token',
            data={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}
        )
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f'Error: Authentication failed. Is the MISO Core API running? Details: {e}', file=sys.stderr)
        sys.exit(1)

def create_genesis_job(token, prompt):
    """Submits a new job to the Genesis Pipeline via the API."""
    headers = {'Authorization': f'Bearer {token}'}
    payload = {'prompt': prompt}
    try:
        response = requests.post(f'{API_BASE_URL}/genesis/create', headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error: Could not create job. Details: {e}', file=sys.stderr)
        sys.exit(1)

def monitor_job(job_id):
    """Polls the API for job status until completion."""
    while True:
        try:
            response = requests.get(f'{API_BASE_URL}/genesis/status/{job_id}')
            response.raise_for_status()
            status_data = response.json()
            status = status_data.get('status', 'unknown')
            message = status_data.get('message', '')

            print(f'Job {job_id}: Status is {status}... {message}')

            if status in ['complete', 'not_found', 'error']:
                break
            
            time.sleep(5) # Wait 5 seconds before polling again
        except requests.exceptions.RequestException as e:
            print(f'Error: Could not get job status. Details: {e}', file=sys.stderr)
            break

def main():
    parser = argparse.ArgumentParser(description='MISO Command-Line Interface')
    parser.add_argument('prompt', type=str, help='The prompt for the Genesis Pipeline.')
    args = parser.parse_args()

    print('--- MISO CLI ---')
    print('1. Authenticating with Core API...')
    auth_token = get_auth_token()
    
    print('2. Submitting job to Genesis Pipeline...')
    job_info = create_genesis_job(auth_token, args.prompt)
    job_id = job_info['job_id']
    
    print(f'   -> Job created successfully with ID: {job_id}')
    
    print('3. Monitoring job progress...')
    monitor_job(job_id)
    
    print('--- MISO CLI Task Complete ---')

if __name__ == '__main__':
    main()
