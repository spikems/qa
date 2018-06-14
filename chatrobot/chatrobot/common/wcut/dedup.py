#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import sys

exist_word = set()
dedup = set()

with open(sys.argv[1], 'rb') as inf:
    for line in inf:
        exist_word.add(line.split()[0])

with open(sys.argv[2], 'rb') as inf:
    for line in inf:
        word = line.split()[0]
        if word not in exist_word:
            dedup.add(line.strip())

with open(sys.argv[2], 'wb') as inf:
    for line in dedup:
        inf.write('%s\n' % line)