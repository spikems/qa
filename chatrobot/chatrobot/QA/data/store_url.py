#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
import sys, time
import time
import requests
import urllib

'''
    python access.py 3 intention

'''
URL = 'http://brand.yoka.com/cosmetics/all/product_0_0_0_3.htm?istopcatalog='
def visit(url):
    fr = urllib.urlopen(url)
    res = fr.read()
    fr.close()
    return res

for line in sys.stdin:
    print line.strip()
    fs = line.strip().split('\t')
    if len(fs) < 4:
        continue
    brandinfo = fs[0]
    question = fs[1]
    context = fs[2]
    answer = fs[3]
    url = 'http://112.253.2.41:10010/storeqa/?answer=%s&brandinfo=%s&question=%s&context=%s' % (answer, brandinfo, question, context)
    print url
    visit(url)
