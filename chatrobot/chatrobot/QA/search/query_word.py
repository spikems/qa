#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
query for chatterbot
input format:
    question:can be any string
output files:
    anwser: result from query
Usage:
    query.py -q <question> -w <way(edit_distance,tfidf)>
"""
import re
import os, sys
import pandas as pd
import traceback
import requests
import logging
import numpy as np
import json
#import synonyms
from optparse import OptionParser
from scipy import spatial

from hparams import create_hparams
from elasticsearch import Elasticsearch
from build_es_body import build_body
from ..preprocess.sent_vec import sent_vec
reload(sys)
sys.setdefaultencoding('utf-8')

es = Elasticsearch(["http://192.168.241.35:9200",
                    "http://192.168.241.46:9200",
                    "http://192.168.241.50:9201",
                    "http://192.168.241.47:9201"],
                   sniffer_timeout = 200, timeou = 100)

class Query(object):

    def __init__(self):
        pass

    def es_query(self, ):
        lables = ['must','should']#      

        for label in lables:
            print label
            body = build_body(self.Hpamas,label)
            result = self.deal_data(body)
            if result:
                return result

    def run(self, dic):
        self.Hpamas = create_hparams(json.dumps(dic))
        # self.__prepare(HPramas)
        response = self.es_query()
        return response

    def sort_sent(self,lresponse):
        return sorted(lresponse,key=lambda x:x['sim_score'],reverse=True)[0:10]

    def deal_data(self,body):
        question_vec = np.array(sent_vec(self.Hpamas.question))

        lresponse = []
        es_re = es.search(index="q2a", body=body, size=self.Hpamas.filter_size)
        if es_re['hits']['max_score']:
            res = es_re['hits']['hits']
            for line in res:
                line['_source']['body'] = body
                line['_source']['score'] = line['_score']
                line['_source']['sim_score'] = 1 - spatial.distance.cosine(question_vec, np.array(line['_source']['sent_vec']))
                lresponse.append(line['_source'])
        if len(lresponse)>0:
            return self.sort_sent(lresponse)
        else:
            return '对不起,你所问的我不知道,正在为你转人工'


if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    import logging.config

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info('task is start')
    # opts = load_option()
    # if opts.question is None or opts.way is None:
    #     print(__doc__)
    #     sys.exit(0)
    dic = {"question":"product油耗怎么样","product":["途观",],"attribute":["油耗"]}
    # HPramas = create_hparams(json.dumps(dic))
    ins = Query()
    ins.run(dic)
    response = ins.es_query()
    print response[0]['question']
