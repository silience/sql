
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

