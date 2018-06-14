#encoding:utf-8
import sys

for line in sys.stdin:
    fs = line.strip().split('\t')
    context = fs[1].strip()
    answer = fs[3].strip()
    question = fs[4].strip()
    brands = fs[0].strip().split('>')
    #out = '%s\t%s\t%s\t%s\t%s' % (brands[0].strip(), brands[1].strip(), question, context, answer)
    out = '%s%s\t%s\t%s\t%s' % (brands[0].strip(), brands[1].strip(), question, context, answer)
    print out
