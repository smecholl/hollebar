import os
import base64
import requests

def list_files_in_folder(repo_owner, repo_name, folder_path, token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}?ref=test-branch'
    print(f"Listing files in folder URL: {url}")
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.json()}")
        return None

def delete_file_from_github(repo_owner, repo_name, file_path, sha, branch_name, token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    print(f"Deleting file URL: {url}")
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'message': f'Delete {file_path}',
        'branch': branch_name,
        'sha': sha
    }
    response = requests.delete(url, headers=headers, json=data)
    print(f"Delete response status code: {response.status_code}")
    print(f"Delete response: {response.json()}")
    if response.status_code == 200:
        print(f"Deleted {file_path} successfully.")
    else:
        print(f"Error: {response.json()}")

def upload_file_to_github(repo_owner, repo_name, file_path, content, branch_name, token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    print(f"Uploading file URL: {url}")
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'message': f'Upload {file_path}',
        'branch': branch_name,
        'content': content
    }
    response = requests.put(url, headers=headers, json=data)
    print(f"Upload response status code: {response.status_code}")
    print(f"Upload response: {response.json()}")
    if response.status_code == 201:
        print(f"Uploaded {file_path} successfully.")
    else:
        print(f"Error: {response.json()}")

def find_most_recent_csv(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    print(f"CSV files found: {csv_files}")
    if not csv_files:
        return None
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    print(f"Most recent CSV file: {csv_files[0]}")
    return csv_files[0]

if __name__ == "__main__":
    repo_owner = 'smecholl'
    repo_name = 'hollebar'
    target_folder = 'csv_handover'
    archive_folder = 'csv_handover/archive'
    branch_name = 'test-branch'
    
    # Read the token from pwd.txt
    with open('pwd.txt', 'r') as file:
        token = file.read().strip()

    # Step 1: Delete existing files in the target folder
    files = list_files_in_folder(repo_owner, repo_name, target_folder, token)
    if files:
        for file in files:
            if file['name'].endswith('.csv'):
                delete_file_from_github(repo_owner, repo_name, file['path'], file['sha'], branch_name, token)

    # Step 2: Find and upload the most recent CSV file to the target folder
    most_recent_csv = find_most_recent_csv('.')
    if most_recent_csv:
        with open(most_recent_csv, 'rb') as f:
            content = f.read()
        content_b64 = base64.b64encode(content).decode('utf-8')
        upload_file_to_github(repo_owner, repo_name, f"{target_folder}/{most_recent_csv}", content_b64, branch_name, token)
        
        # Step 3: Also upload the same file to the archive folder
        upload_file_to_github(repo_owner, repo_name, f"{archive_folder}/{most_recent_csv}", content_b64, branch_name, token)
    else:
        print("No CSV files found to upload.")
