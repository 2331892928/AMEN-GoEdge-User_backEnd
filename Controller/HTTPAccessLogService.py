
import API
import Utils
from fastapi import APIRouter, Path

app = APIRouter(prefix="/HTTPAccessLogService", tags=['访问日志相关服务'])


@app.get("/listHTTPAccessLogs")
async def listHTTPAccessLogs():
    config = Utils.read_config()
    api = config['API']
    if config['Token'] == "" or config['Token'] is None:
        return {"code": 401, "msg": "server is abnormal"}
    GoEdge_Api = API.Api(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    return GoEdge_Api.listHTTPAccessLogs()
