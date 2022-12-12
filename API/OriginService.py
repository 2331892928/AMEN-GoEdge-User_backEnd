import base64
import json
import traceback

from API import Api, ReverseProxyService


class OriginService(Api):
    def findEnabledOrigin(self, originId: int):
        submit = {
            "originId": originId
        }
        #  findEnabledOrigin是简要信息
        #  {"code":200,"data":{"Origin":{"id":2,"isOn":true,"addr":{"protocol":"http","host":"webserver1.ymqq.top","portRange":"8800"}}},"message":"ok"}
        #  findEnabledOriginConfig是复杂信息，data.originJSON是base64编码
        res = self.post(self.Host + "/OriginService/findEnabledOriginConfig", json=submit)
        try:
            if res.json()['code'] == 200:
                if 'originJSON' in res.json()['data']:
                    return [True, res.json()['data']['originJSON']]
                else:
                    return [True, None]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def updateOrigin(self, originJson: dict):
        submit = originJson
        submit_v1 = {}
        try:
            submit['connTimeout']['count'] = int(submit['connTimeout']['count'])
            submit['readTimeout']['count'] = int(submit['readTimeout']['count'])
            submit['idleTimeout']['count'] = int(submit['idleTimeout']['count'])
            connTimeoutJSON = base64.b64encode(json.dumps(submit['connTimeout']).encode('utf-8')).decode("utf-8")
            readTimeoutJSON = base64.b64encode(json.dumps(submit['readTimeout']).encode('utf-8')).decode("utf-8")
            idleTimeoutJSON = base64.b64encode(json.dumps({"unit": "second", "count": 0}).encode('utf-8')).decode("utf-8")  # submit['idleTimeout']
            # certRefJSON = base64.b64encode(json.dumps(submit['certRef']).encode('utf-8')).decode("utf-8")
            if submit['certRef']['certId'] == 0:
                certRefJSON = ""
            else:
                certRefJSON = base64.b64encode(('{"isOn": true, "certId": '+str(submit['certRef']['certId'])+'}').encode('utf-8')).decode("utf-8")

            submit_v1['originId'] = submit['id']
            submit_v1['connTimeoutJSON'] = connTimeoutJSON  # 连接时间
            submit_v1['readTimeoutJSON'] = readTimeoutJSON  # 读取时间
            submit_v1['idleTimeoutJSON'] = idleTimeoutJSON  # 闲置超时  idleTimeoutJSON
            submit_v1['name'] = submit['name']  # 名

            submit['addr']['maxPort'] = 0
            submit['addr']['minPort'] = 0
            submit_v1['addr'] = submit['addr']  # 源站信息 host portRange protocol 【maxPort minPort】这两个保持默认0

            submit_v1[
                'description'] = "AMEN-GoEdge-User创建的源站,不可删除,请通过AMEN-GoEdge-User删除,否则AMEN-GoEdge-User异常"  # 备注submit['description']
            submit_v1['weight'] = int(submit['weight'])  # 权重
            submit_v1['isOn'] = submit['isOn']  # 是否启用
            submit_v1['maxConns'] = 0  # 最大连接数submit['maxConns']
            submit_v1['maxIdleConns'] = 0  # 最大空闲超时时间submit['idleConns']
            submit_v1['domains'] = []  # 专属域名
            submit_v1['certRefJSON'] = certRefJSON  #  源站https
            submit_v1['followPort'] = False  # 端口跟随submit['followPort']
            submit_v1['host'] = ""  # 回源主机名submit['requestHost']
        except:
            traceback.print_exc()
            return [False, "提交数据错误"]
        res = self.post(self.Host + "/OriginService/updateOrigin", json=submit_v1)
        try:
            if res.json()['code'] == 200:
                if 'originJSON' in res.json()['data']:
                    return [True, res.json()['data']['originJSON']]
                else:
                    return [True, None]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def deleteOrigin(self, reverseProxyId: int, GoEdgeApi: ReverseProxyService, originId: int, originJson: dict,
                     Primary: bool = False):
        """
        通过源数据+删除主备字段+将要删除id叠合后触发更新源站信息
        :param reverseProxyId:
        :param GoEdgeApi:
        :param originId:
        :param originJson:
        :param Primary:
        :return:
        """
        isOk = False
        for i, v in enumerate(originJson):
            if v['originId'] == originId:
                isOk = True
                break
        if not isOk:
            return [False, '未找到此源站信息']
        originJson.pop(i)
        return GoEdgeApi.updateReverseProxOrigins(reverseProxyId=reverseProxyId, originsJSON=originJson,
                                                  Primary=Primary)

    def createOrigin(self, originJson: dict):
        submit = originJson
        submit_v1 = {}
        try:
            submit['connTimeout']['count'] = int(submit['connTimeout']['count'])
            submit['readTimeout']['count'] = int(submit['readTimeout']['count'])
            # submit['idleTimeout']['count'] = int(submit['idleTimeout']['count'])
            submit['connTimeout']['unit'] = "second"
            submit['readTimeout']['unit'] = "second"
            # submit['idleTimeout'] = {}
            # submit['idleTimeout']['unit'] = "second"
            connTimeoutJSON = base64.b64encode(json.dumps(submit['connTimeout']).encode('utf-8')).decode("utf-8")
            readTimeoutJSON = base64.b64encode(json.dumps(submit['readTimeout']).encode('utf-8')).decode("utf-8")
            # idleTimeoutJSON = base64.b64encode(json.dumps(submit['idleTimeout']).encode('utf-8')).decode("utf-8")
            idleTimeoutJSON = base64.b64encode(json.dumps({"unit": "second", "count": 0}).encode('utf-8')).decode(
                "utf-8")

            certRefJSON = base64.b64encode(json.dumps(None).encode('utf-8')).decode("utf-8")

            submit_v1['name'] = ""

            submit_v1['addr'] = submit['addr']
            submit_v1['addr']['minPort'] = 0
            submit_v1['addr']['maxPort'] = 0

            submit_v1['description'] = ""

            submit_v1['weight'] = int(submit['weight'])

            submit_v1['isOn'] = True

            submit_v1['connTimeoutJSON'] = connTimeoutJSON
            submit_v1['readTimeoutJSON'] = readTimeoutJSON
            submit_v1['idleTimeoutJSON'] = idleTimeoutJSON

            submit_v1['maxConns'] = 0

            submit_v1['maxIdleConns'] = 0

            submit_v1['domains'] = []

            submit_v1['certRefJSON'] = certRefJSON

            submit_v1['host'] = submit['host']

            submit_v1['followPort'] = False
        except:
            traceback.print_exc()
            return [False, "提交数据错误"]
        res = self.post(self.Host + "/OriginService/createOrigin", json=submit_v1)
        try:
            if res.json()['code'] == 200:
                if 'originId' in res.json()['data']:
                    return [True, res.json()['data']['originId']]
                else:
                    return [True, None]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]
