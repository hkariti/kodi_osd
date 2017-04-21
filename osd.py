from __future__ import unicode_literals
import requests
import subprocess
import pychromecast
import sys
import time

KODI_HOST = [ 'osmc.', 'osmc.local.' ]
KODI_PORT = 80
TERMINAL_NOTIFIER = '/Library/Ruby/Gems/2.0.0//gems/terminal-notifier-1.6.3/bin/terminal-notifier'
GET_WIFI_NAME = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | awk  '/ SSID/ {print $NF}'"
MAX_RETRIES = 10

class Kodi(object):
    def __init__(self, host="localhost", port=80):
        self._url = 'http://{}:{}/jsonrpc'.format(host, port)
    def jsonrpc(self, method, params=dict(), id="id"):
        return requests.post(self._url, json=dict(id=id, jsonrpc="2.0", method=method, params=params)).json()["result"]

def notification(title, artist, album, thumbnail):
    args = [TERMINAL_NOTIFIER, '-title', 'Now Playing', '-message', "{}\nby {} on {}".format(title, artist, album), '-contentImage', thumbnail, '-sender', 'com.apple.iTunes']
    subprocess.Popen(args)

def empty_notif():
    args = [TERMINAL_NOTIFIER, '-title', 'Now Playing', '-message', "Nothing Playing", '-sender', 'com.apple.iTunes']
    subprocess.Popen(args)

wifi_name = subprocess.check_output(GET_WIFI_NAME, shell=True).replace("\n", "")

if wifi_name == 'hkariti':
    for host in KODI_HOST:
        try:
            kodi = Kodi(host, KODI_PORT)
        except Exception as e:
            print "Failed to connect to {0}, skipping. error was: {1}".format(host, str(e))
    if not kodi:
        raise RuntimeError("All hosts failed, can't connect to kodi!")
    players = kodi.jsonrpc('Player.GetActivePlayers')
    if players:
        playing = kodi.jsonrpc('Player.GetItem', params=dict(playerid=players[0]["playerid"], properties=["track", "artist", "album", "title", "thumbnail"]))
        artist = ", ".join(playing['item']['artist'])
        title = playing['item']['title']
        album = playing['item']['album']
        track = playing['item']['track']
        thumbnail = requests.utils.unquote(playing['item']['thumbnail'][8:-1])
        notification(title, artist, album, thumbnail)
    else:
        empty_notif()
elif wifi_name  == 'BigPanda':
    cast = pychromecast.get_chromecast(friendly_name='What Does Cast')
    status = cast.media_controller.status
    count = 0
    while status.player_state == 'UNKNOWN':
        if count == MAX_RETRIES:
            sys.exit(0)
        time.sleep(0.1)
        count += 1
    if status.images:
        thumbnail = status.images[0].url
    else:
        thumbnail = ''
    notification(status.title, status.artist, status.album_name, thumbnail)
