import base64
import json

from API import Api
from API import ServerService


class HTTPWebService(Api):
    def updateHTTPWebRedirectToHTTPS(self, ServerService: ServerService, serverId:int, httpWebId: int, isOn: bool, status: bool):
        """

        :param ServerService:
        :param httpWebId: webid
        :param isOn: 启用禁用
        :param status: bool位=为301否则302
        :return:
        """
        ServerConfig = ServerService.findEnabledServerConfig(serverId)
        if not ServerConfig[0]:
            if ServerConfig[1] is None:
                return [False, None]
            else:
                return [False, ServerConfig[1]]
        try:
            Config = ServerConfig[1]
            Config = json.loads(base64.b64decode(Config).decode())
            redirectToHTTPSJson: dict = Config['web']['redirectToHTTPS']
            if status:
                status_i = 301
            else:
                status_i = 302
            redirectToHTTPSJson.update({
                "isOn": isOn,
                "status": status_i
            })
            redirectToHTTPSJson_bytes = base64.b64encode(json.dumps(redirectToHTTPSJson).encode('utf-8')).decode(
                "utf-8")
        except:
            return [False, None]
        submit = {
            "httpWebId": httpWebId,
            "redirectToHTTPSJSON": redirectToHTTPSJson_bytes
        }
        res = self.post(self.Host + "/HTTPWebService/updateHTTPWebRedirectToHTTPS", json=submit)
        try:
            if res.json()['code'] == 200:
                return [True, "ok"]
            else:
                return [False, res.json()['message']]
        except:
            return [False, None]
