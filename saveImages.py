#!/usr/bin/env python3

import requests
import shutil
import os
import copy
import string
from imgurpython import ImgurClient
from urllib.parse import urlparse

client_id = "1f2722d7e569663"
client_secret = "5056216d2b539b9c2e0832851250f447830c2059"

class Image():
    def __init__(self, url, name):
        self.url = url
        self.name = self.__cleanFilename(name)
        filename, extension = os.path.splitext(url)
        self.extension = extension
    def download(self):
        r = requests.get(self.url, stream=True)
        with open(self.name + self.extension, 'wb') as f:
            r.raw.decode_content=True
            shutil.copyfileobj(r.raw, f)
    def __cleanFilename(self, name):
        s = list(filter(lambda x: x in string.printable, name))
        return ''.join(s).strip().replace(" ", "")

class Page():
    FTYPES = ['jpg', 'jpeg', 'gif', 'png']
    def __init__(self, json):
        self.links = []

        self.data = json['data']
        self.__loadData()
        self.after = self.data['after']
    def __loadData(self):
        for child in self.data['children']:
            if child['kind'] == 't3':
                data = child['data']
                f, extension = os.path.splitext(data['url'])
                if '?' in extension:
                    extension = extension.split('?')[0]
                if "imgur.com" in data['url'] and extension == '':
                    client = ImgurClient(client_id, client_secret)
                    o = urlparse(data['url'])
                    if "/a/" in data['url']:
                        images = client.get_album_images(o.path.split('/')[2])
                        count = 0
                        for image in images:
                            self.links.append(Image(image.link, data['title']+str(count)))
                            count += 1
                    else:
                        print("Imgur link:" + data['url'])
                        image = client.get_image(o.path.split('/')[1])
                        self.links.append(Image(image.link, data['title']))
                elif extension.replace('.', '') in self.FTYPES:
                    self.links.append(Image(data['url'], data['title']))
                else:
                    print(extension)
                    print(data['url'])

class Subreddit():
    headers = {'User-Agent':'python'}
    def __init__(self, name):
        self.pages = []

        self.name = name
        self.baseurl = "http://www.reddit.com/r/{0}/.json".format(self.name)
        self.__loadPages()
    def downloadPage(self, pageNumber):
        pass
    def downloadAll(self):
        for p in self.pages:
            p.downloadAll()
    def __loadPages(self):
        r = requests.get(self.baseurl, headers=self.headers)
        p = Page(r.json())
        self.pages.append(copy.copy(p))
        after = p.after
        count = 1
        while after != None:
            parameters = {'count': count*25, 'after': after}
            r = requests.get(self.baseurl, headers=self.headers, params=parameters)
            p = Page(r.json())
            after = p.after
            self.pages.append(copy.copy(p))
            count = count + 1
    def getImageCount(self):
        total = 0
        for page in self.pages:
            total += len(page.links)
        return total


s = Subreddit('pics')
print(s.getImageCount())
