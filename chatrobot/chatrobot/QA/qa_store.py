#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
store data into ES
"""
# from  question_classify.classify import classify
from  preprocess.preprocess import Preprocess
from .search.query_word import Query
from .search.load_data import Saver
from .keyword.QA_Extract import NewQAExtractWord
from chatrobot.common.util import utf_string
from preprocess.sent_vec import sent_vec
from common_code import keywords,replace_product,compute_length


def store(brandinfo, question, context, answer):

    brandinfo = utf_string(brandinfo).lower().split('>')
    question = utf_string(question).lower()
    context = utf_string(context).lower()
    answer = utf_string(answer).lower()
    # print brandinfo
    # print question
    # print 'answer',answer


    #1. preprocess
    rule, s_new_question = Preprocess().run(question, context)
    if not rule:
        s_answer = '该问题不规范，该问题不规范'
        print s_answer
        return s_answer
    # print 's_new_question:', s_new_question

    #2. question classify
    question_type = 0 #classify(s_new_question)

    # s_new_question = '%s<space>%s' % (brandinfo, s_new_question)
    #3. keyword extract
    o_extract = NewQAExtractWord()
    dic = o_extract.extract_master(s_new_question, question_type)
    dic["answer"] = answer

    #define product and brand
    if brandinfo[0] not in dic['brand']:
        dic['brand'].append(brandinfo[0])
    if brandinfo[0] not in dic['product']:
        dic['product'].append(brandinfo[1])

    #4 replace brand and product use special symbol
    dic = replace_product(dic)

    #5 sentvec
    dic['sent_vec'] = sent_vec(dic['question'])
    #6 keywords sentvec
    kwords = keywords(dic)
    if kwords:  # if no keywords
        dic['kword_vec'] = sent_vec(kwords)

    ins = Saver()
    ins.pass_data(dic)
    print 'successful'
    # print  dic['question']
if __name__ == '__main__':
    ss = store(brandinfo='大众>途观',question='大众途观提车注意什么',answer='提车注意带钱')






 
