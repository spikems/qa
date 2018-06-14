# -*- coding:utf-8 -*-
import os
import sys
from ..server_conf import *
from ..common.basic_tool import CategoryException
from ..common.exldeal import XLSDeal
from preprocess.cut import cut
from preprocess.dedup import dedup_near
from postprocess.result_analyse import ResultAnalyse
from preprocess.feature import all_by_self_defined_feature
from preprocess.feature import extra_by_self_feature
from learn.train import train, t_predict
import json
import traceback


class DmEngine:
    def __init__(self):
        self.project_version_path = ""
        self.d_method = {}
        self.l_text = []
        self.cut_file = ""
        self.sample_file = ""
        self.dedup_file = ""
        self.model_file = ""
        self.feature_file = ""
        self.d_text_colname = {'label' : c_LABEL, 'id' : c_ID, 'title' : c_TITLE, 'abst' : c_ABST, 'target' : c_TARGET}

    def __prepare(self, project_version_path):

        self.project_version_path = project_version_path
        self.d_method = {}
        self.l_text = []
        self.cut_file = '%s/cut.file' % (project_version_path)
        self.sample_file = '%s/sample.xlsx' % (project_version_path)
        self.dedup_file = "%s/dedup.file" % (project_version_path)
        self.model_file = "%s/model" % (project_version_path)
        self.feature_file = "%s/feature.xlsx" % (project_version_path)

    def __load_method(self):
        method_file = '%s/method' % (self.project_version_path)
        with open(method_file, 'r') as reader:
            for method in reader:
                self.d_method = json.loads(method)
                break

    def __read_sample(self):

        self.l_text = XLSDeal().XlsToList(self.sample_file, True)
        self.l_text.pop(0)

    def __collect_category(self):
        labels_list = []
        text_num = len(self.l_text)
        rm_text_list = []
        for i in range(text_num):
            fs = self.l_text[i].split('\t')
            label = fs[self.d_text_colname['label']]  # 获取label标签
            if not label.strip():   # 如果传入的label为空
                rm_text_list.append(i)
                continue
            labels_list.append(label)
        # 移除为空的数据
        for rm_i in rm_text_list:
            del self.l_text[rm_i]
        labels_list = list(set(labels_list))   # 去重操作
        map_category = {}
        if len(labels_list) < 2:  # 类别少于两个报错
            raise CategoryException('The number of categories less than 2 ')
        elif len(labels_list) == 2:   # 二分类
            map_category = {'0': labels_list[0], '1': labels_list[1]}   # 映射关系
        else:   # 多分类
            for i in range(len(labels_list)):
                map_category[str(i-1)] = labels_list[i]    # '-1', '0', '1', '2'
        self.d_method['map_category'] = map_category    # 将获取到的类别映射关系，保存到method中
        method_file = '%s/method' % self.project_version_path
        with open(method_file, 'w') as fw:
            fw.write(json.dumps(self.d_method))

    def __replace_category(self, evaluate):
        # 替换收集后的类别标签
        result_line_list = []
        reverse_map_category = dict(zip(self.d_method['map_category'].values(), self.d_method['map_category'].keys()))
        for line in self.l_text:
            fs = line.split('\t')
            if evaluate:  # 如果是评估，走预测路线，就需要第一列 从str转unicode， 再转成str
                label = fs[self.d_text_colname['label']]
                if not label.strip():  # 如果第一列为空
                    continue
                label = label if type(label) == unicode else label.decode('utf-8')# 获取label标签
                num_label = reverse_map_category[label]
                fs[self.d_text_colname['label']] = num_label.encode('utf-8')
            else:   # 如果是非评估，就是需要第一列不转变
                label = fs[self.d_text_colname['label']]
                num_label = reverse_map_category[label]
                fs[self.d_text_colname['label']] = num_label
            result_line_list.append('\t'.join(fs))
        self.l_text = result_line_list

    def __cut_word(self, predict = False, evaluate = False):
        #context feature
        l_feature_template = []
        if self.d_method['context_feat_info']['is_use'] == 'true':
            l_feature_template = [
                'all_-1_1', 'all_-2_2', 'all_-1', 'all_1', 'all_-2', 'all_2',
                'v_-1', 'v_1', 'v_-1_1', 'v_2', 'v_-2', 'v_-2_2',
                'a_-1_1', 'a_-1', 'a_1', 'a_2', 'a_-2','a_-2_2',
                'n_-1_1', 'n_-2_2', 'n_-1', 'n_-2', 'n_1', 'n_2'
            ]

        # self defined feature
        l_self_features = []
        if self.d_method['self_feat_info']['is_use'] == 'true' and os.path.exists(self.feature_file):
            l_self_features = XLSDeal().XlsToList(self.feature_file, True)

        #cut word feature
        l_features, l_targets = cut(l_texts=self.l_text, d_text_colname = self.d_text_colname, pos_flag=False, l_feature_template=l_feature_template, special_words = l_self_features, industrys = [])
        if predict and not evaluate:
            tmp_features = []
            for features in l_features:
                features = '0 %s' % (features.strip())
                tmp_features.append(features)
            l_features = tmp_features

        #self defined feature
        if self.d_method['self_feat_info']['is_use'] == 'true' and len(l_self_features):
            self_feat_use_way = self.d_method['self_feat_info']['self_feat_use_way']

            if self_feat_use_way == 'all_by_self_feat':
                #完全使用用户自定义特征
                l_features = all_by_self_defined_feature(l_self_features, l_features, self.d_method['algorithm'], l_targets, c_SYNTAX_FILE)
                
            else:
                #加到特征向量中
                l_features = extra_by_self_feature(l_self_features, l_features)

        #write cut words to cut file
        fw = open(self.cut_file, 'w')
        fw.write("\n".join(l_features))
        fw.close()

    def __dedup(self):
        dedup_near(self.cut_file, self.dedup_file, 6, 3)

    def __train(self):

        train(algorithm=self.d_method['algorithm'], trainfile = self.dedup_file, model_path = self.model_file)

    def run(self, project_version_path = ''):
        try:
            self.__prepare(project_version_path)
            self.__load_method()
            self.__read_sample()
            self.__collect_category()
            self.__replace_category(evaluate=False)

            self.__cut_word()

            self.__dedup()

            self.__train()

        except:
            print traceback.format_exc()

    def predict(self, version_path='', input_path = '', output_path = '', evaluate = False):
        '''
        :param version_path:  待预测版本路径
        :param input_path:  待预测数据输入路径
        :param output_path: 预测结果输出路径
        :param evaluate: 是否为评估调用
        :return: 如果是评估调用，则返回效果
        '''
        # 初始化
        base_path = '/'.join(input_path.split('/')[:-2])
        if evaluate:
            base_path = '/'.join(input_path.split('/')[:-1])

        temp_path = base_path + '/temp/'
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        self.project_version_path = version_path
        self.sample_file = input_path
        model_path = version_path + '/model'
        self.feature_file = version_path + '/feature.xlsx'
        self.cut_file = '%s/%s_cut.file' % (temp_path, output_path.split('/')[-1].split('.')[0])
        self.dedup_file = "%s/dedup.file" % (temp_path)
        self.l_text = []
        self.__load_method()
        self.__read_sample()
        self.l_text_bak = self.l_text
        if evaluate:
            self.__replace_category(evaluate=True)
        self.__cut_word(predict=True, evaluate=evaluate)
        temp_path = temp_path + output_path.split('/')[-1].split('.')[0]
        t_predict(model_path, temp_path,  testfile=self.cut_file, algorithm=self.d_method['algorithm'])
        o_ra = ResultAnalyse(self.l_text_bak, temp_path, self.d_text_colname)
        l_result_text = o_ra.integrate_result(map_category=self.d_method['map_category'], evaluate=evaluate)
        XLSDeal().toXlsFile(l_result_text, output_path)
        d_effect = {}
        if evaluate:
            d_effect = o_ra.getEffect()
        return d_effect

    def evaluate(self, d_version_info={}, input_file=''):
        base_path = '/'.join(input_file.split('/')[:-1])
        base_path = base_path.encode('utf-8') if type(base_path) == unicode else base_path
        download_dir_path = '/'.join(input_file.split('/')[-4 : -2])
        time_stamp = input_file.split('/')[-2]
        d_feedback = {'dir_path': '', 'effect': {}}
        for item in d_version_info:
            version_path = item['path']
            version = item['name'].strip()
            version = version.encode('utf-8') if type(version) == unicode else version
            output_path = '%s/%s_result.xlsx' % (base_path, version)
            d_effect = self.predict(version_path, input_file, output_path, True)
            d_feedback['effect'][version] = d_effect

        filename = '%s.tar.gz' % (time_stamp)
        cmd = 'cd %s/../ && tar -zcvf  %s %s/*.xlsx' % (base_path, filename, time_stamp)
        os.system(cmd)
        d_feedback['dir_path'] = '%s/%s' % (download_dir_path, filename)
        return json.dumps(d_feedback)




