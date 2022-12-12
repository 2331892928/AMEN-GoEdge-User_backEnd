import hashlib
import json
import re
import time
import API.MetricStatService as MetricStatService
import API.UserService as UserService
import API.SSLCertService as SSLCertService
import Sql
import Utils
import API.ServerService as ServerService
import API.OriginService as OriginService
import API.ReverseProxyService as ReverseProxyService
from Utils.tencent import Tencent
from fastapi import APIRouter, Path, Body, Depends, Request, Response, Cookie

# from main import Data_Config
app = APIRouter(prefix="/MetricStatService", tags=['指标'])


@app.get("/listMetricStats", tags=['读取'])
async def listMetricStats(UserToken: str = Cookie(None),
                          commons: dict = Depends(Utils.init)):
    config = commons[0]
    ESql = commons[2]
    UserToken = "YMJwls2Xj7JU7zBjGzlk6qjoZKj6ERkiicHx0TfgQgUcD5ntwQeJcuEziS6wNUAp1F2MkKbkdrAvx7AQYpcTgZOmrNLu2X2zt3ARPMA4OgL4nnsOORHlGJvAd3ak6MxN"
    if ESql is None:
        return Utils.message(393)
    api = config['API']
    # GoEdge_Api = MetricStatService.MetricStatService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    # GoEdge_Api.listMetricStats()
    # GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    # GoEdge_Api = ReverseProxyService.ReverseProxyService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], UserToken)
    # GoEdge_Api = OriginService.OriginService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    GoEdge_Api2 = SSLCertService.SSLCertService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    # GoEdge_Api = SSLCertService.SSLCertService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'],
    #                                                      UserToken)
    # serverInfo = GoEdge_Api.findEnabledOrigin(2)
    a = """
    [{"isOn": false, "originId": 2}]
    """
    # GoEdge_Api.updateReverseProxOrigins(2,json.loads(a),True)
    # GoEdge_Api.listSSLCerts(1,0,5)
    # GoEdge_Api2.listSSLCerts()
    GoEdge_Api2.countAllEnabledServersWithSSLCertId(2)
    return 1