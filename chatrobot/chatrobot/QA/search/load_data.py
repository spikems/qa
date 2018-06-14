#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
import data into ES
"""
import sys
from elasticsearch import Elasticsearch
import datetime
from elasticsearch import helpers
#from chatterbot import ChatBot
#from chatterbot.trainers import ChatterBotCorpusTrainer
#from chatterbot.trainers import ListTrainer
import hashlib
import pandas as pd
import traceback
import logging
import re
reload(sys)
sys.setdefaultencoding('utf-8')
#chatbot = ChatBot("Norman")
#chatbot.set_trainer(ListTrainer)
#bot = ChatBot(
#    'Norman',
#    storage_adapter='chatterbot.storage.SQLStorageAdapter',
#    trainer='chatterbot.trainers.ListTrainer',
#    database='../model/database.sqlite3'
#)

es = Elasticsearch(["http://192.168.241.47:9201", "http://192.168.241.46:9200", "192.168.241.50:9201"],
                   sniffer_timeout=60)

def load_data(datafile):
    """
    datafile : a csv file include column name (Q,A,title,class)
    convert:title ->title,class->brand,product,A->anwser,Q->text
    :return:
    dict :{title,text,product,brand,anwswe,}
    """
    ins = Saver()
    df = pd.read_excel(datafile,encoding='GBK')
    # log_brand  = open('../data/brand_product','w')
    num = -1
    for line in df['title']:
        num += 1
        tmp_dict = {}
        if isinstance(line,(float,int)):
            line = ''
        if  not isinstance(df['Q'][num],(float,int)):
            qline = df['Q'][num]
        else:
            qline = ''

        if  not isinstance(df['A'][num],(float,int)):
            aline = df['A'][num]
        else:
            aline = ''
        aline = re.split(r'(发表.*楼)',aline)[-1]
        brand = df['class'][num].split('>')[0].strip()
        product = df['class'][num].split('>')[1].strip()
        tmp_dict['title'] = line.lower()
        tmp_dict['text'] = qline.lower()
        tmp_dict['anwser'] = aline.lower()
        tmp_dict['brand'] = brand.lower()
        tmp_dict['product'] = product.lower()
        ins.pass_data(tmp_dict)
        # log_brand.write('%s\t%s\n'%(brand,product))
        # print ('line',line)
        # print ('qline',qline)
        # print('aline',aline)
        # print (brand,product)
        # exit()
        # return tmp_dict
        # except:
        #     traceback.print_exc()
        #     exit()
        #     logging.info('%s\t%s'%(aline,qline))
        #     continue
    # log_brand.close()

class Saver(object):
    def __init__(self, cache_size=1):
        self.actions = []
        self._cache_size = cache_size

    def pass_data(self,dic,es=es, my_index="q2a", my_type="q2a"):
        # read data
        """
        load to es
        :param dic:
        :param es:
        :param my_index:
        :param my_type:
        :return:
        """
        md5 = hashlib.md5()
        userid = dic['question']
        md5.update(userid)
        doc = {
            # delete,index,create
            # "_op_type": 'update',
            "_index": my_index,
            "_type": my_type,
            "_id": md5.hexdigest(),
            "_source": {
                'question': dic.get('question', ""),
                'include_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'brand': dic.get('brand', ""),
                'industry': dic.get('industry', "汽车"),
                'product': dic.get('product', ""),
                'anwser':dic.get('answer',""),
                'component':dic.get('component',""),
                'attribute':dic.get('attribute',""),
                'evalue_word':dic.get('evaluation',""),
                'service':dic.get('service',""),
                'qword':dic.get('qword',""),
                'sent_vec':dic.get('sent_vec',""),
                'kword_vec':dic.get('keyword_vec',"")
            }
        }
        # 单条写入的方式(
        # es.index(index=my_index,doc_type=my_type,body=doc)
        # 批量处理
        self.actions.append(doc)
        if len(self.actions) >= self._cache_size:
            self.flush()

    def flush(self):
        helpers.bulk(es, self.actions)
        self.actions = []

    def pass_chatbot(self,dic):
        """
        load to chatrbot
        :param dic:
        :return:
        """
        question = dic.get('title','') + dic.get('anwser','')
        anwser = dic.get('anwser','')
 #       bot.train([
 #           question, anwser
 #       ])


if __name__ == '__main__':
    #load_data('../data/all_data.xlsx')
    ins = Saver()
    dic = {"question":"求教大众的落地价格是多少","anwser":"15万","product":["大众"],\
           "qword":"多少","attribute":["价格","落地"],"industry":"汽车"}
    ins.pass_data(dic)

