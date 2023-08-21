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



#GOOGLE_KEY_ID = "f6b0af59c8f9a4ac2159f4b2ceb2904af514d43c"
#GOOGLE_KEY_SECRET = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCc2pmrD+jVQfWF\niKHOfIZzc5Szkp4TgI4glcxF89UJpsuTpYmy6RKP5Il9A8q6D/9F62u69N2jC219\ncOAOAAJFY/p+Jhs9aUwQy4tk1OQuCWgNmJvseSFobJqYmzRrO+DBpQqvQ1vxTRwK\nPai3/MCwOpuh6LVXbN9RpCrtb01u522DWOmq7nf6E1bDm049yb4il+mzyITlVRk4\nM2WzEbW7OP+mGjMf1iLjNpaKT7TzFsnVuwiTPEVF+wEzC8U4uzZmpwW5RFIL+p3V\ndDq2nezemJz5SOD+vYYFZ3Yh/P0JQYeRr4AZ6eQVd+SeHyXi5CHoZiNrUkYTE87E\nta6MMYLdAgMBAAECggEACTZwsKKsVPw9CLUL9eYL+pN3EC4EIVabYnAR8aje4iR9\nEAS4x/yXBcMRTTmwCkoevvNTHkW8D9O/wE6lJkVbXMqAv7CKyIpa+KCP5SH47fhI\n94V3YQYDT5ATa3OwOj0n2A/SxxUAfTV/eF2DP501jxQ+KF4T6pjfK/slt1Difik7\nj76jbTplUSn+cLZh/cpjHeSR9L2I7jz1jwApDoPWUvdKvWqObAUl5/y3CC1nzgbi\nkmk8qKUD1x5LBH2yQjCZFwcQIEkC4vJ4Knnjb4G1EkU5RJTwBP8UYN84ckn/0wyP\n2Ld+WOt7XdrIS6ExH4GPvx7K4DrPun4+g2bxfnOvwQKBgQDQJ/KH3Bzw1GkvBOvW\nSkP0qAgHLmfG9ybx6xMjcKoeu9wJKyFt9wRuLJb9jWbY/z9sKogVwmTDmcbnNDGm\nZFs5zbjCJpPAaMdcdgsw8mt8eAX9TFHX9SKvp5khO1mmglQXpLomDRtz84Jr0DhS\nQwckfb/gG8MZXTvOrkNCftKtQQKBgQDA5/938mDDYaIAU3jerPNhFAeoCoqDYvTS\nZE46RFcj405q3pQoGW9UxNCDCAU1cQKr8ZvbmKYgYahURQCLaLGjVl08hExul2Nm\nBXkr/a6vQDINxf2yInR886Nych9Qq9icaqIMU4wg7zAantDhHLNBxe1PB/PeQye5\nezlIhzLCnQKBgC/A6mAGvFD3ugXCcERiF0L6hZT4LXC05KddUa+wuiaA3JLx5SJw\nKAEKk70pgm3H6Qnsm/m59hn1nm8OR1Gv9knFi1xnM0BSCWKJ5jlddBFDC8S3jJMp\ntsJrhbLdBc0wWxBthxMRsLmiJMqNI06j9/CENM+6LsET5ZOd4OpRZA3BAoGAYN9g\ndEy8eQF7iCxi43f41IRpf+KjQm2cQldqzWnqVLReed6CikyTkv8vMs4BR6AT1mMD\ngNh8fIBuNrtcFaYipsLFGZHajCLsIJyZCBVh9tIHENGfoCgbVXBIYT2cKjfSFGKc\nNBJ0qUlUX9nnTVTLVDlf/bMhrTkOJuARmTGDtSUCgYAsjoWxsaRlczVdb9e6NpSn\nwjths5gpL5JYUZKbY9e5Z8Y7nLRuuqkq7KFqkudLFa5J1cwddtkY639n3h0aHwnf\n71eCCjOsskNdU9VuzB+h4Z11ohlePjW9WuPFgpANJPPUAj8iepn2eDDOmVyxbCOS\n4jMtuy8YvmzaQSCoobfNcw==\n-----END PRIVATE KEY-----\n"
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
        print(item)
        fileId = item['id']
        print(fileId)
        rst = service.files().get_media(fileId = fileId)
        print(rst)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, rst)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        # Write the stuff
        with open(f"armorial/{item['name']}", "wb") as f:
            f.write(file.getbuffer())
            #print(file.getvalue())

