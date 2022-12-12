import base64
import json

from fastapi import APIRouter, Depends, Cookie, Body
import API.ServerService as ServerService
import API.UserService as UserService
import Utils
from API import SSLPolicyService

app = APIRouter(prefix="/SSLPolicyService", tags=['SSL服务'])

@app.post("/updateSSLPolicy")
async def updateSSLPolicy(UserToken: str = Cookie(None),
                       sslPolicyId: int = Body(None),
                       ocsp: bool = Body(None),
                       sslID: int = Body(None),
                       hsts: str = Body(None),
                       minVersion: str = Body(None),
                       http2Enabled: bool = Body(None),
                       commons: dict = Depends(Utils.init)):
    try:
        hsts_bytes = json.loads(base64.b64decode(hsts).decode())
    except:
        return Utils.message(402)
    if sslPolicyId is None or ocsp is None or sslID is None or http2Enabled is None or minVersion is None or hsts is None:
        return Utils.message(201)
    #  此时全部是用户token
    config = commons[0]
    api = config['API']
    GoEdge_Api = SSLPolicyService.SSLPolicyService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    info = GoEdge_Api.updateSSLPolicy(sslPolicyId=sslPolicyId,ocsp=ocsp,sslID=sslID,hsts=hsts_bytes,http2Enabled=http2Enabled,minVersion=minVersion)
    if not info[0]:
        if info[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=info[1])
    return Utils.message(200)

