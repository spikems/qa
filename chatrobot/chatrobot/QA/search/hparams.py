#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
# import OptionParser
import os
import sys
from collections import namedtuple
import json

HParams = namedtuple(
    "HParams",
    [   "question",
        "brand",
        "brand_num",
        "product",
        "product_num",
        "attribute",
        "attribute_num",
        "component",
        "component_num",
        "qword",
        "qword_num",
        "evalue_word",
        "service",
        "filter_size",
        "is_contrast",
    ])


def check_type(word, wtype):
    if not isinstance(word, wtype):
        print '%s is not %stype ' % (word, wtype)
        sys.exit()


def check_params(outer_param):
    dic = json.loads(outer_param)
    if not dic.has_key("question"):
        print "has no key quesiton"
        sys.exit()
    if dic["question"] is None:
        print "question is null"
        sys.exit()
    check_type(dic.get("is_contrast", False), bool)
    for i in ['brand_num', 'product_num', 'component_num',
              'attribute_num', 'qword_num', 'filter_size']:
        check_type(dic.get(i, 80), int)
    return dic


def create_hparams(outer_param):
    Prameter = check_params(outer_param)
    print Prameter["question"]
    print Prameter
    return HParams(
        question=str(Prameter["question"].encode('utf-8', 'ignore')).lower(),
        brand=Prameter.get("brand", ""),
        brand_num=Prameter.get("brand_num", 0),
        product=Prameter.get("product", ""),
        product_num = Prameter.get("product_num", 0),
        attribute=Prameter.get("attribute", ""),
        attribute_num=Prameter.get("attribute_num", 0),
        component=Prameter.get("component", ""),
        component_num=Prameter.get("component_num", 0),
        qword=Prameter.get("qword", ""),
        qword_num=Prameter.get("qword_num", 0),
        service=Prameter.get("service",""),
        evalue_word=Prameter.get("evaluation",""),
        filter_size=Prameter.get("filter_size", 30),
        is_contrast=Prameter.get("is_contrast", False),
    )
