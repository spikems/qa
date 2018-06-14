#encoding:utf-8
import sys
import os
import esm
from chatrobot.common.exldeal import XLSDeal
from chatrobot.common.wcut.jieba.norm import norm_seg, load_industrydict
from chatrobot.dm.learner import Learner
from chatrobot.common.util import singleton
import json

@singleton
class ModelDeal:
   
    def __init__(self):
        
        self.s_model_dir = '%s/model_data' % os.path.dirname(os.path.abspath(__file__))
        self.method_file = '%s/method' % (self.s_model_dir)
        self.model_file = '%s/model' % (self.s_model_dir)
        self.feature_file = "%s/feature.xlsx" % (self.s_model_dir)
        self.f_Index = esm.Index()
        self.predictor = ''
        self.__load_model()
        self.__load_method()
        self.__load_feature()
        load_industrydict([2, 7])

    def __load_model(self):
        self.predictor = Learner(train=False)
        self.predictor.load_model(self.model_file)

    def __load_method(self):
        with open(self.method_file, 'r') as reader:
            for method in reader:
                self.d_method = json.loads(method)
                break

    def __load_feature(self):
        if self.d_method['self_feat_info']['is_use'] == 'true' and os.path.exists(self.feature_file):
            l_self_features = XLSDeal().XlsToList(self.feature_file, True)
            for feature in l_self_features:
                feature = feature.strip()
                self.f_Index.enter(feature)
            self.f_Index.fix()

    def __cut_word(self, s_text=''):
        ws = norm_seg(s_text)
        l_features = []
        for word in ws:
            l_features.append(word.word)
        s_text = " ".join(l_features)
        return s_text.encode('utf-8')

    def __extra_word(self, s_text = ''):

        ret = self.f_Index.query(s_text)
        for item in ret:
            feature = item[1]
            s_text = '%s self_defined_feature_%s' % (s_text, feature)
        return s_text

    def predict(self, s_text):
        pred, pred_prob = self.predictor.predict_one(s_text)
        return pred, pred_prob

    def run(self, s_text = ''):
        s_text = self.__cut_word(s_text)
        s_text = self.__extra_word(s_text)
        pred, pred_prob = self.predict(s_text)
        # map_category = {'0': 'compare', '1' : 'no_compare'}
        map_category = {'0': True, '1': False}
        return map_category[str(pred[0])]

if __name__ == '__main__':
    pass

