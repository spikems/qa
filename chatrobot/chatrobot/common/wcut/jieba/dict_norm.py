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

    def __init__(self, special_words = [], industrys = []):
        self.f_inner_dict = '%s/dict.txt' % os.path.dirname(os.path.abspath(__file__))
        self.d_special_words = special_words
        self.industrys = industrys

        self.f_special_dict = self.f_inner_dict
        self.__load_dictionary()

    def __load_dictionary(self):

        load_industrydict(self.industrys)

        if len(self.d_special_words) == 0:
            return

        special_dict = []
        with open(self.f_inner_dict, 'r') as fr:
            for line in fr:
                special_dict.append(line)

        for line in self.d_special_words:
            fs = line.strip().split()
            if len(fs) == 1:
                fs.append('n')
            line = "%s 10000 %s\n" % (fs[0], fs[1])
            special_dict.append(line)

        self.f_special_dict = '%s/temp_dict/dict_%s_%s.txt' % (cur_path, random.randint(0, 100000), str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        fw = open(self.f_special_dict, 'w')
        for line in special_dict:
            fw.write(line)
        fw.close()

        if os.path.exists(self.f_special_dict):
            jieba.set_dictionary(self.f_special_dict)


    def cut_seg(self, sentence = ''):
        '''
        :param special_words: ['美丽 a', '转发 v']
        :param industrys: 行业字典， 2汽车， 7美妆， 0 新词
        :return: 
        '''
        words = norm_seg(sentence)
        return words

    def release(self):
        if self.f_inner_dict != self.f_special_dict and not len(self.d_special_words):
            cmd = 'rm -rf %s' % self.f_special_dict
            os.system(cmd)

if __name__ == '__main__':
    #CutWord().cut()
    sentence = '我是认识石墨烯和凱特琳Chery东方之子'
    special_words = ['石墨烯 n', '凱特琳 n']
    industrys = [2]
    cw = CutWord( special_words = special_words, industrys = industrys)
    words = cw.cut_seg(sentence = sentence)
    for word in words:
        print word.word , word.flag
    cw.release()
    
           

