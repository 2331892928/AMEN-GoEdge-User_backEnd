import base64
import json

from fastapi import APIRouter, Depends, Cookie, Body
import API.ServerService as ServerService
import API.UserService as UserService
import Utils
from API import HTTPWebService

app = APIRouter(prefix="/HTTPWebService", tags=['WEB服务'])

@app.post("/updateHTTPWebRedirectToHTTPS")
async def updateHTTPWebRedirectToHTTPS(UserToken: str = Cookie(None),
                            httpWebId: int = Body(None),
                            serverId: int = Body(None),
                            isOn: bool = Body(None),
                            status: bool = Body(None),
                            commons: dict = Depends(Utils.init)):
    if isOn is None or httpWebId is None or status is None or serverId is None:
        return Utils.message(201)
    #  此时全部是用户token
    config = commons[0]
    api = config['API']
    GoEdge_Api = HTTPWebService.HTTPWebService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    GoEdge_Api2 = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    info = GoEdge_Api.updateHTTPWebRedirectToHTTPS(ServerService=GoEdge_Api2,serverId=serverId,httpWebId=httpWebId,isOn=isOn,status=status)
    if not info[0]:
        if info[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=info[1])
    return Utils.message(200)

