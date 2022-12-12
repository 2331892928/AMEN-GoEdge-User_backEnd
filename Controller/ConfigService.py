import API.UserService as UserService
import Sql
import Utils
from fastapi import APIRouter, Path, Body, Depends, Request

app = APIRouter(prefix="/ConfigService", tags=['获取本站配置'])


@app.get("/get")
async def get():
    allConfig = Utils.read_config()
    Config = allConfig['Config']
    ConfigV2 = allConfig['Verification']['title']
    C = {}
    C.update(Config)
    C.update({
        "title": ConfigV2
    })
    C.update({
        "nodeClusterId": allConfig['API']['nodeClusterId']
    })
    return C
