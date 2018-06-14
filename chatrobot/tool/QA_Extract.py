# -*- coding:utf-8 -*-
import re
import os
import xlrd
from read_data import WordsTrend
from conf.extract_word_conf import singleton
from conf.extract_word_conf import is_include
from conf.extract_word_conf import remove_include_words
from wcut.jieba.norm import norm_cut,load_industrydict
load_industrydict([0,2])
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


# QA系统的提取关键词部分
# @singleton
class NewQAExtractWord(object):
    def __init__(self):
        # brand_dict = {'汽车品牌名称'：'所属的汽车名'}   区别同义词，三个都是类似
        self.brand_dict, self.product_dict, self.component_dict, self.attribute_dict, self.evaluation_dict, \
        self.service_dict,self.rela_dict = self.read_dm_data()  # 读取数据库数据

        #读取疑问词
        self.common_word_list, self.re_word_list, self.query_word_type_dict = self.read_query_data(path=(project_path + '/conf/query_word.xlsx'))

        self.re_formula_dict = self.assemble_re_formula()
        self.synonym = {}
        for sub in [self.brand_dict,self.product_dict, self.component_dict, self.attribute_dict, self.evaluation_dict,self.service_dict,]:
            self.synonym.update(sub)

    @staticmethod
    def read_dm_data():
        '''
            读取数据库的数据
        '''
        dm_obj = WordsTrend()
        query_list = ['brand', 'product', 'component', 'attribute', 'evaluation', 'service','rela_dict']  # 需要查询的表
        brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict,rela_dict = dm_obj.master(query_list)
        return brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict,rela_dict

    @staticmethod
    def read_query_data(path):
        '''
            读取疑问词数据
        '''
        read_data = xlrd.open_workbook(path)
        table = read_data.sheets()[0]
        common_word_list = []   # 普通词的列表
        re_word_list = []   # 需要通过正则匹配的数据
        query_word_type_dict = {}  # 格式：   query_word:所属类型
        for i in range(1, table.nrows):
            line = table.row_values(i)
            word = line[0].encode('utf-8').strip().lower() if type(line[0]) == str or type(line[0]) == unicode else \
                str(line[0])
            word_type = line[1].encode('utf-8').strip().lower() if type(line[1]) == str or type(line[1]) == unicode else \
                str(line[1])
            word_weight = int(line[2])
            if '#' in word:
                re_word_list.append(word)
            else:
                common_word_list.append(word)
            query_word_type_dict[word] = [word_type,word_weight]
        return common_word_list, re_word_list, query_word_type_dict

    def replace_word(self,word):
        """
        替换同义词
        :param word:
        :return:
        """
        if word in self.synonym:
            return self.synonym[word]
        else:
            return word

    def extract_keyword(self, question):
        '''
            提取四元组:包括产品,组件,评价,服务
        :return:
        '''
        # 替换同义词
        dic = {'relaword':set([])}
        cut_sent = [self.replace_word(i.encode('utf-8','ignore')) for i in norm_cut(question)]
        key_list = [self.product_dict, self.component_dict, self.attribute_dict, self.evaluation_dict,
        self.service_dict]
        keynames = ['product','component','attribute','evaluation','service']
        # print self.rela_dict
        print self.rela_dict['发动机']
        num =0
        for sub in key_list:
            extract_word = set(cut_sent)&set(sub.values())
            dic[keynames[num]] = extract_word
            num+=1
            #寻找关联词
            for word in extract_word:
                if word in self.rela_dict:
                    for relaword in set(self.rela_dict[word])&set(cut_sent):
                        if relaword and relaword not in self.synonym.values():
                            dic['relaword'].add(relaword)
        #格式化 ,全部以列表形式返回
        keynames.append('relaword')
        for name in keynames:
            if dic[name]:
                dic[name] = [i for i in dic[name]]
            else:
                dic[name] = []

        #添加同义词更改后的问句
        dic['new_question'] = ''.join(cut_sent)
        return dic

    def assemble_re_formula(self):
        '''
            通过（有#嘛）组装re表达式字典    {word: formula}
        '''
        re_formula_dict = {}
        for word in self.re_word_list:
            word_list = word.split('#')
            re_formula = re.compile(r'(%s).*?(%s)' % (word_list[0], word_list[1]))
            re_formula_dict[word] = re_formula
        return re_formula_dict

    def filter_brand_word(self, question):
        '''
            识别品牌词
        '''
        brand_word_list = []
        exist_brands_list = remove_include_words(question, self.brand_dict.keys())
        for brand in exist_brands_list:
            brand_word_list.append(self.brand_dict[brand])
        brand_word_list = list(set(brand_word_list))
        if '北京' in brand_word_list and len(brand_word_list) > 1:
            brand_word_list.remove('北京')
        elif '东南' in brand_word_list and len(brand_word_list) > 1:
            brand_word_list.remove('东南')
        return brand_word_list


    def filter_query_word(self, question):
        '''
            过滤疑问词
        '''
        query_word_list = []  # 标题中的疑问词
        for word in self.common_word_list:   # 判断普通的词
            if word in question:
                query_word_list.append(word)
        remove_index_list = []  # 移除包含关系的索引
        for i in range(len(query_word_list)):
            judge_result, included_words = is_include(query_word_list[i], query_word_list[0:i] + query_word_list[i+1:])
            if judge_result:
                remove_index_list.append(query_word_list[i])
        for word in remove_index_list:
            query_word_list.remove(word)

        for word in self.re_formula_dict.keys():
            re_formula = self.re_formula_dict[word]
            if re_formula.search(question):  # 如果存在  有#吗数据
                query_word_list.append(word)

        add_query_type_dict = {}   # 添加疑问词类型
        for word in query_word_list:
            type_word = self.query_word_type_dict[word][0]
            word_weight = self.query_word_type_dict[word][1]
            if type_word in add_query_type_dict:   # 如果有这个种类,选取最大值
                if add_query_type_dict[type_word] < word_weight:
                    add_query_type_dict[type_word] = word_weight
            else:  # 如果字典没有这种类型
                add_query_type_dict[type_word] = word_weight
        # 字典排序输出
        if add_query_type_dict:   # 如果问题不为空
            sorted_data = sorted(add_query_type_dict.items(), key=lambda item: item[1], reverse=True)
            return sorted_data[0][0]
        else:
            return None

    def extract_master(self, question):
        question = ''.join(question.strip().lower().split())
        brand_word_list = self.filter_brand_word(question)
        query_word = self.filter_query_word(question)
        result_dict = { 'brand': brand_word_list, 'qword': query_word}
        dic = self.extract_keyword(question)
        result_dict.update(dic)
        return result_dict

if __name__ == '__main__':
    ext_obj = NewQAExtractWord()
    question = '冬天关闭大众洗发动机的价位怎么样'
    # question = '请问各位的机油尺看的清楚吗？'
    result = ext_obj.extract_master(question)
    print result
    print result['new_question']
    print ' '.join(result['component'])
    print ' '.join(result['relaword'])
    print result['qword']