# -*- coding:utf-8 -*-
'''
    整合计算结构
'''
class ResultAnalyse:
     def __init__(self, l_text, temp_path, d_text_colname):
         '''
         :param l_text:  input file data
         :param temp_path: predict temp file path
         '''
         self.texts = l_text
         self.temp_path = temp_path
         self.d_text_colname = d_text_colname

     def integrate_result(self, map_category, evaluate = False,):
         '''
         :param map_category:  format {'0': name1, '1': name2}
         :param evaluate:
         :return:
         '''
         l_text = self.texts
         temp_path = self.temp_path
         predict_result_data_dict = {}
         l_result_text = []
         with open(temp_path+'.prob') as f:
             one_result_data = f.readline()
             while one_result_data:
                 s_id = one_result_data.split(' ')[0]
                 predtype = map_category[one_result_data.split(' ')[2]].encode('utf-8')
                 prob_list = one_result_data.split(' ')[3:]
                 prob_list.sort()
                 one_result_ret = [predtype, prob_list[-1]]
                 predict_result_data_dict[s_id] = one_result_ret
                 one_result_data = f.readline()

         for i in range(len(l_text)):
             one_result_list = None
             one_text_data_list = l_text[i].split('\t')
             if one_text_data_list[self.d_text_colname['id']] in predict_result_data_dict.keys():  # 如果id能够在keys中相对应
                 id = one_text_data_list[self.d_text_colname['id']]
                 if not evaluate:
                     one_result_list = predict_result_data_dict[id] + one_text_data_list[1:]  # 把元数据第一列去掉，然后在前面插入前三列
                 else:
                     one_result_list = predict_result_data_dict[id] + one_text_data_list  # 在前面插入前三列
                 one_result_str = '\t'.join(one_result_list).replace('\n', '')
                 l_result_text.append(one_result_str)
         return l_result_text

     def getEffect(self):

         C_MAT = []
         precision = ''
         recall = ''
         f1 = ''
         accuracy = ''
         with open(self.temp_path + '.cm', 'r') as fr:
             for line in fr:
                 if line.startswith('confusion_matrix'):
                     st = line.split(':')[1].strip().split('row')
                     for item in st[1:]:
                         eles = item.split('\t')
                         C_MAT.append([ int(ele) for ele in eles])
                 if line.find('precision') != -1:
                     precision = line.split(':')[1].strip()
                 if line.find('recall') != -1:
                     recall = line.split(':')[1].strip()
                 if line.find('f1') != -1:
                     f1 = line.split(':')[1].strip()
                 if line.find('accuracy') != -1:
                     accuracy = line.split(':')[1].strip()
         d_effect = {
             'c_mat': C_MAT,
             'precision': precision,
             'recall': recall,
             'accuracy': accuracy,
             'f1': f1
         }
         return d_effect


