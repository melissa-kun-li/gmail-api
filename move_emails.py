from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.labels', 'https://www.googleapis.com/auth/gmail.modify']

def main():
    """ Finds the messages in inbox containing "unsubscribe".
    Removes the message's Inbox label, adds Subscriptions label.
    i.e. Emails moved from the inbox folder into the subscriptions folder.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # make the API request
    service = build('gmail', 'v1', credentials=creds)

    # find label id where name = 'Subscriptions', later change to app name
    labels = service.users().labels().list(userId = 'me').execute()
    for item in labels['labels']:
        if item['name'] == 'Subscriptions':
            label_id = item['id']

    # need to incorporate nextPageToken in case more than 511 emails
    results = service.users().messages().list(userId = 'me', q = 'label:INBOX unsubscribe', maxResults = 511).execute()
    for item in results['messages']:
        message_id = item['id']
        # message = service.users().messages().get(userId = "me", id = message_id).execute()
        # print(message["snippet"])
        # print('\n')

        message = delete_and_add_label('me', message_id, label_id, 'INBOX')
        try:
            modified_message = service.users().messages().modify(userId = 'me', id = message_id, body = message).execute()
            print('Successfully moved email from Inbox to Subscriptions!')
        except Exception as e:
            print(f'Error occurred: {e}')
        
    print('\n')

def delete_and_add_label(userId, messageId, labelToAdd, labelToRemove):
    message = {
        'userId': userId,
        'id': messageId,
        'addLabelIds': labelToAdd,
        'removeLabelIds': labelToRemove
    }
    return message


if __name__ == '__main__':
    main()