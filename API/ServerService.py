import base64
import json
import traceback

import Sql
from API import Api


class ServerService(Api):
    def createServer(self, ClusterId: int, userId: int, name: str, domain: str):
        #  查询是否存在domain
        # if not self.finddomain(ESql, domain):
        #     return [False, "域名 {} 已经被其他服务所占用，不能重复使用".format(domain)]
        domainList = self.finddomain(ClusterId, [domain])

        if domainList is None:
            return [False, None]
        if domain in domainList:
            return [False, "域名 {} 已经被其他服务所占用，不能重复使用，如果确保域名是自己的，请带上域名所有权和所有权本人有效证件提交给本站管理员/客服处理".format(domain)]
        server_json = json.dumps(
            [{"name": domain, "type": "full"}]
        )
        server_json = base64.b64encode(server_json.encode('utf-8')).decode("utf-8")
        http_json = json.dumps(
            {"isOn": True, "listen": [{"host": "", "maxPort": 0, "minPort": 0, "protocol": "http", "portRange": "80"}]}
        )
        http_json = base64.b64encode(http_json.encode('utf-8')).decode("utf-8")
        https_json = json.dumps(
            {"isOn": False,
             "listen": [{"host": "", "maxPort": 443, "minPort": 443, "protocol": "https", "portRange": "443"}],
             "sslPolicy": None, "sslPolicyRef": None}
        )
        https_json = base64.b64encode(https_json.encode('utf-8')).decode("utf-8")
        submit = {
            "userId": userId,
            "name": name,
            "type": "httpProxy",
            # httpProxy:CDN加速 分发全部
            #  httpWeb:HTTP Web服务  分发静态
            #  tcpProxy:TCP反向代理   tcp反代
            #  udpProxy:UDP反向代理   udp反代
            #  先只做分发全部
            "description": "AMEN-GoEdge-User创建的网站服务,不可删除,请通过AMEN-GoEdge-User删除,否则AMEN-GoEdge-User异常",
            "serverNamesJON": server_json,
            "httpJSON": http_json,
            "httpsJSON": https_json
        }

        res = self.post(self.Host + "/ServerService/createServer", json=submit)
        try:
            if res is None:
                return [False, None]
            if res.json()['code'] != 200:
                return [False, res.json()['message']]
            return [True, res.json()['data']['serverId']]
        except:
            traceback.print_exc()
            return [False, None]

    def finddomain(self, ClusterId: int, domain: list):
        #  查询是否已存在此域名，返回id x
        #  同样没有此接口，遍历数据库
        # row = ESql.fetch("""select * from `edgeServers` WHERE `plainServerNames` like '"qqq.com"' limit 1""")
        # if row is None:
        #     return None
        # return row['id']
        submit = {
            "nodeClusterId": ClusterId,
            "serverNames": domain
        }
        res = self.post(self.Host + "/ServerService/checkServerNameDuplicationInNodeCluster", json=submit)
        try:
            if "duplicatedServerNames" in res.json()['data']:
                return res.json()['data']['duplicatedServerNames']
            else:
                return []
        except:
            return None

    def findAllUserServers(self, userId: int):
        #  防止越权，用usertoken
        submit = {
            "userId": userId
        }
        res = self.post(self.Host + "/ServerService/findAllUserServers", json=submit)
        try:
            if res.json()['code'] == 200:
                if "servers" in res.json()['data']:
                    return [True, res.json()['data']['servers']]
                else:
                    return [True, []]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def updateServerIsOn(self, serverId: int, isOn: bool):
        submit = {
            "serverId": serverId,
            "isOn": isOn
        }
        res = self.post(self.Host + "/ServerService/updateServerIsOn", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, 'ok']
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def findEnabledServerConfig(self, serverId: int):
        submit = {
            "serverId": serverId
        }
        res = self.post(self.Host + "/ServerService/findEnabledServerConfig", json=submit)
        try:
            if res.json()['code'] == 200:
                if 'serverJSON' in res.json()['data']:
                    # base64.b64decode(res.json()['data']['serverJSON'])
                    return [True, res.json()['data']['serverJSON']]
                else:
                    return [True, "e30="]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def findEnabledServer(self, serverId: int):
        submit = {
            "serverId": serverId
        }
        res = self.post(self.Host + "/ServerService/findEnabledServer", json=submit)
        try:
            if res.json()['code'] == 200:
                if 'server' in res.json()['data']:
                    return [True, res.json()['data']['server']]
                else:
                    return [True, {}]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def deleteServer(self, serverId: int):
        submit = {
            "serverId": serverId
        }
        res = self.post(self.Host + "/ServerService/deleteServer", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, "ok"]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def updateServerReverseProxy(self, serverId: int, reverseProxyJSON: dict):
        #  这种方式不安全，换
        # reverseProxyJSON_bytes = base64.b64encode(json.dumps(reverseProxyJSON).encode('utf-8')).decode("utf-8")
        # reverseProxyJSON_bytes = base64.b64encode(json.dumps(reverseProxyJSON).encode('utf-8')).decode("utf-8")
        ServerConfig = self.findEnabledServerConfig(serverId)
        if not ServerConfig[0]:
            if ServerConfig[1] is None:
                return [False, None]
            else:
                return [False, ServerConfig[1]]
        try:
            Config = ServerConfig[1]
            Config = json.loads(base64.b64decode(Config).decode())
            reverseProxy = Config['reverseProxyRef']
            reverseProxy['isOn'] = reverseProxyJSON['isOn']
            reverseProxyJSON_bytes = base64.b64encode(json.dumps(reverseProxy).encode('utf-8')).decode("utf-8")
        except:
            return [False, None]
        submit = {
            "serverId": serverId,
            "reverseProxyJSON": reverseProxyJSON_bytes
        }
        res = self.post(self.Host + "/ServerService/updateServerReverseProxy", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, "ok"]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def updateServerHTTPS(self,serverId:int,isOn:bool):
        ServerConfig = self.findEnabledServerConfig(serverId)
        if not ServerConfig[0]:
            if ServerConfig[1] is None:
                return [False, None]
            else:
                return [False, ServerConfig[1]]
        try:
            Config = ServerConfig[1]
            Config = json.loads(base64.b64decode(Config).decode())
            https = Config['https']
            https['isOn'] = isOn
            httpsJSON_bytes = base64.b64encode(json.dumps(https).encode('utf-8')).decode("utf-8")
        except:
            return [False, None]
        submit = {
            "serverId": serverId,
            "httpsJSON": httpsJSON_bytes
        }
        res = self.post(self.Host+"/ServerService/updateServerHTTPS",json=submit)
        try:
            if res.json()['code'] == 200:
                return [True,"ok"]
            else:
                return [False,res.json()['message']]
        except:
            return [False,None]

    def updateServerHTTP(self,serverId:int,isOn:bool):
        ServerConfig = self.findEnabledServerConfig(serverId)
        if not ServerConfig[0]:
            if ServerConfig[1] is None:
                return [False, None]
            else:
                return [False, ServerConfig[1]]
        try:
            Config = ServerConfig[1]
            Config = json.loads(base64.b64decode(Config).decode())
            https = Config['http']
            https['isOn'] = isOn
            httpsJSON_bytes = base64.b64encode(json.dumps(https).encode('utf-8')).decode("utf-8")
        except:
            return [False, None]
        submit = {
            "serverId": serverId,
            "httpJSON": httpsJSON_bytes
        }
        res = self.post(self.Host+"/ServerService/updateServerHTTP",json=submit)
        try:
            if res.json()['code'] == 200:
                return [True,"ok"]
            else:
                return [False,res.json()['message']]
        except:
            return [False,None]



