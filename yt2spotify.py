import sys
import os
import spotipy
import spotipy.util as util
import requests
import re
from bs4 import BeautifulSoup

scope = 'playlist-modify-public'
redirect = 'http://google.com/'
id = os.environ.get('SPOTIFY_APP_ID')
secret = os.environ.get('SPOTIFY_APP_SECRET')


def playlistTitle(url):
    sourceCode = requests.get(url).text
    soup = BeautifulSoup(sourceCode, 'html.parser')
    return soup.title.string.replace(' - YouTube', '')


def getPlaylistSongs(url):
    # Goes through YT and collects all titles in a playlist
    songs = []
    sourceCode = requests.get(url).text
    soup = BeautifulSoup(sourceCode, 'html.parser')
    for link in soup.find_all("a", {"dir": "ltr"}):
        href = link.get('href')
        if href.startswith('/watch?'):
            songs.append(link.string.strip())
    return songs


def getPlaylistId():
    playlists = sp.current_user_playlists()
    return (playlists['items'][0]['id'])


def sanitizeTitle(title):
    title = re.sub(r'\(.*\)', '', title)  # Remove anything within ()
    title = re.sub(r'\[.*\]', '', title)  # Remove anything within []
    title = re.sub(r'\*.*\*', '', title)  # Remove anything within **
    # Remove ft/feat because it's easier to find the correct song on Spotify
    title = title.lower().replace('feat', '')
    title = title.lower().replace('ft', '')
    return title


def searchSong(title):
    return sp.search(title, limit=1, type='track', market='US')


def getSongId(song):
    # Catch and error returning false so I can later check if it was added
    # to the playlist and print the song wasn't added to the playlist
    try:
        return song['tracks']['items'][0]['id']
    except:
        return False


def addSong(song, playlist, user):
    sp.user_playlist_add_tracks(user, playlist, [song])


if len(sys.argv) > 1:
    username = sys.argv[1]
    playlistUrl = sys.argv[2]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope, id, secret, redirect)

if token:
    # Gather basic variables we only need to find once
    sp = spotipy.Spotify(auth=token)
    sp.user_playlist_create(username, name=playlistTitle(playlistUrl))
    songs = getPlaylistSongs(playlistUrl)
    playlist_id = getPlaylistId()

    for song in songs:
        music = searchSong(sanitizeTitle(song))
        songId = getSongId(music)
        if(songId):  # I check to see if getSongId() returned false here
            addSong(songId, playlist_id, username)
        else:
            print(song + " was not added")
else:
    print("Can't get token for", username)
