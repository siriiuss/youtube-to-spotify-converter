import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
load_dotenv()

def convert(url, name):
    # YouTube API yetkilendirme.
    scopes = ['https://www.googleapis.com/auth/youtube.readonly']
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=scopes)
    credentials = flow.run_console()

    youtube = build('youtube', 'v3', credentials=credentials)

    # Spotify API yetkilendirme
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    redirect_uri = 'https://youtube-to-spotify-converter.vercel.app/callback'
    scope = 'playlist-modify-public'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    ))

    # YouTube oynatma listesi URL'sini alın
    playlist_url = url

    # YouTube'dan şarkı başlıklarını ve video ID'lerini alın
    playlist_id = re.findall(r'(?<=list=)([a-zA-Z0-9_-]+)', playlist_url)[0]

    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )

    response = request.execute()

    song_titles = []
    video_ids = []

    for item in response['items']:
        title = item['snippet']['title']
        video_id = item['snippet']['resourceId']['videoId']

        song_titles.append(title)
        video_ids.append(video_id)

    # Spotify çalma listesi oluştur
    user_id = sp.me()['id']
    playlist_name = name

    playlist = sp.user_playlist_create(user=user_id, name=playlist_name)

    # YouTube'dan alınan şarkı başlıklarını Spotify'da ara ve şarkı URI'lerini al
    song_uris = []

    for title in song_titles:
        results = sp.search(q=title, type='track')
        items = results['tracks']['items']

        if len(items) > 0:
            song_uri = items[0]['uri']
            song_uris.append(song_uri)

    # Şarkı URI'lerini Spotify çalma listesine ekle
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=song_uris)


