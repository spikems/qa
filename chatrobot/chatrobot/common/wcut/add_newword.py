#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
update neword.dict from table
"""
import os
import sys
import pymysql
import datetime
import logging
import traceback
import pdb
reload(sys)
from jieba import suggest_freq
sys.setdefaultencoding('utf-8')

conn = pymysql.connect(host='192.168.241.45', port=3306, user='oopin', passwd='OOpin2007Group', db='dm_base',
                       charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)

all_sex = ('n','nr','nz','ag','ad','a','b','c','dg','d','e','f','g','h','i','j','l','m','ns','p','q','r','s','t','u','vt','vn'
	  'w','y','z') 


class updateNewword(object):
    def __init__(self):
        pass

    def read_newword(self):
        start_time = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d 00:00:00')
        end_time = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')
        try:
            sql = "select word,word_sex from new_words where %s < update_time < %s and word_sex  in %s"
            logger.info(sql % (start_time, end_time,all_sex))
            cur.execute(sql, (start_time, end_time,all_sex))
            conn.commit()
            dnewword = cur.fetchall()
            logger.info('how many  newword :%s ' % len(dnewword))
            # pdb.set_trace()
            return dnewword
        except:
            traceback.print_exc()
            return False
        finally:
            conn.close()

    def remove_dup(self,dirPath):
        existWord = set()
        for root,dir,files in os.walk(dirPath):
            for file in files:
                logger.info('filename :%s '%file)
                filepath = os.path.join(root,file)
                with open(filepath,'rb') as inf:
                    for line in inf:
                        word = line.split(' ')[0].encode('utf-8','ignore')
                        existWord.add(word)
        logger.info('len(existWord) = %s'%len(existWord))
        return existWord

    def writer_newword(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        existWord = self.remove_dup('./jieba/industrydict/')
        infile = './jieba/industrydict/newword.dict'
        if os.path.isfile(infile):
            writer = open(infile, 'a+')
        else:
            writer = open(infile, 'wb')
        lword = self.read_newword()

        num = 0
        if lword:
            for sub in lword:
                if sub['word'] :
                    word = sub['word'].encode('utf-8', 'ignore').replace(' ','')
                    sex = sub['word_sex'].encode('utf-8', 'ignore').strip()
                    if word not in existWord and sex:
                        freq = suggest_freq(word,True) if suggest_freq(word,True) else 1
                        num += 1
                        writer.write('%s %s %s\n' % (word,freq,sex))
        logger.info('%s words have been writted in infile' % num)
        writer.close()
        logger.info('write newword task is finish')

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    import logging.config

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info('task is start')

    ins = updateNewword()
    ins.writer_newword()
