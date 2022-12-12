import os
import shutil
import sys
import time
from fastapi import FastAPI, Request, Depends, Cookie, HTTPException
import requests

import Sql
import Utils
import API
from Controller.HTTPAccessLogService import app as HTTPAccessLogService
from Controller.UserService import app as UserService
from Controller.Verification import app as Verification
from Controller.ConfigService import app as ConfigService
from Controller.ServerService import app as ServerService
from Controller.MetricStatService import app as MetricStatService
from Controller.OriginService import app as OriginService
from Controller.SSLCertService import app as SSLCertService
from Controller.SSLPolicyService import app as SSLPolicyService
from Controller.HTTPWebService import app as HTTPWebService


def userInit(UserToken: str = Cookie(None),
             UserId: int = Cookie(None),
             commons: dict = Depends(Utils.init)):
    #  查询cookie是否过期 或 非法Token
    # print(UserToken)
    #  没有API验证是否正确，读取数据库，虽然每个接口都有输出token错误，提前做好
    if UserToken is None:
        raise HTTPException(status_code=388, detail=Utils.message(388))
    ESql: Sql.Sql = commons[2]
    if ESql is None:
        raise HTTPException(status_code=393, detail=Utils.message(393))
    userinfo_token = ESql.fetch_where("edgeAPIAccessTokens", {
        "token": UserToken
    })
    if userinfo_token is None:
        raise HTTPException(status_code=388, detail=Utils.message(388))
    if int(userinfo_token['expiredAt']) < time.time():
        #  过期了
        raise HTTPException(status_code=388, detail=Utils.message(388))
    #  查询userid是否有效
    if userinfo_token['userId'] != UserId:
        raise HTTPException(status_code=388, detail=Utils.message(388))


# 添加全局依赖
app = FastAPI(dependencies=[Depends(Utils.verify_token)], docs_url=None, redoc_url=None)
# app.mount()
# 挂载

app.include_router(HTTPAccessLogService)
app.include_router(UserService)
app.include_router(Verification)
app.include_router(ConfigService)
app.include_router(ServerService, dependencies=[Depends(userInit)])
app.include_router(OriginService, dependencies=[Depends(userInit)])
app.include_router(SSLCertService, dependencies=[Depends(userInit)])
app.include_router(SSLPolicyService, dependencies=[Depends(userInit)])
app.include_router(HTTPWebService, dependencies=[Depends(userInit)])
app.include_router(MetricStatService)


@app.on_event('startup')
def init_data():
    #  检查配置文件是否存在，不存在创建一个
    if not os.path.exists('./Config/Config.json'):
        shutil.copy('./Config/Config_initialization.json', './Config/Config.json')
    # 查询adminId,根据acceskeyid 和key查找
    config = Utils.read_config()
    mysql = config['mysql']
    API_Config = config['API']
    Emysql = config['EdgeAdmin_mysql']
    ESql = Sql.Sql(Emysql['host'], Emysql['port'], Emysql['user'], Emysql['password'], Emysql['database'])
    user_info = ESql.fetch_where("edgeUserAccessKeys", {
        "uniqueId": API_Config['AccessKey ID'],
        "secret": API_Config['AccessKey Key'],
        "state": 1
    })
    if user_info is None:
        raise "id 和 key错误"
    else:
        #  写入adminId
        update = {
            "adminId": user_info["adminId"]
        }
        config.update(update)
        Utils.update_config(config)
    print("AMEN-GoEdge-User后端启动完毕！")


@app.on_event('shutdown')
def shutdown():
    print("shutdown")


if __name__ == "__main__":
    pass
    #import uvicorn

    #uvicorn.run(app='main:app', host="0.0.0.0", port=8002, reload=True, debug=True)
