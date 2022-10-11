##
## Created: Fri Oct 07 23:41:16 PDT 2022
##
## Copyright (C) 2022 Sriram Karra <karra.etc@gmail.com>
##
## Distributed under the very permissive "Do Whatever the Hell You Want With
## It" license.
##
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.


from __future__ import print_function

import os.path, sys
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

MIN_MSGS_PER_LOOP=10
MAX_MSGS_PER_LOOP=500                 # Keep it <= 500

OP_DRY_RUN="dry-run"            # Prints information about specified label
OP_DELETE_ALL="delete-all"      # Delete all mails with specified label
OP_DELETE_SOME="delete-ten"     # as a small sanity check
OP_PRINT_LABELS= "print-label-names" # Prints names of all labels

OP_CHOICES = [OP_DRY_RUN, OP_DELETE_ALL, OP_DELETE_SOME, OP_PRINT_LABELS]

parser = argparse.ArgumentParser()

def main():
    ## parse the command line and set up some global vars for convenience.
    args = parse_cmdline();
    flag_label_name = args.label_name

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

        if args.op == OP_PRINT_LABELS:
            print_all_labels(labels)
            return

        if not args.label_name:
            sys.stderr.write('Error: This operation requires a label name\n\n')
            parser.print_help()
            return

        target_label_id = find_target_label_id(labels, flag_label_name)
        if target_label_id == None:
            print("Could not find Target label: ", flag_label_name)
            return None

        print("Processing label name: %s; ID: %s" % (flag_label_name,
                                                     target_label_id))

        ## Useful for a dry run before deleting them
        # inspect_messages_with_label_id(service, target_label_id)

        label=service.users().labels().get(userId='me',
                                           id=target_label_id).execute()
        total_msgs = label['messagesTotal']
        total_threads =  label['threadsTotal']
        print("  Total Messages: %d; Total Threads: %d" % (total_msgs,
                                                           total_threads))
        if total_msgs == 0:
            return 0

        if args.op == OP_DRY_RUN:
            return 0

        if args.op == OP_DELETE_ALL:
            msgs_per_loop = MAX_MSGS_PER_LOOP
            num_loops = int(total_msgs/msgs_per_loop) + 1
        else:
            msgs_per_loop = MIN_MSGS_PER_LOOP
            num_loops = 1

        for i in range(num_loops):
            print("Iteration %d..." % i)

            delete_messages_with_label_id(service, target_label_id,
                                          msgs_per_loop)
    
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def parse_cmdline ():
    parser.add_argument("--op", help="What to do. Default to 'dry-run'",
                        type=str, choices=OP_CHOICES, default=OP_DRY_RUN)
    parser.add_argument("--label-name", help="specify name of label to operate on")

    return parser.parse_args()

def delete_messages_with_label_id (service, label_id, max):
    results = service.users().messages().list(userId='me',
                                              labelIds=[label_id],
                                              maxResults=max).execute()

    mids= [m['id'] for m in results['messages']]
    count = len(mids)

    print("  Batch deleting %d messages..." % count)
    results=service.users().messages().batchDelete(userId='me',
                                                   body={'ids':mids}).execute()
    
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
def inspect_messages_with_label_id (service, label_id):
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
