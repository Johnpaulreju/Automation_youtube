from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import yt_dlp
from datetime import datetime
import pytz
import os
from tqdm import tqdm
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]


def get_authenticated_service():
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


def download_video(url, filename="video.mp4"):
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'noprogress': True,
        'quiet': True
    }
    if os.path.exists(filename):
        os.remove(filename)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return filename, info['title']


def upload_video(filename, title, description="", tags=None, category_id="22", 
                 privacy_status="private", for_kids=False, schedule_time=None):
    if tags is None:
        tags = []

    print(f"Uploading video: {title}")
    youtube = get_authenticated_service()

    status = {'privacyStatus': privacy_status, 'selfDeclaredMadeForKids': for_kids}

    if schedule_time:
        status['publishAt'] = schedule_time.isoformat()

    body = {
        'snippet': {'title': title, 'description': description, 'tags': tags, 'categoryId': category_id},
        'status': status
    }

    media = MediaFileUpload(filename, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    with tqdm(total=100, desc="Uploading", unit="%") as pbar:
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                pbar.update(int(status.progress() * 100) - pbar.n)

    video_id = response['id']
    print(f"✅ Upload Complete! Video ID: {video_id}")
    return video_id


@app.route('/schedule', methods=['POST'])
def schedule_upload():
    data = request.json
    url = data.get("url")
    schedule_time = data.get("schedule_time")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    filename, title = download_video(url)

    utc_time = None
    if schedule_time:
        local_tz = pytz.timezone("Asia/Kolkata")
        local_time = local_tz.localize(datetime.strptime(schedule_time, "%Y-%m-%d %H:%M"))
        utc_time = local_time.astimezone(pytz.utc)

    video_id = upload_video(filename, title, schedule_time=utc_time)

    return jsonify({"message": "Upload scheduled", "video_id": video_id})


@app.route('/delete', methods=['POST'])
def delete_video():
    data = request.json
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    try:
        youtube = get_authenticated_service()
        youtube.videos().delete(id=video_id).execute()

        return jsonify({"message": f"Video {video_id} deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
