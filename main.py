from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']
TARGET_LABEL='Lists/Linux Kernel' #### UPDATE ####

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return

        # print_all_labels(labels)

        target_label_id = find_target_label_id(labels, TARGET_LABEL)
        if target_label_id == None:
            print("Could not find Targe label: ", TARGET_LABEL)
            return None
        print("Your chosen label name: ", TARGET_LABEL, "; ID: ", target_label_id)

        delete_messages_with_label_id(service, target_label_id, 10)
        # sanity_check_messages_with_label_id(service, target_label_id)
    
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def delete_messages_with_label_id (service, label_id, max):
    label=service.users().labels().get(userId='me', id=label_id).execute()
    print("Everything we know about the label: ", label)

    results = service.users().messages().list(userId='me',
                                              labelIds=[label_id],
                                              maxResults=max).execute()

    mids= [m['id'] for m in results['messages']]
    print("Processing following messages..", len(mids))
    for mid in mids:
        print_message_id(service, mid)

    print("Executing batch delete operation...")
    results=service.users().messages().batchDelete(userId='me',
                                                   body={'ids':mids}).execute()
    print(results)
    
def print_message_id (service, mid):    
    mb = service.users().messages().get(userId='me', id=mid).execute()
    print("Message ID: ", mid)
    for header in  mb['payload']['headers']:
        if header['name'] == 'Date':
            print("    Date: ", header['value'])
        if header['name'] == 'From':
            print("    From: ", header['value'])
        if header['name'] == 'Subject':
            print("    Subject: ", header['value'])

## Fetch 10 messages with the given label id and print out some details for
## each message, allowing manual verifiation that we are picking up the right stuff.
def sanity_check_messages_with_label_id (service, label_id):
    label=service.users().labels().get(userId='me', id=label_id).execute()
    print("Everything we know about the label: ", label)

    results = service.users().messages().list(userId='me',
                                              labelIds=[label_id],
                                              maxResults=10).execute()
    for m in  results['messages']:
        print("Message ID: ", m['id'])
        mb = service.users().messages().get(userId='me', id=m['id']).execute()
        for header in  mb['payload']['headers']:
            if header['name'] == 'List-ID':
                print("List id: ", header['value'])
            if header['name'] == 'Subject':
                print("Subject: ", header['value'])

def find_target_label_id (labels, target_label_name):
    for label in labels:
        if label['name'] == target_label_name:
            return label['id']
    return None

def print_all_labels (labels):
    print('Labels:')
    for label in labels:
        print(label['id'], " ", label['name'])

if __name__ == '__main__':
    main()
