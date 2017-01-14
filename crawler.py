#!/usr/bin/env python3
# -*- coding: utf-8 -*-

domain = 'https://wiki.52poke.com/'
listUrl = 'wiki/宝可梦列表（按全国图鉴编号）/简单版'
# listUrl = '招式列表'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'


def getHtmlStr(url, domain='', user_agent=''):
    """get html text from url

    :url: TODO
    :domain: TODO
    :returns: TODO

    """
    from urllib.parse import quote
    from urllib import request
    import zlib

    url = domain + url
    url = quote(url, safe='/:')
    req = request.Request(url)
    req.add_header('User-Agent', user_agent)
    with request.urlopen(req) as response:
        print('Status:', response.status, response.reason)
        for k, v in response.getheaders():
            print('%s: %s' % (k, v))
        content_encoding = response.headers.get('Content-Encoding')
        if content_encoding == 'gzip':
            html = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)
        html = html.decode('utf-8')
        print(html)


def getPokewikiHtml(url):
    return getHtmlStr(url, domain, user_agent)


listHtml = getPokewikiHtml(listUrl)
