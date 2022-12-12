import base64
import json

from fastapi import APIRouter, Depends, Cookie, Body
import API.ServerService as ServerService
import API.UserService as UserService
import Utils

app = APIRouter(prefix="/ServerService", tags=['网站服务'])


#  将userid放进cookie httponly中

@app.post("/createServer")
async def createServer(UserToken: str = Cookie(None),
                       UserId: int = Cookie(None),
                       clusterId: int = Body(),
                       domian: str = Body(),
                       name: str = Body(),
                       commons: dict = Depends(Utils.init)):
    #  此时全部是用户token
    config = commons[0]
    ESql = commons[2]
    if ESql is None:
        return Utils.message(393)
    api = config['API']
    #  用户管理还是需要管理token的
    GoEdge_Api = UserService.UserService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    # userId = GoEdge_Api.token_find_userid(ESql, UserToken)
    # if userId is None:
    #     return Utils.message(388)
    if clusterId != api['nodeClusterId']:
        return Utils.message(387)
    GoEdge_Api = ServerService.ServerService(api['HOST'], None, None, UserToken)
    info = GoEdge_Api.createServer(clusterId, userId=UserId, name=name, domain=domian)
    if not info[0]:
        if info[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=info[1])
    return Utils.message(200, info[1])


@app.get("/findAllUserServers")
async def findAllUserServers(UserToken: str = Cookie(None),
                             UserId: int = Cookie(None),
                             commons: dict = Depends(Utils.init)
                             ):
    #  此时全部是用户token
    config = commons[0]
    ESql = commons[2]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], None, None, UserToken)
    # GoEdge_UserService = UserService.UserService(api['HOST'], None, None, UserToken)
    # userId = GoEdge_UserService.token_find_userid(ESql, UserToken)
    domainList = GoEdge_Api.findAllUserServers(UserId)
    if not domainList[0]:
        if domainList[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=domainList[1])
    return Utils.message(200, domainList[1])


@app.post("/updateServerIsOn")
async def updateServerIsOn(UserToken: str = Cookie(None),
                           UserId: int = Cookie(None),
                           serverId: int = Body(None),
                           isOn: bool = Body(None),
                           commons: dict = Depends(Utils.init)):
    #  此时全部是用户token
    config = commons[0]
    ESql = commons[2]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], None, None, UserToken)
    updateServer = GoEdge_Api.updateServerIsOn(serverId, isOn)
    if not updateServer[0]:
        if updateServer[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=updateServer[1])
    return Utils.message(200)


@app.post("/findEnabledServerConfig")
async def findEnabledServerConfig(UserToken: str = Cookie(None),
                                  serverId: int = Body(None),
                                  isOn: bool = Body(None),
                                  commons: dict = Depends(Utils.init)):
    #  单独int参数时需要带上其他类型参数，不然类型错误，fastapibug
    config = commons[0]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    if serverId is None:
        return Utils.message(201)
    serverInfo = GoEdge_Api.findEnabledServerConfig(serverId)
    if not serverInfo[0]:
        if serverInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=serverInfo[1])
    return Utils.message(200, serverInfo[1])


@app.post("/deleteServer")
async def deleteServer(UserToken: str = Cookie(None),
                       serverId: int = Body(None),
                       isOn: bool = Body(None),
                       commons: dict = Depends(Utils.init)):
    #  单独int参数时需要带上其他类型参数，不然类型错误，fastapibug
    config = commons[0]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    if serverId is None:
        return Utils.message(201)
    #  检查是否被禁用，无禁用不可删除
    ServerInfo1 = GoEdge_Api.findEnabledServer(serverId)
    if not ServerInfo1[0]:
        if ServerInfo1[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=ServerInfo1[1])
    if ServerInfo1[1] == {}:
        return Utils.message(402)
    if "isOn" in ServerInfo1[1] and ServerInfo1[1]['isOn']:
        return Utils.message(386)
    serverInfo = GoEdge_Api.deleteServer(serverId)
    if not serverInfo[0]:
        if serverInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=serverInfo[1])
    return Utils.message(200)


@app.post("/updateServerReverseProxy")
async def updateServerReverseProxy(UserToken: str = Cookie(None),
                                   serverId: int = Body(None),
                                   reverseProxyJSON: str = Body(None),
                                   commons: dict = Depends(Utils.init)):
    #  源站配置base64传入解码后再传入类工具，类工具再编码
    config = commons[0]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    if serverId is None:
        return Utils.message(201)
    reverseProxyJSON_bytes = json.loads(base64.b64decode(reverseProxyJSON).decode("utf-8"))
    serverInfo = GoEdge_Api.updateServerReverseProxy(serverId, reverseProxyJSON_bytes)
    if not serverInfo[0]:
        if serverInfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=serverInfo[1])
    return Utils.message(200)


@app.post("/updateServerHTTPS")
async def updateServerHTTPS(UserToken: str = Cookie(None),
                            serverId: int = Body(None),
                            isOn: bool = Body(None),
                            commons: dict = Depends(Utils.init)):
    if isOn is None or serverId is None:
        return Utils.message(201)
    config = commons[0]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    HTTPSinfo = GoEdge_Api.updateServerHTTPS(serverId, isOn)
    if not HTTPSinfo[0]:
        if HTTPSinfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=HTTPSinfo[1])
    return Utils.message(200)

@app.post("/updateServerHTTP")
async def updateServerHTTP(UserToken: str = Cookie(None),
                            serverId: int = Body(None),
                            isOn: bool = Body(None),
                            commons: dict = Depends(Utils.init)):
    if isOn is None or serverId is None:
        return Utils.message(201)
    config = commons[0]
    api = config['API']
    GoEdge_Api = ServerService.ServerService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    HTTPSinfo = GoEdge_Api.updateServerHTTP(serverId, isOn)
    if not HTTPSinfo[0]:
        if HTTPSinfo[1] is None:
            return Utils.message(402)
        else:
            return Utils.message(389, message=HTTPSinfo[1])
    return Utils.message(200)
