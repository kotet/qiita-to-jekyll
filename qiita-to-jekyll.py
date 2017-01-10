# coding:utf-8
import argparse
import urllib.parse
import urllib.request
import json
import time
import re
import os

def get_json(access_token):
    url = 'https://qiita.com/api/v2/authenticated_user/items'
    headers = {
        'Authorization' : 'Bearer ' + access_token
    }
    values = {
        'page' : '1',
        'per_page' : '100'
    }

    data = urllib.parse.urlencode(values)

    req = urllib.request.Request(url + '?' + data, headers=headers)
    result = urllib.request.urlopen(req).read().decode('utf-8')

    return json.loads(result)

def convert_to_markdown(item,tag,note,imgpath,postdir):
    created_at = time.strptime(item['created_at'],'%Y-%m-%dT%H:%M:%S+09:00')
    filename = '%04d-%02d-%02d-%s.md' % (
        created_at[0],
        created_at[1],
        created_at[2],
        item['id'])
    front_matter = """\
---
layout: post
title: "%s"
tags: %s
---
""" % (item['title'], tag)
    qiita_image_url = 'https://qiita-image-store.s3.amazonaws.com'
    if not os.path.exists(postdir):
        os.makedirs(postdir)
    f = open(postdir+'/'+filename,'w')
    f.write(front_matter + note + '\n' + item['body'].replace(qiita_image_url,imgpath))
    f.close()

def collect_image(item,imagedir):
    regex = ':\/\/qiita-image-store\.s3\.amazonaws\.com.*?[\)\"]'
    matches = re.findall(regex,item['body'])
    for match in matches:
        url = match[0:-1]
        path = urllib.parse.urlparse(url).path
        result = urllib.request.urlopen(url).read()
        if not os.path.exists(imagedir+os.path.dirname(path)):
            os.makedirs(imagedir+os.path.dirname(path))
        f = open(imagedir+path,'wb')
        f.write(result)
        f.close()
        

def main(args):
    data = get_json(args.access_token)
    for item in data:
        convert_to_markdown(item,args.tag,args.note,args.imgpath,args.postdir)
        collect_image(item,args.imagedir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('access_token',type=str)
    parser.add_argument('--tag',type=str,default='Qiita')
    parser.add_argument('--note',type=str,default='この記事はQiitaに投稿されたものの転載です。\n\n---')
    parser.add_argument('--imgpath',type=str,default='{{ site.url }}/assets/qiita')
    parser.add_argument('--postdir',type=str,default='post')
    parser.add_argument('--imagedir',type=str,default='image')
    args = parser.parse_args()
    main(args)
