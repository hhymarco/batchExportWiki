# -*- coding: utf-8 -*-

import logging
import requests
import os
import time
from urllib import parse
from pyquery import PyQuery as pq

def generateHeaders():
    headersBrower = '''
Accept:application/json, text/javascript, */*; q=0.01
Accept-Encoding:gzip, deflate, sdch
Accept-Language:en-US,en;q=0.8
Connection:keep-alive
User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 OPR/44.0.2510.857
    '''

    headersMap = dict()
    for item in headersBrower.splitlines():
        item = str.strip(item)
        if item and ":" in item:
            (key, value) = item.split(":", 1)
            headersMap[str.strip(key)] = str.strip(value)

    return headersMap

# 如果wiki需要登录验证,先用浏览器访问wiki,登录以后,获取该用户的cookie信息. cookie信息一般包含JSESSIONID
def genereateCookies():
    cookieString = "JSESSIONID=*****;"
    cookieMap1 = {}
    for item in cookieString.split(";"):
        item = str.strip(item)
        if item and "=" in item:
            (key, value) = item.split("=", 1)
            cookieMap1[str.strip(key)] = str.strip(value)

    return cookieMap1


def save_file(url, path):
    if os.path.exists(path):
        logging.debug("exist path=" + path)
        return

    logging.debug("将 %s 保存到 %s" % (url, path))

    logging.debug("start get " + url)

    while True:
        try:
            resp = requests.get(url, timeout=20, headers=generateHeaders(), cookies=genereateCookies(), stream=True)
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3) 
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)

    if resp.status_code  == 200:
        with open(path, 'wb') as f:
            while True:
                try:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                    break
                except requests.exceptions.ConnectionError:
                    print('ConnectionError -- please wait 3 seconds')
                    time.sleep(3)
            f.close()

        logging.debug("save file " + path)

        time.sleep(1)

    else:
        print("error ", resp.status_code)

def parse_host_pageId_fromurl(url):
    r = parse.urlsplit(url)

    if r.port == None :
        host = r.scheme + "://" + r.netloc
    else :
        host = r.scheme + "://" + r.netloc + ":" + r.port

    params=parse.parse_qs(r.query,True)
    if "pageId" in params:
        pageId = params["pageId"]
    if "pageId" not in params:
        pageId = "0"

    return (host, pageId[0])


def get_sub_pages_url(parentUrl):
    urlarrays = parse_host_pageId_fromurl(parentUrl)
    if  urlarrays[1]=="0":
        return []

    url = "%s/plugins/pagetree/naturalchildren.action?decorator=none&excerpt=false&sort=position&reverse=false&disableLinks=false&expandCurrent=false&hasRoot=true&pageId=%s&treeId=0&startDepth=0" % urlarrays
    
    while True:
        try:
            resp = requests.get(url, timeout=20, headers=generateHeaders(), cookies=genereateCookies(), stream=True)
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3) 
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)

    if resp.status_code == 200:
        doc = pq(resp.text)
        links = []

        for a in doc.find("a").items():
            text = a.text().strip()
            if a.attr("href") and text:
                links.append({
                    "title" : text.encode("utf-8"),
                    "href" : parse.urljoin(parentUrl, a.attr("href"))
                })

        return links

    else :
        logging.error("failed get url %s status_code=%d " % (url, resp.status_code))

    return []

def export_wiki(wiki_title, wiki_page_url, dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

    urlarrays=parse_host_pageId_fromurl(wiki_page_url)
    export_url = "%s/exportword?pageId=%s" % urlarrays
    save_file(export_url, dir + "/" + wiki_title + ".doc")

    subpages = get_sub_pages_url(wiki_page_url)
    if subpages :
        parentdir = dir + "/" + wiki_title
        for subpage in subpages :
            export_wiki(str(subpage["title"],'utf-8').replace("/","_"), subpage["href"], parentdir)


logging.basicConfig(level=logging.DEBUG)

# 请先修改generateHeaders和genereateCookies方法的配置
wiki_page_url = "http://wiki.***.**/pages/viewpage.action?pageId=***"
wiki_title = "{title}"
dir = "/User/{mypath}"
export_wiki(wiki_title, wiki_page_url, dir)

