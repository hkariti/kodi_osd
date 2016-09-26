from __future__ import unicode_literals
import requests
import subprocess

KODI_HOST = 'osmc.'
KODI_PORT = 80
TERMINAL_NOTIFIER = '/Library/Ruby/Gems/2.0.0//gems/terminal-notifier-1.6.3/bin/terminal-notifier'

class Kodi(object):
    def __init__(self, host="localhost", port=80):
        self._url = 'http://{}:{}/jsonrpc'.format(host, port)
    def jsonrpc(self, method, params=dict(), id="id"):
        return requests.post(self._url, json=dict(id=id, jsonrpc="2.0", method=method, params=params)).json()["result"]

kodi = Kodi(KODI_HOST, KODI_PORT)
players = kodi.jsonrpc('Player.GetActivePlayers')
if players:
    playing = kodi.jsonrpc('Player.GetItem', params=dict(playerid=players[0]["playerid"], properties=["track", "artist", "album", "title", "thumbnail"]))
    artist = ", ".join(playing['item']['artist'])
    title = playing['item']['title']
    album = playing['item']['album']
    track = playing['item']['track']
    thumbnail = requests.utils.unquote(playing['item']['thumbnail'][8:-1])
    args = [TERMINAL_NOTIFIER, '-title', 'Now Playing', '-message', "{}\nby {} on {}".format(title, artist, album), '-contentImage', thumbnail, '-sender', 'com.apple.iTunes']
else:
    args = [TERMINAL_NOTIFIER, '-title', 'Now Playing', '-message', "Nothing Playing", '-sender', 'com.apple.iTunes']
subprocess.Popen(args)
