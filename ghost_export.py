# -*- coding:utf-8 -*-
#
# ghost_export 是为Ghost 导出博客文件的一个python小工具,
# 默认把ghost_export.py放在Ghost的根目录下,它就可以顺利工作了. 
# 导出 的目录为 post
# created by Wasabi 2013-10-18
#
# Version 0.1
#


import sqlite3
import os,sys

# 通常只要配置了ghost_path就可以了.


# ghost 目录 
ghost_path = './'
# ghost_path = 'E:/webroot/demo/Ghost-0.3.2/'

# db 目录
db_path = ghost_path + 'content/data/ghost-dev.db'

# 输出目录
export_path = ghost_path +'post/'

suffix = '.md'

# 写入文件
def create_file(filename, content):
    f = open(export_path+filename+suffix, 'w')
    f.write(content)
    f.close()
    
# 主程序 
def main():
    # 如果不存在,就创建post 目录 
    if not os.path.exists(ghost_path + "post"):
        os.mkdir(ghost_path+"post")
    
    print db_path
    conn = sqlite3.connect(db_path)
    
    c = conn.cursor()
    
    c.execute("SELECT * FROM posts limit 1000")
    
    res = c.fetchall()
    
    str = ''
    for f in res:
        create_file(f[3],f[4])

        str += "* [%s](%s)\n" % (f[2],f[3]+suffix)
        
#     print str
    
    create_file('README',str)
    conn.close()


    
reload(sys)                         # 2
sys.setdefaultencoding('utf-8')     # 3
# print sys.getdefaultencoding()

main()
print "export file to %s" % export_path
print "Finish!";    
    


# 游标对象有以下的操作：
# execute()--执行sql语句   
# executemany--执行多条sql语句   
# close()--关闭游标   
# fetchone()--从结果中取一条记录，并将游标指向下一条记录   
# fetchmany()--从结果中取多条记录   
# fetchall()--从结果中取出所有记录   
# scroll()--游标滚动  