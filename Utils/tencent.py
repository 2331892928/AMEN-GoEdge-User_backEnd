import json
import random
import urllib
from urllib import parse

import requests


class Tencent:
    def __init__(self):
        pass

    def check_ticket(self, ticket: str, randstr: str):
        url = 'https://cgi.urlsec.qq.com/index.php?m=check&a=gw_check&callback=url_query&url=https%3A%2F%2Fwww.qq.com' \
              '%2F' + str(
            random.randint(
                111111, 999999)) + '&ticket=' + urllib.parse.quote(ticket) + '&randstr=' + urllib.parse.quote(randstr)
        try:
            res = requests.get(url, headers={
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Connection": "close",
                "referer": "https://urlsec.qq.com/check.html",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/86.0.4240.198 Safari/537.36",
            })
            # print(res.content.decode())
            arr = self.jsonp_decode(res.content.decode())
            arr = json.loads(arr)
            if arr['reCode'] == 0:  # 验证通过
                return 1
            elif arr['reCode'] == -109:  # 验证码错误
                return 0
            else:  # 接口已失效
                return -1
        except:  # 接口已失效
            return -1

    def jsonp_decode(self, jsonp: str):
        jsonp = jsonp.lstrip()
        jsonp = jsonp.rstrip()
        if jsonp[0:1] != "[" and jsonp[0:1] != "{":
            begin = jsonp.find("(")

            if begin != -1:
                end = jsonp.find(")")
                if end != -1:
                    jsonp = jsonp[begin + 1:end]
        return jsonp
