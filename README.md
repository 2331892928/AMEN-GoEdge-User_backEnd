# AMEN-GoEdge-User后端

## 这是什么项目？
这是 GoEdge CDN的用户端

## 为什么要创作,GoEdge没有用户端吗？
有，但是是商业版才可用，也就是需要💴

## 有哪些功能
       1.注册  
       2.登录  
       3.验证码  
       4.网站管理  
       5.添加/删除网站  
       6.https设置(http2/强制https/https证书/hsts/开关http|s/ocps/tls)  
       7.源站管理(支持端口/支持域名/支持ip/支持https/支持https证书/添加/删除)  
       8.证书管理(一键绑定/添加/删除)  

## 后续会增加功能吗？
会的，会逐渐加上：waf规则自定义/webp/缓存/防盗链/Websocket/地区限制/URL跳转/网站统计(流量/请求数)/拦截日志

## 只有后端，没有前端吗？
有的，项目在 https://github.com/2331892928/AMEN-GoEdge-User_frontEnd

## 如何升级？
后期会给升级方法，基本覆盖即可

## 如何安装后端？
### 导入sql
将此项目根目录下的 edge_code.sql导入即可
### GoEdgeAdmin设置
1.系统设置->高级设置->API节点->主节点详情->修改节点->更多选项->是否开启HTTP API端口(开启)->HTTP API监听端口(自行设置)->启用当前节点(打开)  
2.系统用户->随便一个->详情->accesskeys—>按需创建添加，记住即可后边用
### 填写配置文件
没有配置文件？  
将项目运行一遍，即可在项目根目录下的Config文件夹里  
配置文件名：Config.json  
配置解释：
```json
{
    "Config": {
        "whetherVerificationCodeIsEnabl": false    # 是否开启腾讯验证码，验证码界面有：
      # 注册/登录/发送验证码。关闭后只有以下生效：发送验证码
    },
    "mysql": {# 本项目sql配置
        "host": "127.0.0.1", # mysql主机名
        "port": 3306,# mysql端口
        "user": "goedge",# mysql用户
        "password": "goedge",# mysql密码
        "database": "goedge"# mysql数据库
    },
    "EdgeAdmin_mysql": { # GoEdgeAdmin的数据库
        "host": "",
        "port": 8001,
        "user": "",
        "password": "",
        "database": ""
    },
    "Verification": {  #  发送验证码配置，邮箱配置
        "type": 0,
        "host": "",  # 邮箱主机名
        "port": 465,  #邮箱端口
        "ssl": true,  #邮箱是否启用ssl
        "user": "", #邮箱用户名
        "password": "", #邮箱密码
        "title": "AMEN-GoEdge-User", #邮箱主题/网站主题
        "frequentTime": 60  # 验证码多久失效/内频繁 秒单位，如60秒：
#  60秒内生效，60秒内不可再次发送否则频繁
    },
    "API": { # 安装第二步GoEdgeAdmin设置的内容 nodeClusterId为注册用户默认绑定的集群id
        "HOST": "",
        "AccessKey ID": "",
        "AccessKey Key": "",
        "nodeClusterId": 1
    },
      # 以下为系统运行临时配置，不可动  
    "Token": "",
    "expiresAt": 0,
    "adminId": 2
}
```
### 宝塔安装示例
> 什么是宝塔？bt.cn  
> 软件商店搜索 python项目管理器 进行安装  
> 软件商店搜索 进程守护 进行安装  
> 打开 python项目管理器  
> 添加项目  
> 版本管理，安装python3.7.9等待  
> 添加项目 框架python  
> 启动方式 gunicorn  
> 项目路径 不解释  
> 日志目录 不解释  
> 启动文件 选择项目路径下的main.py  
> 端口随意  
> 权限看你的项目文件夹权限不解释  
> 安装模块依赖勾上，守护进程开机启动看自己  
> 确定 等待  
> 启动完毕，关闭项目  
> 配置  
> 修改worker_class节点为 'uvicorn.workers.UvicornWorker'  
> 保存 运行  
> 产生配置文件 关闭项目  
> 修改配置文件  
> 启动项目，启动成功，若失败，请提交issues进行咨询或查看日志自行研究  