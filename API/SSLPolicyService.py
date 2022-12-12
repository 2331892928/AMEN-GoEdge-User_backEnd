import base64
import json

from API import Api


class SSLPolicyService(Api):
    def updateSSLPolicy(self, sslPolicyId: int, ocsp: bool, sslID: int, hsts: dict, http2Enabled: bool,
                        minVersion: str):
        if "isOn" not in hsts or "maxAge" not in hsts or "preload" not in hsts or "includeSubDomains" not in hsts:
            return [False, None]
        try:
            hstsV2 = {}
            hstsV2['isOn'] = hsts['isOn']
            hstsV2['maxAge'] = int(hsts['maxAge'])
            hstsV2['preload'] = hsts['preload']
            hstsV2['includeSubDomains'] = hsts['includeSubDomains']
            hstsV2['domains'] = []
            hsts_bytes = base64.b64encode(json.dumps(hstsV2).encode('utf-8')).decode('utf-8')
            if sslID <= 0:
                ssl = base64.b64encode('[]'.encode('utf-8')).decode('utf-8')
            else:
                ssl = base64.b64encode(('[{"isOn": true, "certId": '+str(sslID)+'}]').encode('utf-8')).decode('utf-8')
        except:
            return [False,None]
        submit = {
            "sslPolicyId": sslPolicyId,
            "http2Enabled": http2Enabled,
            "sslCertsJSON": ssl,
            "hstsJSON": hsts_bytes,
            "ocspIsOn": ocsp,
            "minVersion": minVersion
        }
        res = self.post(self.Host + "/SSLPolicyService/updateSSLPolicy", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, "ok"]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]
