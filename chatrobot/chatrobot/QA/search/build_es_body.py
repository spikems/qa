#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

def body_add(body,group):
    for field in group:
        body["query"]["bool"][field[0]].append({field[1]: {field[2]: field[3]}})

def build_body(HParams,label = 'must'):

    question = HParams.question
    brand = HParams.brand
    brand_num = HParams.brand_num
    product = HParams.product
    product_num = HParams.product_num
    attribute = HParams.attribute
    attribute_num = HParams.attribute_num
    component = HParams.component
    component_num = HParams.component_num
    qword = HParams.qword
    qword_num = HParams.qword_num
    evalue_word = HParams.evalue_word
    service = HParams.service
    is_contrast = HParams.is_contrast

    body = {"query": {"bool": {"must": [{"multi_match": {
        "fields": ["question"],
        "query": question}}],
        "should": [],"boost":3}}}
    # if product:
    #     body["query"]["bool"]["must"].append({"terms": {"product": product}})
    # if brand:
    #     body["query"]["bool"]["must"].append({"terms": {"brand": brand}})
    if is_contrast:
        body_add(body,[('must','term','is_contrast',is_contrast)])

    if label == 'must':
        termslist = []
        if attribute:
            termslist.append(('must','terms','attribute',attribute))
        if component:
            termslist.append(('must','terms','component',component))
        if qword:
            termslist.append(('must','term','qword',qword))
        if evalue_word:
            termslist.append(('must','terms','evalue_word',evalue_word))
        if service:
            termslist.append(('must','terms','service',service))
        body_add(body,termslist)

    if label == 'extra_evalue':
        termslist = []
        if attribute:
            termslist.append(('must','terms','attribute',attribute))
        if component:
            termslist.append(('must','terms','component',component))
        if qword:
            termslist.append(('must','term','qword',qword))
        if evalue_word:
            termslist.append(('should','terms','evalue_word',evalue_word))
        if service:
            termslist.append(('must','terms','service',service))
        body_add(body,termslist)

    if label == 'should':
        if attribute:
            body["query"]["bool"]["should"].append({"terms": {"attribute": attribute}})
        if component:
            body["query"]["bool"]["should"].append({"terms": {"component": component}})
        if qword:
            body["query"]["bool"]["should"].append({"term": {"qword": qword}})
        if evalue_word:
            body["query"]["bool"]["should"].append({"terms": {"evalue_word": evalue_word}})
        if service:
            body["query"]["bool"]["should"].append({"terms": {"service": service}})

    return body