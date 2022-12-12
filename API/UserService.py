import hashlib
import json

import requests

import Sql
import Utils
from API import Api


class UserService(Api):
    def registerUser(self, username, password, mobile, email, fullname, ip, source):
        """注册用户"""
        submit = {
            "username": username,
            "password": password,
            "mobile": mobile,
            "email": email,
            "fullname": fullname,
            "ip": ip
        }
        res = self.post(self.Host + "/UserService/registerUser", json=submit)
        return res.json()

    def createUser(self, username, password, mobile, email, fullname, ip, source, tel, nodeClusterId):
        submit = {
            "username": username,
            "password": password,
            "mobile": mobile,
            "email": email,
            "fullname": fullname,
            "remark": "AMEN-GoEdge-User创建的用户,不可删除,请通过AMEN-GoEdge-User删除,否则AMEN-GoEdge-User异常",
            "nodeClusterId": nodeClusterId,
            "tel": tel
        }
        res = self.post(self.Host + "/UserService/createUser", json=submit)
        if res is None:
            return None
        return res.json()

    def loginUser(self, Emysql: Sql.Sql, username: str, password: str):
        #  登陆服务官方没有开，自己写，数据库的密码就是md5(原始密码)
        # submit = {
        #     "username": username,
        #     "password": password,
        # }
        # # res = requests.post(self.Host + "/UserService/loginUser",json=submit)
        # res = self.post(self.Host + "/UserService/loginUser", json=submit)
        # # print(res.content.decode())
        # return res.json()
        # md = hashlib.md5(password.encode())

        userinfo = Emysql.fetch_where("edgeUsers", {
            "username": username,
            # "password": md.hexdigest(),
            # "serversEnabled":1,
            "state": 1
        })
        #  isOn字段无用
        #  state=0被删除
        #  serversEnabled=0被禁用
        if userinfo is not None:
            #  查找AccessKey
            userinfov2: dict = self.findAllEnabledUserAccessKeys(userinfo['id'])
            if userinfov2 is None:
                #  生成key
                keyinfo = self.createUserAccessKey(Emysql, userinfo['id'])
                if not keyinfo[0]:
                    #  生成失败
                    return None
                #  生成成功
                userinfov2 = {'uniqueId': keyinfo[1], 'secret': keyinfo[2]}
            elif userinfov2 == "0":
                #  异常
                return None
            # userinfov2 = json.loads(userinfov2)
            userinfov3 = {
                "uniqueId": userinfov2['uniqueId'],
                "secret": userinfov2['secret']
            }
            userinfo.update(userinfov3)
            return userinfo
        else:
            return None

    def createUserAccessKey(self, ESql: Sql.Sql, userid: int):
        #  理由为None，内部出错
        submit = {
            "userId": userid,
            "description": "AMEN-GoEdge-User创建的Key,不可删除,请通过AMEN-GoEdge-User删除,否则AMEN-GoEdge-User异常"
        }
        res = self.post(self.Host + "/UserAccessKeyService/createUserAccessKey", json=submit)
        if res is None:
            return [False, None]
        keyinfo = None
        try:
            if res.json()['code'] != 200:
                msg = "code为：{}".format(res.json()['code'])
                if "message" in res.json():
                    msg = res.json()['message']
                return [False, msg]
            keyId = res.json()['data']['userAccessKeyId']
            #  根据keyId查找，无此接口通过数据库查找
            keyinfo = ESql.fetch_where("edgeUserAccessKeys", {
                "id": keyId
            })
        except:
            return [False, None]
        if keyinfo is None:
            return [False, None]
        else:
            return [True, keyinfo['uniqueId'], keyinfo['secret']]

    def findAllEnabledUserAccessKeys(self, userid: int):
        submit = {
            "userId": userid,
        }
        res = self.post(self.Host + "/UserAccessKeyService/findAllEnabledUserAccessKeys", json=submit)
        try:
            if res is not None:
                if len(res.json()['data']['userAccessKeys']) == 0:
                    return None
                else:
                    return res.json()['data']['userAccessKeys'][0]
            else:
                return "0"
        except:
            return None

    def token_find_userid(self, ESql: Sql.Sql, UserToken: str):
        userinfo_token = ESql.fetch_where("edgeAPIAccessTokens", {
            "token": UserToken
        })
        if userinfo_token is None:
            return None
        return userinfo_token['userId']
