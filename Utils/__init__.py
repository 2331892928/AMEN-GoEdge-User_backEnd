import json
import os
import random
import shutil
import time

import API
import ErrCode
import Sql


def read_config():
    """"读取配置"""
    #  检查配置文件是否存在，不存在创建一个
    if not os.path.exists('./Config/Config.json'):
        shutil.copy('./Config/Config_initialization.json', './Config/Config.json')
    with open("Config/Config.json") as json_file:
        config = json.load(json_file)
    return config


def update_config(config):
    """"更新配置"""
    with open("Config/Config.json", 'w') as json_file:
        json.dump(config, json_file, indent=4)
    return None


def verify_token():
    # 查询token是否过期
    config = read_config()
    api = config['API']
    GoEdge_Api = API.Api(api['HOST'], api['AccessKey ID'], api['AccessKey Key'])
    if config['Token'] == "" or config['Token'] is None:
        #  生成Token
        token = GoEdge_Api.getToken()
        if token is not None:
            token = {
                "Token": token[0],
                "expiresAt": token[1]
            }

        else:
            token = {
                "Token": "",
                "expiresAt": 0
            }
        config = read_config()
        config.update(token)
        update_config(config)
    #  是否过期
    #  给两分钟宽限期
    if config['expiresAt'] - 120 < time.time():
        token = GoEdge_Api.getToken()
        if token is not None:
            token = {
                "Token": token[0],
                "expiresAt": token[1]
            }

        else:
            token = {
                "Token": "",
                "expiresAt": 0
            }
        config = read_config()
        config.update(token)
        update_config(config)


async def init():
    """读取配置文件，连接数据库等初始化操作"""
    #  连接数据库
    config = read_config()
    mysql = config['mysql']
    Emysql = config['EdgeAdmin_mysql']
    VSql = Sql.Sql(mysql['host'], mysql['port'], mysql['user'], mysql['password'], mysql['database'])
    ESql = Sql.Sql(Emysql['host'], Emysql['port'], Emysql['user'], Emysql['password'], Emysql['database'])
    return [config, VSql, ESql]


def generate_random_str(randomlength=16):
    """
  生成一个指定长度的随机字符串
  """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def message(code: int, data=None, message: str = "unknown"):
    """返回json，message只有400code或ErrCode没有相应的时候才有用"""
    if data is None:
        data = {}
    if code == 400 or code == 389:
        msg = message
    else:
        msg = ErrCode.ErrCode[str(code)]
    res = {
        "code": code,
        "data": data,
        "message": msg
    }
    return res
