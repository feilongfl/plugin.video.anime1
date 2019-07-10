# -*- coding: utf-8 -*-

import routing
import logging
import base64
import xbmcaddon
from resources.lib import kodiutils
from resources.lib import kodilogging
import xbmc
from xbmcgui import ListItem, Dialog, DialogProgress
from xbmcplugin import addDirectoryItem, endOfDirectory

import urllib2
import urllib

import re


ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()
dialog = Dialog()

def Post(url,params,referer=None):
    _params = urllib.urlencode(params)
    req = urllib2.Request(url,_params)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0)')
    if referer != None:
        req.add_header('Referer', referer)

    return urllib2.urlopen(req).read()

def Get(url, referer=None):
    # print(url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0)')
    if referer != None:
        req.add_header('Referer', referer)

    return urllib2.urlopen(req).read()

def playUrl(video_url,img,plot,title):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    li = ListItem(path=video_url,thumbnailImage=img)
    li.setInfo( type="video", infoLabels={ "title":title, "Path" : video_url, "plot": plot,} )
    playlist.add(url=video_url, listitem=li)
    xbmc.Player().play(playlist)


@plugin.route('/')
def index():
    # addDirectoryItem(plugin.handle, plugin.url_for(
    #     show_search_input), ListItem("Search"), True)
    p = Get('https://anime1.me/')
    it = re.finditer(r"""<tr class="row-\d+ (?:even|odd)"><td class="column-1"><a href="/\?cat=(\d+)">(.*?)</a></td><td class="column-2">(.*?)</td><td class="column-3">(.*?)</td><td class="column-4">(.*?)</td><td class="column-5">(.*?)</td></tr>""",p)
    for match in it:
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_detail, id=match.group(1)), ListItem(match.group(2)), True)

    endOfDirectory(plugin.handle)

def ParseDetail(url):
    p = Get(url)
    it = re.finditer(r"""<h2 class="entry-title"><a href="(.*?)" rel="bookmark">(.*?)</a>.*?<iframe src="(.*?)".*?></iframe>""",p)

    for match in it:
        vid = match.group(3)
        title = match.group(2)
        li = ListItem(title)
        li.setInfo('video', {})
        # addDirectoryItem(plugin.handle, plugin.url_for(play_Video, video=vid, title=title), li, False)
        url = '%s.m3u8|referer=%s|origin=%s' %(vid, vid, vid)
        print(url)
        addDirectoryItem(plugin.handle, url, li, False)

    mnav = re.search(r"""<div class="nav-previous"><a href="(.*?/page/\d+)" >上一頁</a>""", p)
    if mnav:
        return mnav.group(1)
    else:
        return None

@plugin.route('/Detail')
def show_detail():
    id = plugin.args['id'][0]
    url = 'https://anime1.me/?cat=%s' % id
    while True:
        print('load %s' % url)
        url = ParseDetail(url)
        if not url:
            break

    endOfDirectory(plugin.handle)

def run():
    plugin.run()
