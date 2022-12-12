import re
import time

from email.header import Header
from email.mime.text import MIMEText


import Utils
from fastapi import APIRouter, Path, Depends, Body
import smtplib

from Utils.tencent import Tencent

app = APIRouter(prefix="/Verification", tags=['验证服务'])


@app.post("/getcode")
async def getcode(number: str = Body(description='必须正确的邮箱，且必填'),
                  #  注册必须滑块，不可关闭
                  ticket: str = Body(),
                  randstr: str = Body(),
                  commons: dict = Depends(Utils.init)):
    # if type != 0 and type != 1:
    #     return Utils.message(201)
    # if type == 1:
    #     return Utils.message(202)

    # 用户名用手机或邮箱
    ret = re.match('^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$', number)
    type = 0  # 0是邮箱 1是手机
    if not ret:
        ret = re.match(r'([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)', number)
        if not ret:
            return Utils.message(395)
        else:
            type = 0
    else:
        type = 1
    if type == 1:
        return Utils.message(202)
    #  参数正确，开始滑块

    #  验证腾讯滑块验证码
    T = Tencent()
    flag = T.check_ticket(ticket, randstr)
    if flag == -1:
        return Utils.message(394)
    if flag == 0:
        return Utils.message(396)
    # 滑块结束

    #  查询数据库寻找title,暂时查询不到，用配置文件替代
    config = commons[0]
    Verification = config['Verification']
    mysql = config['mysql']
    host = Verification['host']
    port = Verification['port']
    uer_name = Verification['user']
    password = Verification['password']
    #  写入验证码
    yzm = Utils.generate_random_str(6)
    # VSql = Sql.Sql(mysql['host'], mysql['port'], mysql['user'], mysql['password'], mysql['database'])
    VSql = commons[1]
    if VSql is None:
        return Utils.message(401)
    millis = int(round(time.time() * 1000))
    toBeWritten = {
        "type": 0,
        "number": number,
        "code": yzm,
        "timeStamp": str(millis)
    }
    #  先查询是否频繁
    code_db = VSql.fetch_where("edge_code", {
        "number": number
    }, additionalContent="order by `timeStamp` desc")
    if code_db is not None:
        if millis - int(code_db['timeStamp']) < Verification['frequentTime'] * 1000:
            return Utils.message(398)

    flag = VSql.insert("edge_code", toBeWritten)
    if not flag:
        return Utils.message(4012)
    msg = "标题不是验证码。\n您正在注册 {} 的验证码，验证码为：{}".format(Verification['title'], yzm)
    msg = MIMEText(msg, 'plain', 'utf-8')
    # 放入邮件主题 随机标题，防止拦截，特别是qq邮箱
    msg['Subject'] = Header("{}注册验证码 {}".format(Verification['title'], Utils.generate_random_str(6)), 'utf-8')

    # 放入发件人
    msg['From'] = uer_name

    try:
        '''2、创建 SMTP 对象
        SMTP 协议是由源服务器到目的地服务器传送邮件的一组规则。(可简单理解为：我们需要通过SMTP指定一个服务器，这样才能把邮件送到另一个服务器)'''

        if Verification['ssl']:
            smtpObj = smtplib.SMTP_SSL(host, port)
        else:
            smtpObj = smtplib.SMTP(host, port)
        '''3、连接（connect）指定服务器'''
        smtpObj.connect(host, port)
        '''4、登录，需要：登录邮箱和授权码'''
        smtpObj.login(uer_name, password)
        '''5、发邮件。
        参数：发件人，收件人和邮件内容
        msg.as_string()是一个字符串类型：as_string()是将发送的信息msg变为字符串类型。
        '''
        smtpObj.sendmail(uer_name, number, msg.as_string())
        '''6、退出'''
        smtpObj.quit()
    except:
        # traceback.print_exc()
        #  邮箱发送失败。删除记录
        VSql.delete("edge_code", toBeWritten)
        return Utils.message(399)
    return Utils.message(200)

