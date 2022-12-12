import base64
import hashlib
import json
import re
import time

import API.UserService as UserService
import API.ReverseProxyService as ReverseProxyService
import Sql
import Utils
from API import OriginService as OriginService, ServerService, SSLPolicyService
from Utils.tencent import Tencent
from fastapi import APIRouter, Path, Body, Depends, Request, Response, Cookie

# from main import Data_Config
app = APIRouter(prefix="/OriginService", tags=['源站管理服务'])


@app.post("/updateOrigin", tags=['修改源站'])
async def updateOrigin(
        UserToken: str = Cookie(None),
        OriginJson: str = Body(None),
        isOn: bool = Body(None),
        commons: dict = Depends(Utils.init)):
    #  单参数时错误，需要加一个
    config = commons[0]
    api = config['API']
    if OriginJson is None:
        return Utils.message(201)
    GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    OriginJson_bytes = json.loads(base64.b64decode(OriginJson).decode("utf-8"))
    originInfo = GoEdge_Api.updateOrigin(OriginJson_bytes)
    if not originInfo[0]:
        if originInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=originInfo[1])
    return Utils.message(200)


@app.post("/findEnabledOrigin", tags=['获取源站配置'])
async def findEnabledOrigin(
        UserToken: str = Cookie(None),
        originId: int = Body(None),
        isOn: bool = Body(None),
        commons: dict = Depends(Utils.init)):
    #  源站配置base64传入解码后再传入类工具，类工具再编码
    #  单int参数需要带其他类型参数，否则异常，fastapibug
    config = commons[0]
    api = config['API']
    GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    if originId is None:
        return Utils.message(201)
    originInfo = GoEdge_Api.findEnabledOrigin(originId)
    if not originInfo[0]:
        if originInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=originInfo[1])
    return Utils.message(200, data=originInfo[1])


@app.post("/deleteOrigin")
async def deleteOrigin(
        UserToken: str = Cookie(None),
        originId: int = Body(None),
        reverseProxyId: int = Body(None),
        isOn: bool = Body(None),
        originJson: str = Body(None),
        commons: dict = Depends(Utils.init)):
    # isOn是否主源站,originJson primaryOrigins等字段更新，通过这个字段进行引导源站
    config = commons[0]
    api = config['API']
    GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    GoEdge_Api2 = ReverseProxyService.ReverseProxyService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'],
                                                          UserToken)
    if originId is None:
        return Utils.message(201)
    if reverseProxyId is None:
        return Utils.message(201)
    if isOn is None:
        return Utils.message(201)
    if originJson is None:
        return Utils.message(201)
    OriginJson_bytes = json.loads(base64.b64decode(originJson).decode("utf-8"))
    ReverseProxOriginsInfo = GoEdge_Api.deleteOrigin(reverseProxyId=reverseProxyId, GoEdgeApi=GoEdge_Api2,
                                                     originId=originId, originJson=OriginJson_bytes, Primary=isOn)
    if not ReverseProxOriginsInfo[0]:
        if ReverseProxOriginsInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=ReverseProxOriginsInfo[1])
    return Utils.message(200)


@app.post("/createOrigin")
async def createOrigin(
        UserToken: str = Cookie(None),
        reverseProxyId: int = Body(None),
        originJson: str = Body(None),
        isOn: bool = Body(None),
        commons: dict = Depends(Utils.init)):
    # 单int参数需要带其他类型参数，否则异常，fastapibug
    #  isOn为是否主源站，true主，false备
    config = commons[0]
    api = config['API']
    GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    if originJson is None:
        return Utils.message(201)
    if isOn is None:
        return Utils.message(201)
    if reverseProxyId is None:
        return Utils.message(201)
    OriginJson_bytes = json.loads(base64.b64decode(originJson).decode("utf-8"))
    originInfo = GoEdge_Api.createOrigin(OriginJson_bytes)

    if not originInfo[0]:
        if originInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=originInfo[1])
    #  创建成功，放入反代理
    sourceData = OriginJson_bytes['sourceData']
    GoEdge_Api2 = ReverseProxyService.ReverseProxyService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'],
                                                          UserToken)
    if originInfo[1] is None:
        return Utils.message(402)
    sourceData.append({"isOn": True, "originId": originInfo[1]})
    ReverseProxOriginsInfo = GoEdge_Api2.updateReverseProxOrigins(reverseProxyId=reverseProxyId, originsJSON=sourceData,
                                                                  Primary=isOn)
    if not ReverseProxOriginsInfo[0]:
        if ReverseProxOriginsInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=ReverseProxOriginsInfo[1])
    return Utils.message(200)


@app.post("/updateOriginSSL")
async def updateOriginSSL(
        UserToken: str = Cookie(None),
        serverId: int = Body(None),
        certId: int = Body(None),
        commons: dict = Depends(Utils.init)):
    config = commons[0]
    api = config['API']
    GoEdge_Api = SSLPolicyService.SSLPolicyService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    GoEdge_Api2 = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    serverInfo = GoEdge_Api2.findEnabledServerConfig(serverId)
    if not serverInfo[0]:
        if serverInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=serverInfo[1])
    serverInfoConfig = json.loads(base64.b64decode(serverInfo[1]).decode('utf-8'))
    sslPolicyId = serverInfoConfig['https']['sslPolicyRef']['sslPolicyId']
    hsts = serverInfoConfig['https']['sslPolicy']['hsts']
    http2Enabled = serverInfoConfig['https']['sslPolicy']['http2Enabled']
    ocspIsOn = serverInfoConfig['https']['sslPolicy']['ocspIsOn']
    minVersion = serverInfoConfig['https']['sslPolicy']['minVersion']
    if hsts is None:
        hsts = {
            "isOn":False,
            "maxAge":1,
            "preload":False,
            "includeSubDomains":False
        }
    sslInfo = GoEdge_Api.updateSSLPolicy(sslPolicyId=sslPolicyId,ocsp=ocspIsOn,sslID=certId,hsts=hsts,http2Enabled=http2Enabled,minVersion=minVersion)
    if not sslInfo[0]:
        if sslInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=sslInfo[1])
    return Utils.message(200)

