#encoding:utf-8
import sys
import os
import esm

class PreProcess:
   
    def __init__(self):
        
        self.s_feat_dir = '%s/feature' % os.path.dirname(os.path.abspath(__file__))
        self.d_sep = {}
        self.e_brand = esm.Index()
        self.question = ''
        self.__load_feat()

    def __load_feat(self):
        s_separate_path = '%s/separate_inquire.info' % (self.s_feat_dir)
        with open(s_separate_path, "r") as f:
            for line in f:
                fs = line.strip().split()
                self.d_sep[fs[0]] = fs[1]
        
        s_brand_path = '%s/brands' % (self.s_feat_dir)
        with open(s_brand_path, "r") as fr:
            for line in fr:
                self.e_brand.enter(line.strip())
        self.e_brand.fix()
         
    def separate_deal(self):
        question = self.question
        wentis = question.split('？')
        for wenti in wentis:
            for seprate in self.d_sep:
                flag = True
                for feat in seprate.split('#'):
                    if wenti.find(feat) == -1:
                       flag = False
                       break
                if flag:
                    question = '%s %s' % (question, self.d_sep[seprate])
        self.question = question
 
    def brand_feat_deal(self):
        question = self.question
        ret = self.e_brand.query(question)
        if len(ret) > 1:
            question = '%s brand_num_%s' % (question, len(ret))
        
        self.question = question

    def brand_self_feature():
        XLSDeal().XlsToList(self.feature_file, True)

    def run(self, question):

        self.question = question if type(question) == str else question.encode('utf-8')
        self.separate_deal()
        self.brand_feat_deal()
        return self.question

if __name__ == '__main__':
    o_pre = PreProcess()
    for line in sys.stdin:
        #question = '山区城市，雅阁和凯美瑞最小离地间隙对比，选哪个'
        question = line.strip()
        print o_pre.run(question)

