#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
1.test suggest_freq
2.test load industry_dict
3.test special word (If the word contains spaces, add to userword / specialword )
industry_dict = {2:"car_dict",7:"makeup.dict"}

"""
from jieba import suggest_freq
from jieba.norm import norm_seg,load_industrydict
#print suggest_freq('小黑瓶',True)

#test 2
testword = ['长安欧尚',"睿骋cc","行动力","蓝水粉水小黑瓶"]
load_industrydict([2,7])
for i in testword :
    for word in norm_seg(i):
        print word.word,word.flag



