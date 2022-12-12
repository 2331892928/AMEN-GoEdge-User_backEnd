import base64
import json

from API import Api


class ReverseProxyService(Api):
    def updateReverseProxOrigins(self, reverseProxyId: int, originsJSON: dict, Primary: bool = False):
        """
        修改源站信息，不是源站配置，是网站服务器->源站信息->源站配置。做新增，新增数据为：源数据+新数据，源数据由上层传递，本函数不做查询源数据
        :param reverseProxyId:
        :param originsJSON:
        :param Primary:
        :return:
        """
        originsJSON_bytes = base64.b64encode(json.dumps(originsJSON).encode('utf-8')).decode("utf-8")
        submit = {
            "reverseProxyId": reverseProxyId,
            "originsJSON": originsJSON_bytes
        }
        if Primary:
            res = self.post(self.Host + "/ReverseProxyService/updateReverseProxyPrimaryOrigins", json=submit)
        else:
            res = self.post(self.Host + "/ReverseProxyService/updateReverseProxyBackupOrigins", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True,"ok"]
            else:
                return [True, res.json()['message']]
        except:
            return [False,None]