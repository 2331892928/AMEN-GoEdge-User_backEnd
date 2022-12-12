import json
import traceback

import requests


class Api:
    def __init__(self, Host, Id, Key, Token=None):
        self.Token = Token
        self.Host = Host
        self.Id = Id
        self.Key = Key
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            "Content-Type": "application/json",
            "AMEN": "YMWLGZS"
        }
        session = requests.session()
        session.headers['X-Edge-Access-Token'] = Token
        session.headers['AMEN'] = "YMWLGZS"
        # session.headers['Content-Type'] = "application/json"
        session.headers[
            'User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
        session.keep_alive = False
        self.Session = session

    def get(self, url, headers):
        try:
            return self.Session.get(url, headers=headers)
        except:
            return None

    def post(self, url, json=None, headers=None):
        try:
            return self.Session.post(url, json=json, headers=headers)
        except:
            traceback.print_exc()
            return None

    def getToken(self, type: str = "admin", accessKeyId: str = None, accessKey: str = None):
        if accessKey is None or accessKeyId is None:
            submit = {
                "type": "admin",
                "accessKeyId": self.Id,
                "accessKey": self.Key
            }
        else:
            submit = {
                "type": type,
                "accessKeyId": accessKeyId,
                "accessKey": accessKey
            }
        try:
            res = requests.post(self.Host + "/APIAccessTokenService/getAPIAccessToken", data=json.dumps(submit),
                                headers=self.header)
            if res.json()['message'] != "ok":
                return None
            return [res.json()['data']['token'], res.json()['data']['expiresAt']]
        except:
            # traceback.print_exc()
            return None

    def listHTTPAccessLogs(self):
        """列出单页访问日志"""
        submit = {
            "serverId": 2,
            "day": "20221121",
            "size": 100,
            "reverse": True
        }
        # submit = {
        #     "node": 1
        # }
        # res = self.post(self.Host + "/HTTPAccessLogService/listHTTPAccessLogs", json=submit)
        res = self.post(self.Host + "/DBService/findAllDBTables")
        print(res.text)
        # text = res.content.decode()
        # return json.loads(text)
        return ""
