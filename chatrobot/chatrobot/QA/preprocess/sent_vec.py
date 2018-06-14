#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import requests


def sent_vec(sent,is_seg=True):
    url = 'http://112.253.2.39:1107/sentvec/?sent=%s&is_seg=%s' % (sent,is_seg)
    r = requests.get(url)
    return r.json()


if __name__ == '__main__':
    sent_vec('大众车真的很好')