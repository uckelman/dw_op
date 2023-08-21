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
cred_info = {"type": "service_account",
                        "project_id": "dw-order-of-precedence",
                         "private_key_id": config.GOOGLE_KEY_ID,
                         "private_key": config.GOOGLE_KEY_SECRET,
                         "client_email": "artificial-deputy-for-the-orde@dw-order-of-precedence.iam.gserviceaccount.com",
                         "client_id": "111021806773359996540",
                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                         "token_uri": "https://oauth2.googleapis.com/token",
                         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                         "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/artificial-deputy-for-the-orde%40dw-order-of-precedence.iam.gserviceaccount.com"
}

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
    if item['mimeType'] == 'image/png':
        fileId = item['id']
        rst = service.files().get_media(fileId = fileId)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, rst)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        # Write the stuff
        with open("%s/%s" %(config.ARMORIAL_PATH,item['name'].strip(), "wb") as f:
            f.write(file.getbuffer())
            #print(file.getvalue())

