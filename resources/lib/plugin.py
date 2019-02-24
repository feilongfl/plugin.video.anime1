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

def playUrl(video_url,img='',plot='No info',title='video'):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    li = ListItem(path=video_url,thumbnailImage=img)
    li.setInfo( type="video", infoLabels={ "Path" : video_url, "plot": plot,} )
    playlist.add(url=video_url, listitem=li)
    xbmc.Player().play(playlist)


@plugin.route('/')
def index():
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_search_input), ListItem("Search"), True)
    p = Get('http://www.zzzfun.com/map-index.html')
    it = re.finditer(r'<a href="(.*?)" style="\s*color: #fffee4;\s*">(.*?)<\/a><em>\/<\/em><\/h5>\s*<div class="tipInfo">\s*<div class="play-img"><img src="(.*?)" alt="(?:.*?)" \/><\/div>',p)
    for match in it:
        id = re.search(r'(\d+)',match.group(1)).group()
        addDirectoryItem(plugin.handle, plugin.url_for(show_detail, id=id, img=match.group(3)), ListItem(match.group(2),thumbnailImage=match.group(3)), True)

    endOfDirectory(plugin.handle)

@plugin.route('/search_input')
def show_search_input():
    s = dialog.input('Search')
    p = Get('http://www.zzzfun.com/vod-search.html?wd=%s' % s)
    it = re.finditer(r'<a class="play-img" href="(.*?)"><img src="(.*?)" alt="(.*?)"', p)

    for match in it:
        id = re.search(r'\d+',match.group(1)).group()
        print match.group(3)
        # print id
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_detail, id=id, img=match.group(2)), ListItem(match.group(3),thumbnailImage=match.group(2)), True)

    endOfDirectory(plugin.handle)

@plugin.route('/Detail')
def show_detail():
    img = plugin.args['img'][0]
    id = plugin.args['id'][0]
    p = Get('http://www.zzzfun.com/vod-detail-id-%s.html' % id)
    it = re.finditer(r'<a class="" href="(.*?)" target="_blank"><span class="title">(.*?)<\/span><\/a>',p)

    plot = ''
    plotObj = re.search(r'<meta name="description" content="([\s\S]*?)"\s*\/>',p)
    if plotObj:
        plot = plotObj.group(1)

    for match in it:
        vid = match.group(1)
        title = match.group(2)
        li = ListItem(title,thumbnailImage=img)
        li.setInfo('video',{
            'plot': plot
        })
        addDirectoryItem(plugin.handle, plugin.url_for(play_Video, video=vid, img=img, plot=plot, title=title), li, False)

    endOfDirectory(plugin.handle)

@plugin.route('/video')
def play_Video():
    progress = DialogProgress()
    progress.create('Loading')
    progress.update(10, "", 'Loading Video Info', "")
    img = plugin.args['img'][0]
    video_url = plugin.args['video'][0]
    plot = plugin.args['plot'][0]
    title = plugin.args['title'][0]
    progress.update(30, "", 'Loading Web Files', "")
    p = Get('http://www.zzzfun.com' + video_url)
    match = re.search(r'"link_pre":"(?:.*?)","url":"(.*?)"',p)

    print("-1",match.group(1))
    video_url = base64.b64decode(match.group(1))
    video_url = urllib.unquote(video_url)
    progress.update(60, "", "Analyse Video Url", "")

    print("0",video_url)
    p = Get("http://www.zzzfun.com/static/danmu/san.php?" + video_url)
    video_url = re.search(r'<source src="(.*?)"', p).group(1)
    print("1",video_url)

    progress.update(100, "", "", "")
    progress.close()

    playUrl(video_url,img=img,plot=plot,title=title)

def run():
    plugin.run()
