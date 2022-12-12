import hashlib
import json
import re
import time

import API.UserService as UserService
import Sql
import Utils
from Utils.tencent import Tencent
from fastapi import APIRouter, Path, Body, Depends, Request, Response, Cookie

# from main import Data_Config
app = APIRouter(prefix="/UserService", tags=['用户相关服务'])


@app.post("/registerUser", tags=['注册用户'])
async def registerUser(request1: Request,
                       username: str = Body(
                           description='必须是正确的手机号或邮箱，且必填'),
                       # username: str = Body(regex=r"^[a-zA-Z][a-zA-Z0-9_]{4,15}$", min_length=5,
                       #                      max_length=13, description='用户必填,最小5个字符，最大13个字符，且只能大写/小写字母,数字和特殊符号'),
                       password: str = Body(regex=r"^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", min_length=5,
                                            max_length=13, description='密码必填,最小5个字符，最大13个字符，且只能大写/小写字母,数字和特殊符号'),
                       # mobile: str = Body(
                       #     regex='^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$',
                       #     description='必须是正确的手机号，且必填'),
                       #  先暂时参数邮箱保留，后期手机验证码写上后，根据用户名决定不填，手机注册邮箱空，手机号存在。邮箱注册手机空，邮箱号存在
                       # email: str = Body(regex=r'([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)', description='必须正确的邮箱，且必填'),
                       code: str = Body(),
                       ticket: str = Body(None),
                       randstr: str = Body(None),
                       commons: dict = Depends(Utils.init)):
    #  初始化
    email = None
    mobile = None
    # 用户名用手机或邮箱
    ret = re.match('^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$', username)
    type = 0  # 0是邮箱 1是手机
    if not ret:
        ret = re.match(r'([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)', username)
        if not ret:
            return Utils.message(395)
        else:
            email = username
            type = 0
    else:
        mobile = username
        type = 1
    if type == 1:
        return Utils.message(202)

    config = commons[0]
    ip = request1.client.host
    #  验证腾讯滑块验证码
    if config['Config']['whetherVerificationCodeIsEnabl']:
        if ticket is None or randstr is None:
            return Utils.message(396)
        T = Tencent()
        flag = T.check_ticket(ticket, randstr)
        if flag == -1:
            return Utils.message(394)
        if flag == 0:
            return Utils.message(396)
    # 滑块结束
    api = config['API']
    Verification = config['Verification']
    #  连接数据库查询验证码
    VSql: Sql.Sql = commons[1]
    if VSql is None:
        return Utils.message(401)
    code_db = VSql.fetch_where("edge_code", {
        "number": email
    }, additionalContent="order by `timeStamp` desc")
    #  查询验证码是否过期
    millis = int(round(time.time() * 1000))
    if code_db is not None:
        if millis - int(code_db['timeStamp']) > Verification['frequentTime'] * 1000:
            return Utils.message(397)
        else:
            #  查询验证码是否正确
            if code.lower() != str(code_db['code']).lower():
                return Utils.message(397)
    else:
        return Utils.message(397)

    #  验证成功，删除此验证码
    VSql.delete("edge_code", {
        "id": code_db['id']
    })
    GoEdge_Api = UserService.UserService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    # res = GoEdge_Api.createUser(username, password, mobile, email, username, ip, None, mobile, 1)
    res = GoEdge_Api.createUser(username, password, mobile, email, username, ip, None, mobile, api['nodeClusterId'])
    if res is None:
        return Utils.message(402)
    return res


@app.post("/loginUser")
async def loginUser(
        response: Response,
        username: str = Body(),
        password: str = Body(),
        ticket: str = Body(None),
        randstr: str = Body(None),
        commons: dict = Depends(Utils.init)):
    config = commons[0]
    #  判断参数
    if username is None or username == "" or password is None or password == "":
        return Utils.message(390)
    #  验证腾讯滑块验证码
    if config['Config']['whetherVerificationCodeIsEnabl']:
        if ticket is None or randstr is None:
            return Utils.message(396)
        T = Tencent()
        flag = T.check_ticket(ticket, randstr)
        if flag == -1:
            return Utils.message(394)
        if flag == 0:
            return Utils.message(396)
    # 滑块结束
    api = config['API']
    ESql = commons[2]
    if ESql is None:
        return Utils.message(393)
    GoEdge_Api = UserService.UserService(api['HOST'], api['AccessKey ID'], api['AccessKey Key'], config['Token'])
    res = GoEdge_Api.loginUser(ESql, username, password)
    if res is None:
        return Utils.message(392)
    md = hashlib.md5(password.encode())
    if res['password'] != md.hexdigest():
        return Utils.message(390)
    if res['serversEnabled'] == 0:
        return Utils.message(391)
    #  获取成功，获取token
    userToken = GoEdge_Api.getToken("user", res['uniqueId'], res['secret'])
    if userToken is None:
        return Utils.message(402)
    #  置入cookie
    #  置入cookie
    # response.set_cookie(key="UserToken",value=userToken[0])
    response.set_cookie(key="UserToken", value=userToken[0], max_age=userToken[1], httponly=True)
    response.set_cookie(key="UserId", value=res['id'], max_age=userToken[1], httponly=True)
    return Utils.message(200, {
        "Token": userToken[0],
        "Time": userToken[1]
    })

@app.post("/logout")
async def logout(response: Response,
                 UserToken: str = Cookie(None),
                 UserId: int = Cookie(None), ):
    response.delete_cookie(key="UserToken", httponly=True)
    response.delete_cookie(key="UserId", httponly=True)

    return Utils.message(200)
