from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

def get_gdrive_service():
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
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']

cred_info = config.GOOGLE_CRED

credentials = service_account.Credentials.from_service_account_info(info=cred_info, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)
page_token = None

parents = ['1uaESfAUtJbO8eXhbdYOjOShZ_ub2QccT']


response = service.files().list(q="parents in '1uaESfAUtJbO8eXhbdYOjOShZ_ub2QccT'",
                                            corpora='allDrives',
                                            supportsAllDrives=True,
                                            includeItemsFromAllDrives=True,
                                            fields='nextPageToken, '
                                                   'files(id, name,parents,mimeType,webContentLink)',
                                            pageToken=page_token).execute()

results = response
items = results.get('files', [])
import io
from googleapiclient.http import MediaIoBaseDownload
for item in items:
    print(item['name'])
    print(item['mimeType'])
    if (item['mimeType'] == 'image/png') or (item['mimeType'] == 'image/svg+xml') :

        fileId = item['id']
        rst = service.files().get_media(fileId = fileId)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, rst)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        # Write the stuff
        print("%s/%s" %(config.ARMORIAL_PATH,item['name'].strip()))
        with open("%s/%s" %(config.ARMORIAL_PATH,item['name'].strip()), "wb") as f:
            f.write(file.getbuffer())
            #print(file.getvalue())

