#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from .preprocess import  PreProcess
from .model import ModelDeal
def classify(question):


    #1. preprocess
    o_pre = PreProcess()
    s_feats = o_pre.run(question)

    #model info deal
    o_md = ModelDeal()
    ret = o_md.run(question)

    #load model
    return ret
     
if __name__ == '__main__':
    classify(question='大众和奔驰哪个好')