#encoding:utf-8
import os,sys
cur_path = os.path.dirname(os.path.abspath(__file__))
jieba_path = '%s/../' % cur_path
sys.path.insert(0, jieba_path)

import jieba
from jieba.norm import norm_cut, norm_seg
from jieba.norm import load_industrydict
import datetime
import random


class CutWord:

    def __init__(self):
        self.feat_words = []
        self.f_inner_dict = '%s/dict.txt' % os.path.dirname(os.path.abspath(__file__))
        self.l_inner_dict = []
        self.l_special_dict = []
        self.__load_dictionary()

    def __load_dictionary(self):
        with open(self.f_inner_dict, 'r') as fr:
            for line in fr:
                self.l_inner_dict.append(line)

    def __set_new_dic(self, feat_words):
        special_dict = []
        for line in feat_words:
            if line.split() == 1:
                line = '%s n' % line
            fs = line.split()
            line = "%s 5 %s\n" % (fs[0], fs[1])
            special_dict.append(line)

        f_special_dict = 'temp_dict/dict_%s_%s.txt' % (random.randint(0, 100000), str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        fw = open(f_special_dict, 'w')
        for line in self.l_inner_dict:
            fw.write(line)
        for line in special_dict:
            fw.write(line)
        fw.close()
        return f_special_dict

    def cut(self, sentence = '', special_words = [], industrys = []):
        '''
        :param special_words: ['美丽 a', '转发 v']
        :param industrys: 行业字典， 2汽车， 7美妆， 0 新词
        :return: 
        '''
        f_special_dict = self.f_inner_dict
        if special_words and f_special_dict:
            f_special_dict = self.__set_new_dic(special_words)
            if os.path.exists(f_special_dict):
                jieba.set_dictionary(f_special_dict)

        load_industrydict(industrys)
        print sentence
        words = norm_seg(sentence)

        if special_words and os.path.exists(f_special_dict) and self.f_inner_dict != f_special_dict:
            cmd = 'rm -rf %s' % f_special_dict
            os.system(cmd)
        return words

if __name__ == '__main__':
    #CutWord().cut()
    sentence = '我是认识石墨烯和凱特琳Chery东方之子'
    special_words = ['石墨烯 n', '凱特琳 n']
    industrys = [2]
    words = CutWord().cut(sentence = sentence, special_words = special_words, industrys = industrys)
    for word in words:
        print word.word , word.flag
           

