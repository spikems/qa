#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
import pymysql
import traceback



conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='dm_base',
                       charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    cur.execute('select name from ip')
    conn.commit()
    for line in cur.fetchall():
        word = line['name'].strip().encode('utf-8', 'ignore')
        cur.execute('insert into newwords(word) values(%s)', (word,))
        conn.commit()
except:
    traceback.print_exc()

conn.close()
