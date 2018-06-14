#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import numpy as np
from ast import literal_eval
from scipy import spatial
from proprecess.sent_vec import sent_vec

class SortDoc(object):
    def __init__(self):
        pass

    def sort(self,way,lresult):
        if way == 'sent_vec':
            lresult = sorted(lresult,key=lambda x:x[3],reverse=True)
            return lresult

    def prepare(self,raw_sent,data):
        lresult = []  #(quesiton,anwser,score,sim_score,kword_score)
        s1_afv = sent_vec(raw_sent)
        for i in data:
            sub_cell = []
            sub_cell.append(i['question'])
            sub_cell.append(i['anwser'])
            sub_cell.append(str(round(i['score'], 2)))
            s2_afv = np.array(literal_eval(i['sent_vec']))
            sim = 1 - spatial.distance.cosine(s1_afv, s2_afv)
            sub_cell.append(sim)
            lresult.append(sub_cell)
        return lresult

if __name__ == '__main__':
    pass

















