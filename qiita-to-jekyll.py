import argparse
import urllib.parse
import urllib.request
import json
import time

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


parser = argparse.ArgumentParser()
parser.add_argument('access_token',type=str)
parser.add_argument('--tag',type=str)
parser.add_argument('--note',type=str)
args = parser.parse_args()

data = get_json(args.access_token)

tag = 'Qiita'
if args.tag :
    tag = args.tag
note = 'この記事はQiitaに投稿されたものの転載です。\n\n---'
if args.tag :
    tag = args.tag
for item in data:
    created_at = time.strptime(item['created_at'],'%Y-%m-%dT%H:%M:%S+09:00')
    filename = '%04d-%02d-%02d-%s.md' % (
        created_at[0],
        created_at[1],
        created_at[2],
        item['id'])
    f = open(filename,'w')
    front_matter = """\
---
layout: post
title: "%s"
tags: %s
---
""" % (item['title'], tag)
    f.write(front_matter + note + '\n' + item['body'])
    f.close()
