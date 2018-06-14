#encoding:utf-8
# from chatrobot.common.exldeal import XLSDeal
from chatrobot.common.util import singleton
# from util import singleton
from exldeal import XLSDeal
import os
import esm
import sys
import jieba

@singleton
class Preprocess:

    def __init__(self):
        self.question = ''
        self.context = ''
        self.length = 0
        self.s_inquire_dir = '%s/../data' % os.path.dirname(os.path.abspath(__file__))
        self.f_inquire_feature = '%s/query_word.xlsx' % self.s_inquire_dir
        self.f_lian_feature = '%s/lian_word' % self.s_inquire_dir
        self.e_lianword = esm.Index()
        self.__load_lianword()
        self.d_inquire_feature = {}
        self.has_title_inquire_word = False
        self.has_context_inquire_word = False
        self.wenhao_thre = 10
        self.inquire_thre = 13
        self.__load__inquire_feature()

    def __load_lianword(self):
        with open(self.f_lian_feature, 'r') as fr:
            for line in fr:
                self.e_lianword.enter(line.strip())
        self.e_lianword.fix()

    def __load__inquire_feature(self):
        l_self_features = XLSDeal().XlsToList(self.f_inquire_feature, True)
        for item in l_self_features:
            fs = item.split('\t')
            if len(fs) < 1:
                continue
            inquire = fs[0]
            self.d_inquire_feature[inquire] = 1

    def __has_lianword(self, text):
        ret = self.e_lianword.query(text.encode('utf-8'))
        return len(ret) > 0

    def __has_inquire_word(self):
        '''
         1. 是否含有疑问词
        :return:
        '''
        self.has_title_inquire_word = False
        for inquire in self.d_inquire_feature:
            fs = inquire.split('#')
            flag = True
            for item in fs:
                if self.question.find(item.decode('utf-8')) == -1:
                    flag = False
                    break
            if flag:
                self.has_title_inquire_word = True
                break

        self.has_context_inquire_word = False
        last_ind_list = []
        for inquire in self.d_inquire_feature:
            fs = inquire.split('#')
            last_ind = ''
            flag = True
            for item in fs:
                if self.context.find(item.decode('utf-8')) == -1 or item.decode('utf-8') in (u'?', u"？"):
                    flag = False
                last_ind = self.context.find(item.decode('utf-8'))
            if flag:
                last_ind_list.append(last_ind)
        if last_ind_list:   # 如果包含疑问词数据
            last_ind = min(last_ind_list)
            sent_ind = self.__getCurSentIndex(self.context, last_ind)
            self.has_context_inquire_word = sent_ind


    def __subUniqSequence(self, text):
        ret = []
        for ch in text[::-1]:
            ret.append(ch)
            if ch in (u',', u'!', u'。', u'，', u'！'):
                break
        return "".join(ret[::-1])

    def __getCurSentIndex(self, text, last_ind):

        i = 0
        text = '%s?' % (text)
        for ch in text[last_ind + 1:]:
            i = i + 1
            if ch in (u',', u'!', u'。', u'，', u'！'):
                break
        return last_ind + i

    def __containWenHao(self, text):
        return text.find(u'?') != -1 or text.find(u'？') != -1

    def __getWenHaoPos(self, text):
         first = text.find(u'?')
         second = text.find(u'？')
         if first > 0 and second > 0:
             return min(second, first)
         elif first * second < 0:
             return max(first, second)
         return 0

    def __title_ratio(self, abstract):
        abstract = abstract.encode('utf-8') if type(abstract) == unicode else abstract
        cal_ratio_index = esm.Index()
        word_list = jieba.cut(self.question)
        for word in word_list:
            if not word.strip():  # 去掉空格
                continue
            cal_ratio_index.enter(word.encode('utf-8') if type(word) == unicode else word)
        cal_ratio_index.fix()
        ret = cal_ratio_index.query(abstract)
        query_word_list = []
        for i in ret:
            if i[1] not in query_word_list:
                query_word_list.append(i[1])
        repeat_length = len(''.join(query_word_list))
        return float(repeat_length) / float(len(self.question))

    def __prepare(self, question, context):

        self.question = question.decode('utf-8') if type(question) == str else question
        self.context = context.decode('utf-8') if type(context) == str else context
        self.q_length = len(self.question)
        self.c_length = len(self.context)
        self.has_inquire_word = False
        self.has_title_inquire_word = False
        self.has_context_inquire_word = False
        self.__has_inquire_word()

    def rule_1(self):
        '''
        如果标题含有问号， 而且字数<35,  且 >=10 ,  就直接选取标题
        :return:
        '''
        if self.__containWenHao(self.question) and self.q_length >= self.wenhao_thre and self.q_length < 35:
            return True, self.question
        return False, self.question

    def rule_2(self):
        '''
         如果标题（0）含有疑问词， 而且标题字数<35,  且 >=13 , 就直接选取标题
        :param self:
        :return:
        '''
        if self.has_title_inquire_word and self.q_length >= self.inquire_thre and self.q_length < 35:
            return True, self.question
        return False, self.question

    def rule_3(self):
        '''
        否则，保留标题，从正文补充：
        :return:
        '''
        abstract_A = self.rule_3_A().strip()  # 摘要A
        abstract_B = self.rule_3_B().strip()  # 摘要B
        abstract_C = ''             # 摘要C
        if (not abstract_A) and (not abstract_B):  # 如果摘要A和摘要B都为空
            return False, ''
        if not self.question.strip():   # 如果question 为空
            abstract_C = abstract_B if abstract_B else abstract_A
        else:
            k_A = self.__title_ratio(abstract_A)
            k_B = self.__title_ratio(abstract_B)
            abstract_C = abstract_A if (k_A > k_B) else abstract_B
        if not abstract_C and abstract_A:   # 避免了  如果  abstract_A不为0，abstract_b为0，但是k_A为0.
            abstract_C = abstract_A
        k_C = self.__title_ratio(abstract_C)
        if k_C > 0.33:
            return True, abstract_C
        else:
            return True, '%s%s' % (self.question, abstract_C)

    def rule_3_A(self):
        '''
         规则3. A，找到正文第一个问号，截取问号到前面逗号的字段（1），并对（1）的长度判断
        :return:
        '''
        if self.__containWenHao(self.context) and self.c_length > 0:
            inq_ind = self.__getWenHaoPos(self.context)
            s_sub_seq = self.__subUniqSequence(self.context[:inq_ind])
            fetch = ''
            if len(s_sub_seq) >= self.wenhao_thre:
                if self.__has_lianword(s_sub_seq): #有
                    ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
                    s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                    fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
                else:
                    fetch = s_sub_seq
            else:
                ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
                s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                if self.__has_lianword(s_pre_sub_seq): #有
                    ind = 0 if inq_ind - len(s_sub_seq) - len(s_pre_sub_seq) < 0 else inq_ind - len(s_sub_seq) - len(s_pre_sub_seq)
                    s_pre_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                    fetch = '%s%s%s' % ( s_pre_pre_sub_seq, s_pre_sub_seq, s_sub_seq)
                else:
                    fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
            # #B coding
            # common_len = len([item for item in  self.question  if item in fetch])
            # if float(common_len) / (self.q_length) > 0.33:
            #     return True, fetch
            # else:
            #     return True, '%s%s' % (self.question, fetch)
            return fetch
        return ''

    def rule_3_B(self):

        '''
           规则3. B，找到正文第一个疑问词，截取疑问词所在的那句话（1），并对（1）的长度判断
           :return:
        '''
        if self.has_context_inquire_word and self.c_length > 0:
            inq_ind = self.has_context_inquire_word
            s_sub_seq = self.__subUniqSequence(self.context[:inq_ind])
            fetch = ''
            if len(s_sub_seq) >= self.inquire_thre: #contain comma is ten
                if self.__has_lianword(s_sub_seq): #有
                    ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
                    s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                    fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
                else:
                    fetch = s_sub_seq
            else:
                ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
                s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                if self.__has_lianword(s_pre_sub_seq): #有
                    ind = 0 if inq_ind - len(s_sub_seq) - len(s_pre_sub_seq) < 0 else inq_ind - len(s_sub_seq) - len(s_pre_sub_seq)
                    s_pre_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
                    fetch = '%s%s%s' % (s_pre_pre_sub_seq,  s_pre_sub_seq, s_sub_seq )
                else:
                    fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)

            # # B coding
            # common_len = len([item for item in self.question if item in fetch])
            # if float(common_len) / float(self.q_length) > 0.33:
            #     return True, fetch
            # else:
            #     return True, '%s%s' % (self.question, fetch)
            return fetch
        return ''

    # def rule_5(self):
    #
    #     '''
    #        见wiki：http://doc.mxspider.top/pages/viewpage.action?pageId=853280
    #        :return:
    #     '''
    #     if self.has_context_inquire_word and self.c_length > 0:
    #         inq_ind =  self.has_context_inquire_word
    #         s_sub_seq = self.__subUniqSequence(self.context[:inq_ind])
    #         fetch = ''
    #         if len(s_sub_seq) >= self.inquire_thre: #contain comma is ten
    #             if self.__has_lianword(s_sub_seq): #有
    #                 ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
    #                 s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #                 fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
    #             else:
    #                 fetch = s_sub_seq
    #         else:
    #             ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
    #             s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #             if self.__has_lianword(s_pre_sub_seq): #有
    #                 ind = 0 if inq_ind - len(s_sub_seq) - len(s_pre_sub_seq) < 0 else inq_ind - len(s_sub_seq) - len(s_pre_sub_seq)
    #                 s_pre_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #                 fetch = '%s%s%s' % (s_pre_pre_sub_seq,  s_pre_sub_seq, s_sub_seq )
    #             else:
    #                 fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
    #
    #         # B coding
    #         common_len = len([item for item in self.question if item in fetch])
    #         if float(common_len) / float(self.q_length) > 0.33:
    #             return True, fetch
    #         else:
    #             return True, '%s%s' % (self.question, fetch)
    #     return False, ''

    # def rule_6(self):
    #     '''
    #      见wiki：http://doc.mxspider.top/pages/viewpage.action?pageId=853280
    #     :return:
    #     '''
    #     if self.has_title_inquire_word and self.q_length < self.inquire_thre and self.q_length > 0 and \
    #            self.__containWenHao(self.context) and self.c_length > 0 :
    #
    #         inq_ind = self.__getWenHaoPos(self.context)
    #         s_sub_seq = self.__subUniqSequence(self.context[:inq_ind])
    #         fetch = ''
    #         if len(s_sub_seq) >= self.wenhao_thre:
    #             if self.__has_lianword(s_sub_seq): #有
    #                 ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
    #                 s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #                 fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
    #             else:
    #                 fetch = s_sub_seq
    #         else:
    #             ind = 0 if inq_ind - len(s_sub_seq) < 0 else inq_ind - len(s_sub_seq)
    #             s_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #             if self.__has_lianword(s_pre_sub_seq): #有
    #                 ind = 0 if inq_ind - len(s_sub_seq) - len(s_pre_sub_seq) < 0 else inq_ind - len(s_sub_seq) - len(s_pre_sub_seq)
    #                 s_pre_pre_sub_seq = self.__subUniqSequence(self.context[:ind])
    #                 fetch = '%s%s%s' % ( s_pre_pre_sub_seq, s_pre_sub_seq, s_sub_seq)
    #             else:
    #                 fetch = '%s%s' % (s_pre_sub_seq, s_sub_seq)
    #
    #         #B coding
    #         common_len = len([item for item in  self.question  if item in fetch])
    #         if float(common_len) / (self.q_length) > 0.33:
    #             return True, fetch
    #         else:
    #             return True, '%s%s' % (self.question, fetch)
    #
    #     return False, ''

    def run(self, question, context):

        self.__prepare(question, context)
        fs = ['rule_1', 'rule_2', 'rule_3']
        for name in fs:
            ret, question = getattr(self, name)()
            if ret:
                if len(question) < 5 or len(question) > 50:
                    question = ''
                else:
                    while question[0] in (u',', u'!', u'。', u'，', u'！'):
                        question = question[1:]
                return name, question
        return 'illegal question!', ''


if __name__ == "__main__":
    question = '比亚迪宋油耗怎么看'
    context = '我买的2017款手动精英1.5T的，请问油耗怎么看，怎么调'
    rule, question = Preprocess().run(question, context)
    print rule, question
