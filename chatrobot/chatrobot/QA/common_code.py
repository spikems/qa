#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
def replace_product(dic):
    """
    replace all brand and product
    """
    dic['question'] = dic['question'].encode('utf-8','ignore')
    for word in dic['brand']:
        dic['question'] = dic['question'].replace(word,'brand')
    for word in dic['product']:
        dic['question'] = dic['question'].replace(word,'product')
    return dic

def keywords(dic):
    """
    communate all keywords
    """
    words = set()
    if dic['qword'] :
        words.add(dic['qword'])
    words = words|set(dic['component'])|set(dic['attribute'])|set(dic['evaluation'])|set(dic['service'])
    try:
        strword =' '.join(words)
    except:
        print 'words:', words
    return  ' '.join(words)


def compute_length(dic):
    fields = ['attribute', 'brand', 'component', 'product']
    for field in fields:
        field_num = '%s_num' % (field)
        dic[field_num] = len(dic[field])