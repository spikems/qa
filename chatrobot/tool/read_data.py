#! /usr/bin/python
# -*- coding:utf-8 -*-
from modelbase import ModelBase


class WordsTrend(ModelBase):

    def __init__(self):
        super(WordsTrend, self).__init__()
        self.brand_table = 'brands'
        self.product_table = 'product'
        self.component_table = 'component'
        self.attribute_table = 'attribute'
        self.evaluation_table = 'evaluation'
        self.service_table = 'service'

    def query_brand(self):
        sql = 'select * from %s where industry=2' % self.brand_table
        db_datas = super(WordsTrend, self).query(sql)
        brands_word_dict = {}  # 属性词
        for data in db_datas:
            data['brand_name'] = data['brand_name'].strip().lower() if data['brand_name'] else None  # 所有的name转为
            if data['brand_name']:  # 如果存在
                data['brand_name'] = ''.join(data['brand_name'].split())
                brands_word_dict[data['brand_name']] = data['brand_name']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        syn_word = ''.join(word.strip().split())
                        brands_word_dict[syn_word] = data['brand_name']
        return brands_word_dict

    def query_product(self):
        sql = 'select * from %s where industry=2' % self.product_table
        db_datas = super(WordsTrend, self).query(sql)
        product_word_dict = {}  # 属性词
        for data in db_datas:
            data['product'] = data['product'].strip().lower() if data['product'] else None  # 所有的name转为
            if data['product']:  # 如果存在
                data['product'] = ''.join(data['product'].split())
                product_word_dict[data['product']] = data['product']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        syn_word = ''.join(word.strip().split())
                        product_word_dict[syn_word] = data['product']
        return product_word_dict

    def query_component(self):
        sql = 'select * from %s where industry_id=2' % self.component_table
        db_datas = super(WordsTrend, self).query(sql)
        component_word_dict = {}  # 属性词
        for data in db_datas:
            data['component'] = data['component'].strip().lower() if data['component'] else None  # 所有的name转为
            if data['component']:  # 如果存在
                component_word_dict[data['component']] = data['component']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        component_word_dict[word.strip()] = data['component']
        return component_word_dict

    def query_attribute(self):
        sql = 'select * from %s where industry_id=0 or industry_id=2' % self.attribute_table
        db_datas = super(WordsTrend, self).query(sql)
        attribute_word_dict = {}  # 同义词
        for data in db_datas:
            data['word'] = data['word'].strip().lower() if data['word'] else None  # 所有的name转为
            if data['word']:  # 如果存在
                attribute_word_dict[data['word']] = data['word']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        attribute_word_dict[word.strip()] = data['word']
        return attribute_word_dict

    def query_evaluation(self):
        sql = 'select * from %s where industry_id=0 or industry_id=2' % self.evaluation_table
        db_datas = super(WordsTrend, self).query(sql)
        evaluation_word_dict = {}  # 同义词
        for data in db_datas:
            data['evaluation'] = data['evaluation'].strip().lower() if data['evaluation'] else None  # 所有的name转为
            if data['evaluation']:  # 如果存在
                evaluation_word_dict[data['evaluation']] = data['evaluation']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        evaluation_word_dict[word.strip()] = data['evaluation']
        return evaluation_word_dict

    def query_service(self):
        sql = 'select * from %s where industry=0 or industry=2' % self.service_table
        db_datas = super(WordsTrend, self).query(sql)
        service_word_dict = {}  # 同义词
        for data in db_datas:
            data['word'] = data['word'].strip().lower() if data['word'] else None  # 所有的name转为
            if data['word']:  # 如果存在
                service_word_dict[data['word']] = data['word']
            else:
                continue
            # 处理同义词过程
            data['synonyms'] = data['synonyms'].strip().lower() if data['synonyms'] else None
            if data['synonyms']:
                syn_list = data['synonyms'].split('|')
                for word in syn_list:
                    if word.strip():  # 如果同义词不为空
                        service_word_dict[word.strip()] = data['word']

        return service_word_dict

    def query_relaword(self):
        """
        find sent relaword according to keyword
        :return:
        """
        sql = "select kword,relaword from relaword where industry ='汽车' "
        db_datas = super(WordsTrend, self).query(sql)
        rela_dict = {}
        for word in db_datas:
            kword = word['kword'].strip().lower()
            relaword = word['relaword'].strip().lower()
            if kword in rela_dict:
                rela_dict[kword].append(relaword)
            else:
                rela_dict[kword] = [ relaword,]
        return rela_dict

    def master(self, query_list):
        print query_list
        brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict,rela_dict = {}, {}, {}, {}, {}, {},{}
        if 'brand' in query_list:
            brand_dict = self.query_brand()  # 获取品牌数据
        if 'product' in query_list:
            product_dict = self.query_product()  # 获取车型数据
        if 'component' in query_list:
            component_dict = self.query_component()  # 获取组件数据
        if 'attribute' in query_list:
            attribute_dict = self.query_attribute()  # 获取属性数据
        if 'evaluation' in query_list:
            evaluation_dict = self.query_evaluation()  # 获取评价词数据
        if 'service' in query_list:
            service_dict = self.query_service()  # 获取服务词数据
        if  'rela_dict' in query_list:
            rela_dict = self.query_relaword() # get relaword

        return brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict,rela_dict


def write_to_file():
    test = WordsTrend()
    test.query_relaword()
    brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict,rela_dict=\
        test.master(['brand', 'product', 'component', 'attribute','evaluation','service','rela_dict'])
    print rela_dict
    exit()
    names = [brand_dict, product_dict, component_dict, attribute_dict, evaluation_dict, service_dict]
    files = ['brand', 'product', 'component', 'attribute','evaluation','service']
    num = 0
    for sub in names:
        outf = open('data/%s'%files[num],'w')
        num+=1
        vset = set([])
        for k,v in sub.items():
            vset.add(v.strip())
        for word in vset:
            outf.write('%s\n'%word)
        outf.close()




if __name__ == '__main__':
    write_to_file()
