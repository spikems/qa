# -*- coding:utf-8 -*-
import re
import os
import esm
import xlrd
from read_data import WordsTrend
from conf.extract_word_conf import singleton
from conf.extract_word_conf import is_include
from conf.extract_word_conf import remove_include_words
project_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件夹的路径


# QA系统的提取关键词部分
# @singleton
class NewQAExtractWord(object):
    def __init__(self):
        # brand_dict = {'汽车品牌名称'：'所属的汽车名'}   区别同义词，三个都是类似
        self.brand_dict, self.product_dict, self.component_dict, self.attribute_dict, self.evaluation_dict, \
        self.service_dict = self.read_dm_data()  # 读取数据库数据
        self.component_exist, self.attribute_exist, self.evaluation_exist, self.service_exist = {}, {}, {}, {}   # 存放找到的数据
        self.common_word_list, self.re_word_list, self.query_word_type_dict = self.read_query_data(path=(project_path + '/conf/query_word.xlsx'))

        self.re_formula_dict = self.assemble_re_formula()
        self.integrate_word_dict = {}   # 整合数据:  product   component, attribute
        self.search_index = esm.Index()
        self.integrate_data()

    @staticmethod
    def read_dm_data():
        '''
            读取数据库的数据
        '''
        dm_obj = WordsTrend()
        query_list = ['brand', 'product', 'component', 'attribute', 'evaluation', 'service']  # 需要查询的表
        brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict = dm_obj.master(query_list)
        return brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict

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

    def integrate_data(self):
        '''
            整合数据:  product   component, attribute
        '''
        sign_num = 0    # 用来标记列表位置
        sign_list = ['product', 'component', 'attribute', 'evaluation', 'service']
        for data_dict in [self.product_dict, self.component_dict, self.attribute_dict, self.evaluation_dict, self.service_dict]:
            sign_str = sign_list[sign_num]
            for data in data_dict.keys():
                if data in self.integrate_word_dict:
                    self.integrate_word_dict[data] += [sign_str]
                else:
                    self.integrate_word_dict[data] = [sign_str]
            sign_num += 1
        for data in self.integrate_word_dict.keys():
            self.search_index.enter(data)
            if len(self.integrate_word_dict[data]) > 1:
                print data, ': ', self.integrate_word_dict[data]
        self.search_index.fix()

    def integrate_search(self, question):
        '''
            利用index搜索数据
        :return:
        '''
        exit_word_list = []
        pos_word_data = self.search_index.query(question)     # 数据格式是[((6,12), 变速), ((6,15), 变速器)]
        skip_sign = 0  # 0代表不跳过， 1代表跳过前一个词，2代替跳过前两个词
        word_list_lenght = len(pos_word_data)
        for num in range(word_list_lenght):
            # while stop_sign:  # 向后就看是否有被包含关系，
            if num == 0:    # 第一个位置的词比较特殊，需要和后面一个词进行比较
                if len(pos_word_data) < 2:  # 如果只有一个词
                    exit_word_list.append(pos_word_data[num][1])
                else:
                    first_start_pos, first_end_pos = pos_word_data[0][0]
                    i = 1  # 用来代表比较的下一个词
                    second_start_pos,  second_end_pos = pos_word_data[1][0]
                    # 第一个大括号表达包含关系，   第二个括号表达，即使是包含关系，后面没有内容了
                    while (first_end_pos >= second_end_pos) and (i < (word_list_lenght - 1)):    # 当包含关系是继续向下
                        i += 1
                        second_start_pos, second_end_pos = pos_word_data[i][0]
                    if first_start_pos < second_start_pos:   # 去除末尾包含后，如第一个词不等于第二个词开头，则肯定是分开
                        exit_word_list.append(pos_word_data[num][1])
                    else:
                        skip_sign = 1
            elif (num+1) == len(pos_word_data):  # 如果是最后一个词, 只要不是包含前一个词，且起始位置 落后 上个词的结束位置
                last_star_pos, last_end_pos = pos_word_data[num - 1 - skip_sign][0]  # 上一个
                star_pos, end_pos = pos_word_data[num][0]
                if (star_pos < last_end_pos) and (star_pos != last_star_pos):  # 如果当前  (轮胎和胎噪) 情况
                    continue
                else:
                    exit_word_list.append(pos_word_data[num][1])
            else:
                if (num - 1 - skip_sign) >= 0:  # 向前遍历，不能低于第一个元素
                    last_star_pos, last_end_pos = pos_word_data[num - 1 - skip_sign][0]  # 上一个
                else:
                    last_star_pos, last_end_pos = 0, 0
                next_star_pos, next_end_pos = pos_word_data[num+1][0]  # 下一个
                star_pos, end_pos = pos_word_data[num][0]  # 本次
                if (star_pos >= next_star_pos) or (star_pos < last_end_pos and star_pos != last_end_pos):  # 向前和向后的比较
                    skip_sign += 1  # 觉得是否要跳过这个词
                    continue
                else:
                    exit_word_list.append(pos_word_data[num][1])
                    skip_sign = 0
        exit_word_list = list(set(exit_word_list))
        return exit_word_list

    def divide_data(self, exit_word_list):
        '''
            划分各个存在词的数据列表
            :return:
        '''
        product_word_list, component_word_list, attribute_word_list, evaluation_word_list, service_word_list = [], [], [], [], []
        for word in exit_word_list:
            type_str_list = self.integrate_word_dict[word]
            for type_str in type_str_list:
                if type_str == 'product':
                    product_word_list.append(self.product_dict[word])
                elif type_str == 'component':
                    if word != self.component_dict[word]:  # 如果两个词不相同，需要替换
                        self.component_exist[word] = self.component_dict[word]
                    component_word_list.append(self.component_dict[word])
                elif type_str == 'attribute':
                    if word != self.attribute_dict[word]:
                        self.attribute_exist[word] = self.attribute_dict[word]
                    attribute_word_list.append(self.attribute_dict[word])
                elif type_str == 'evaluation':
                    if word != self.evaluation_dict[word]:
                        self.evaluation_exist[word] = self.evaluation_dict[word]
                    evaluation_word_list.append(self.evaluation_dict[word])
                elif type_str == 'service':
                    if word != self.service_dict[word]:
                        self.service_exist[word] = self.service_dict[word]
                    service_word_list.append(self.service_dict[word])
        product_word_list = list(set(product_word_list))
        component_word_list = list(set(component_word_list))
        attribute_word_list = list(set(attribute_word_list))
        evaluation_word_list = list(set(evaluation_word_list))
        service_word_list = list(set(service_word_list))
        return product_word_list, component_word_list, attribute_word_list, evaluation_word_list, service_word_list

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

    def question_replace(self, question):
        '''替换疑问词'''
        for data_dict in [self.component_exist, self.attribute_exist, self.evaluation_exist, self.service_exist]:
            for word1 in data_dict:
                if word1 in question:
                    question = question.replace(word1, data_dict[word1], 5)
        return question

    def extract_master(self, question):
        question = ''.join(question.strip().lower().split())
        brand_word_list, product_word_list, component_word_list, attribute_word_list, query_word = [], [], [], [], []
        brand_word_list = self.filter_brand_word(question)
        query_word = self.filter_query_word(question)
        exit_word_list = self.integrate_search(question)
        product_word_list, component_word_list, attribute_word_list, evaluation_word_list, service_word_list \
            = self.divide_data(exit_word_list)
        new_question = self.question_replace(question)
        result_dict = {'question': question, 'new_question': new_question, 'brand': brand_word_list, 'product': product_word_list,
                       'attribute': attribute_word_list,'component': component_word_list, 'evaluation': evaluation_word_list,
                       'service': service_word_list, 'qword': query_word}
        return result_dict

if __name__ == '__main__':
    ext_obj = NewQAExtractWord()
    question = '想了解是否需要给小六喷底盘装甲'
    # question = '请问各位的机油尺看的清楚吗？'
    ext_obj.extract_master(question)
