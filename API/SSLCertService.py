import base64

from API import Api


class SSLCertService(Api):
    def listSSLCerts(self, userId: int, offset: int, size: int, keyword: str = None):
        if keyword is None:
            submit = {
                "userId": userId,
                "offset": offset,
                "size": size
            }
        else:
            submit = {
                "userId": userId,
                "offset": offset,
                "size": size,
                "keyword": keyword
            }
        res = self.post(self.Host + "/SSLCertService/listSSLCerts", json=submit)
        try:
            if res.json()['code'] == 200:
                if "sslCertsJSON" in res.json()['data']:
                    return [True, res.json()['data']['sslCertsJSON']]
                else:
                    return [True, 'W10=']
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def createSSLCert(self, name: str, isCA: bool, certData: str, keyData: str,timeBeginAt:int,timeEndAt:int,dnsNames:list,issuer_type:str,issuer_author:str):
        """
        certData  keyData base64编码
        :param issuer_author:
        :param issuer_type:
        :param dnsNames:
        :param timeEndAt:
        :param timeBeginAt:
        :param name:
        :param isCA:
        :param certData:
        :param keyData:
        :return:
        """
        # certData_bytes  = base64.b64encode(certData.encode('utf-8')).decode("utf-8")
        # keyData_bytes  = base64.b64encode(keyData.encode('utf-8')).decode("utf-8")
        # print(certData_bytes)
        submit = {
            "isOn": True,
            "name": name,
            "serverName": "",
            "isCA": isCA,
            "certData": certData,
            "keyData": keyData,
            "timeBeginAt": timeBeginAt,
            "timeEndAt": timeEndAt,
            "dnsNames": dnsNames,
            "commonNames": [issuer_type, issuer_author],
            "description": "AMEN-GoEdge-User创建的HTTPS证书,用户为：AMEN,不可删除,请通过AMEN-GoEdge-User删除,否则AMEN-GoEdge-User异常"
        }
        res = self.post(self.Host + "/SSLCertService/createSSLCert", json=submit)
        try:
            if res.json()['code'] == 200:
                if "sslCertId" in res.json()['data']:
                    return [True,res.json()['data']['sslCertId']]
                else:
                    return [False,res.json()['message']]
            else:
                return [False,res.json()['message']]
        except:
            return [False,None]

    def countSSLCerts(self, userId: int, keyword: str = None):
        if keyword is None:
            submit = {
                "userId": userId
            }
        else:
            submit = {
                "userId": userId,
                "keyword": keyword
            }
        res = self.post(self.Host + "/SSLCertService/countSSLCerts", json=submit)
        try:
            if res.json()['code'] == 200:
                if "count" in res.json()['data']:
                    return [True, res.json()['data']['count']]
                else:
                    return [True, 0]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def deleteSSLCert(self,sslCertId:int):
        submit = {
            "sslCertId":sslCertId
        }
        res = self.post(self.Host + "/SSLCertService/deleteSSLCert", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, "ok"]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

    def countAllEnabledServersWithSSLCertId(self,sslCertId:int):
        """计算使用某个SSL证书的服务数量"""
        submit = {
            "sslCertId":sslCertId
        }
        res = self.post(self.Host+"/ServerService/countAllEnabledServersWithSSLCertId",json=submit)
        try:
            if res.json()['code'] == 200:
                if "count" in res.json()['data']:
                    return [True, res.json()['data']['count']]
                else:
                    return [True, 0]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]

