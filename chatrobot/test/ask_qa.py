#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
example for ask question
"""
import requests

def ask_question(question):
    """
    :param question: a question about  automobile type :string
    :return: list include more dict
    """
    url = 'http://192.168.241.6:10020/answer/?question=%s'%question
    r = requests.get(url)
    print r.json()

if __name__ == '__main__':
    ask_question(question='奔驰车耗油么')

