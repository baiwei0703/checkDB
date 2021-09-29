#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 注意：decimal 类型在查询时，需要手动转成字符，汉字需要decode
# 类似： CAST(amounts AS CHAR) amounts
# 字节类型转换字符串 str(bytes, encoding="utf-8")
'''
PooledDB的参数：
1. mincached，最少的空闲连接数，如果空闲连接数小于这个数，pool会创建一个新的连接
2. maxcached，最大的空闲连接数，如果空闲连接数大于这个数，pool会关闭空闲连接
3. maxconnections，最大的连接数，
4. blocking，当连接数达到最大的连接数时，在请求连接的时候，如果这个值是True，请求连接的程序会一直等待，直到当前连接数小于最大连接数，如果这个值是False，会报错，
5. maxshared 当连接数达到这个数，新请求的连接会分享已经分配出去的连接

在uwsgi中，每个http请求都会分发给一个进程，连接池中配置的连接数都是一个进程为单位的（即上面的最大连接数，都是在一个进程中的连接数），而如果业务中，一个http请求中需要的sql连接数不是很多的话（其实大多数都只需要创建一个连接），配置的连接数配置都不需要太大。
连接池对性能的提升表现在：
1.在程序创建连接的时候，可以从一个空闲的连接中获取，不需要重新初始化连接，提升获取连接的速度
2.关闭连接的时候，把连接放回连接池，而不是真正的关闭，所以可以减少频繁地打开和关闭连接
'''

import pymysql
import os
import configparser
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB


class Config(object):
    """
    # Config().get_content("user_information")

    配置文件里面的参数
    [notdbMysql]
    host = 192.168.1.101
    port = 3306
    user = root
    password = python123
    """

    def __init__(self, config_filename="db.cnf"):
        file_path = os.path.join(os.path.dirname(__file__), config_filename)
        self.cf = configparser.ConfigParser()
        self.cf.read(file_path)

    def get_sections(self):
        return self.cf.sections()

    def get_options(self, section):
        return self.cf.options(section)

    def get_content(self, section):
        result = {}
        for option in self.get_options(section):
            value = self.cf.get(section, option)
            result[option] = int(value) if value.isdigit() else value
        return result


class BasePymysqlPool(object):
    def __init__(self, host, port, user, password, db=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db
        self.conn = None
        self.cursor = None


class MyPymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self, conf_name=None):
        self.conf = Config().get_content(conf_name)
        super(MyPymysqlPool, self).__init__(**self.conf)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__get_conn()
        self._cursor = self._conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __get_conn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if MyPymysqlPool.__pool is None:
            __pool = PooledDB(creator=pymysql,
                              mincached=1,
                              maxcached=20,
                              host=self.db_host,
                              port=self.db_port,
                              user=self.user,
                              passwd=self.password,
                              db=self.db,
                              use_unicode=True,
                              charset="utf8",
                              cursorclass=DictCursor)
        return __pool.connection()

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def get_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: ret list(字典对象)/boolean 查询到的结果集
        """
        ret = False
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count:
            ret = self._cursor.fetchall()
        return ret

    def get_many(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: ret list/boolean 查询到的结果集
        """
        ret = False
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count:
            ret = self._cursor.fetchmany(num)
        return ret

    def get_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: ret list/boolean 查询到的结果集
        """
        ret = False
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count:
            ret = self._cursor.fetchone()
        return ret

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert_many(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, is_end=1):
        """
        @summary: 释放连接池资源
        """
        if is_end == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()

# if __name__ == '__main__':
# # #     mysql = MyPymysqlPool("db_info")
#     mysql = MyPymysqlPool("db_139")
# #
# #     # sqlAll = "select * from order_info;"
# #     # result = mysql.get_all(sqlAll)
# #     # print(result)
# #
# #     # sqlAll = "select * from order_info;"
# #     # result = mysql.get_many(sqlAll, 2)
# #     # print(result)
# #
# #     # result = mysql.get_one(sqlAll)
# #     # print(result)
# #
# #     # sql_insert = "insert into test (name) values(%s)"
# #     # vals = ('test1')
# #     # result = mysql.insert(sql_insert, vals)
# #
# #     # sql_insert = "insert into test (`name`) values(%s)"
# #     # vals = ('test6', 'test7')
# #     # result = mysql.insert_many(sql_insert, vals)
# #     # print(result)
# #
# #     # sql_update = "update test set `name` = %s where id = 2"
# #     # vals = 'test1'
# #     # result = mysql.update(sql_update, vals)
# #     # print(result)
# #
#
#     # 释放资源
#     mysql.dispose()
