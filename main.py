# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials

# import os
# import re
# import unicodedata
# from pytube import YouTube

# # OAuth 2.0 scopes required for YouTube uploads
# SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# def slugify(value, allow_unicode=False):
#     """
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Remove characters that aren't alphanumerics,
#     underscores, or hyphens. Convert to lowercase. Also strip leading and
#     trailing whitespace, dashes, and underscores.
#     """
#     value = str(value)
#     if allow_unicode:
#         value = unicodedata.normalize('NFKC', value)
#     else:
#         value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')

# def get_authenticated_service():
#     """
#     Get authenticated YouTube API service.
#     """
#     credentials = None
#     token_file = 'token.json'
    
#     # Check if token.json exists (saved credentials)
#     if os.path.exists(token_file):
#         credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
    
#     # If credentials don't exist or are invalid, authenticate
#     if not credentials or not credentials.valid:
#         if credentials and credentials.expired and credentials.refresh_token:
#             credentials.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secret.json', SCOPES)
#             credentials = flow.run_local_server(port=8080)
        
#         # Save the credentials for the next run
#         with open(token_file, 'w') as token:
#             token.write(credentials.to_json())
    
#     return build('youtube', 'v3', credentials=credentials)

# def download_video(url):
#     """
#     Download video from YouTube URL.
#     """
#     print("Downloading video...")
#     yt = YouTube(url)
#     streams = yt.streams
    
#     quality_p = ['720p', '480p', '360p']
    
#     for q in quality_p:
#         s = streams.filter(resolution=q)
#         if s:
#             filename = f"{slugify(yt.title)}.mp4"
#             s.first().download(filename=filename)
#             return filename, yt.title
    
#     # If no stream found with specified resolutions
#     print("No stream found with specified resolutions, trying progressive stream...")
#     stream = streams.filter(progressive=True).order_by('resolution').desc().first()
#     if stream:
#         filename = f"{slugify(yt.title)}.mp4"
#         stream.download(filename=filename)
#         return filename, yt.title
    
#     raise Exception("Could not find a suitable stream to download.")

# def upload_video(filename, title, description="", tags=None, category_id="22", privacy_status="public", for_kids=False):
#     """
#     Upload a video to YouTube.
#     """
#     if tags is None:
#         tags = []
    
#     print(f"Uploading video: {title}")
#     youtube = get_authenticated_service()
    
#     body = {
#         'snippet': {
#             'title': title,
#             'description': description,
#             'tags': tags,
#             'categoryId': category_id
#         },
#         'status': {
#             'privacyStatus': privacy_status,
#             'selfDeclaredMadeForKids': for_kids
#         }
#     }
    
#     # Call the API's videos.insert method to create and upload the video
#     media = MediaFileUpload(filename, chunksize=-1, resumable=True)
#     upload_request = youtube.videos().insert(
#         part=",".join(body.keys()),
#         body=body,
#         media_body=media
#     )
    
#     # Execute the upload in chunks
#     response = None
#     while response is None:
#         status, response = upload_request.next_chunk()
#         if status:
#             print(f"Uploaded {int(status.progress() * 100)}%")
    
#     print(f"Upload Complete! Video ID: {response['id']}")
#     return response

# def main():
#     # Example 1: Download and upload
#     # filename, title = download_video('https://www.youtube.com/watch?v=example')
#     # upload_video(filename, title, description="Uploaded using Python script")
    
#     # Example 2: Upload existing file
#     upload_video(
#         filename="test.mp4",
#         title="My Video Title",
#         description="This is a video uploaded using the YouTube API.",
#         tags=["example", "upload", "api"],
#         category_id="22",  # People & Blogs
#         privacy_status="public",
#         for_kids=False
#     )

# if __name__ == "__main__":
#     main()






from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import yt_dlp
from datetime import datetime, timedelta
import pytz  # For timezone support
import os
import re
import unicodedata
# from pytube import YouTube
from tqdm import tqdm

# OAuth 2.0 scopes required for YouTube uploads
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def get_authenticated_service():
    """
    Get authenticated YouTube API service.
    """
    credentials = None
    token_file = 'token.json'
    
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())
    
    return build('youtube', 'v3', credentials=credentials)

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': '%(title)s.%(ext)s',  # Saves file with the video title
        'merge_output_format': 'mp4'  # Ensures it's saved as MP4
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info['title']
    

def convert_shorts_url(url):
    if "shorts" in url:
        return url.replace("shorts/", "watch?v=")
    return url


def upload_video(filename, title, description="", tags=None, category_id="22", 
                 privacy_status="private", for_kids=False, schedule_time=None):
    """
    Upload a video to YouTube and optionally schedule it for a future time.
    """
    if tags is None:
        tags = []

    print(f"Uploading video: {title}")
    youtube = get_authenticated_service()

    # Set the publish time if scheduling is enabled
    status = {
        'privacyStatus': privacy_status,
        'selfDeclaredMadeForKids': for_kids
    }

    if schedule_time:
        status['publishAt'] = schedule_time.isoformat()  # ISO 8601 format

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': status
    }

    # Upload the video
    media = MediaFileUpload(filename, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    with tqdm(total=100, desc="Uploading", unit="%") as pbar:
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                pbar.update(int(status.progress() * 100) - pbar.n)  # Update progress bar

    print(f"✅ Upload Complete! Video ID: {response['id']}")
    return response

# def main():
#     url = input("Enter YouTube video URL: ")
#     url = convert_shorts_url(url)
#     filename, title = download_video(url)
#     print(f"Downloaded: {filename}")


#     upload_video(
#         filename=filename,
#         title=title,
#         description="This video was uploaded using a Python script.",
#         tags=["example", "upload", "api"],
#         category_id="22",
#         privacy_status="public",
#         for_kids=False
#     )

def main():
    url = input("Enter YouTube video URL: ")
    url = convert_shorts_url(url)  # Fix Shorts URL if needed
    filename, title = download_video(url)

    print(f"Downloaded: {filename}")

    # Ask the user if they want to schedule the upload
    schedule_option = input("Do you want to schedule the upload? (yes/no): ").strip().lower()

    if schedule_option == 'yes':
        future_time = input("Enter the scheduled time (YYYY-MM-DD HH:MM, 24-hour format): ")
        
        # Convert user input to a datetime object
        scheduled_datetime = datetime.strptime(future_time, "%Y-%m-%d %H:%M")

        # Convert to UTC (YouTube requires UTC time)
        local_tz = pytz.timezone("Asia/Kolkata")  # Change this to your local timezone
        local_time = local_tz.localize(scheduled_datetime)
        utc_time = local_time.astimezone(pytz.utc)

        upload_video(
            filename=filename,
            title=title,
            description="This video was uploaded using a Python script.",
            tags=["example", "upload", "api"],
            category_id="22",
            privacy_status="private",  # Must be private for scheduling
            for_kids=False,
            schedule_time=utc_time
        )
    else:
        upload_video(
            filename=filename,
            title=title,
            description="This video was uploaded using a Python script.",
            tags=["example", "upload", "api"],
            category_id="22",
            privacy_status="public",
            for_kids=False
        )


if __name__ == "__main__":
    main()