import traceback

import pymysql
from pymysql import cursors


class Sql:
    def __init__(self, host, port, user, password, database):
        # 链接服务端
        try:
            self.connect = pymysql.connect(
                host=host,  # MySQL服务端的IP地址
                port=port,  # MySQL默认PORT地址(端口号)
                user=user,  # 用户名
                password=password,  # 密码,也可以简写为passwd
                database=database,  # 库名称,也可以简写为db
                charset='utf8',  # 字符编码
                cursorclass=cursors.DictCursor
            )
        except:
            self.connect = None
        if self.connect is None:
            self.cursor = None
        else:
            self.cursor = self.connect.cursor()

    def fj(self, args: dict):
        #  分解
        keys = ""
        values = ""
        for i in args:
            #  分解Key
            if keys == "":
                keys = "(`" + i + "`"
            else:
                keys = keys + ",`" + i + "`"
            #  分解value
            if values == "":
                values = "(" + str(args[i])
            else:
                if isinstance(args[i], int):
                    values = values + "," + str(args[i])
                elif isinstance(args[i], float):
                    values = values + "," + str(args[i])
                elif isinstance(args[i], str):
                    values = values + ",'" + args[i] + "'"
                else:
                    return None
        if keys != "":
            keys = keys + ")"
        if values != "":
            values = values + ")"
        return [keys, values]

    def fj_where(self, args: dict, separator: str = "and"):
        prepare = ""
        value = ""
        for i in args:
            if isinstance(args[i], int):
                value = str(args[i])
            elif isinstance(args[i], float):
                values = str(args[i])
            elif isinstance(args[i], str):
                value = "'" + args[i] + "'"
            else:
                return None
            if value == "":
                return None
            if prepare == "":
                prepare = "`" + i + "`" + "=" + value
            else:
                prepare = prepare + " " + separator + " `" + i + "`" + "=" + value
        return prepare

    def query(self, sql: str):
        try:
            affect_rows = self.cursor.execute(sql)
            res = self.cursor.fetchall()  # 获取所有数据
            return res
        except:
            return None

    def execute(self, sql: str):
        # self.connect.query(sql)
        try:
            return self.cursor.execute(sql)
        except:
            # traceback.print_exc()
            return None

    def fetchall(self, tableName: str):
        sql = "select * from `{}`".format(tableName)
        return self.query(sql)

    def fetchall_where(self, tableName: str, args, separator: str = "and", additionalContent: str = None):
        prepare = self.fj_where(args, separator)
        sql = """select * from `{}` where {}""".format(tableName, prepare)
        if additionalContent is not None:
            sql = sql + " " + additionalContent
        return self.query(sql)

    def fetch_where(self, tableName: str, args, separator: str = "and", additionalContent: str = None):
        prepare = self.fj_where(args, separator)
        sql = """select * from `{}` where {}""".format(tableName, prepare)
        if additionalContent is not None:
            sql = sql + " " + additionalContent
        res = self.query(sql)
        if res is None or len(res) == 0:
            return None
        return res[0]

    def fetch(self, tableName: str):
        sql = "select * from `{}`".format(tableName)
        res = self.query(sql)
        if res is None or len(res) == 0:
            return None
        return res[0]

    def insert(self, tableName: str, args: dict):
        res = self.fj(args)
        keys = res[0]
        values = res[1]
        sql = """insert into `{}` {} values {}""".format(tableName, keys, values)
        affect_rows = self.execute(sql)
        if affect_rows is None:
            return False
        else:
            return True

    def delete(self, tableName: str, args: dict, separator: str = "and"):
        prepare = self.fj_where(args, separator)
        sql = """delete from `{}` where {}""".format(tableName, prepare)
        affect_rows = self.execute(sql)
        if affect_rows is None:
            return False
        else:
            return True
