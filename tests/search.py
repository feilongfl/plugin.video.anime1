
import urllib2
import urllib

import re

def Post(url,params):
    _params = urllib.urlencode(params)
    req = urllib2.Request(url,_params)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0)')
    return urllib2.urlopen(req).read()

s = 'd'
p = Post('http://www.1993s.top/index.php?s=vod-search',{ 'wd': s })
print p
it = re.finditer( r'<a class=\"v-thumb stui-vodlist__thumb lazyload\" href=\"(.*?)\" title=\"(.*?)\" data-original=\"(.*?)\">', p)
print it

for match in it:
    print match.group(1)
    print match.group(2)
    print match.group(3)
