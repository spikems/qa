# -*- coding:utf-8 -*-
import copy

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


def is_include(word, word_list):
    '''
        检验词是否有包含关系
    '''
    included_words = []
    for other_word in word_list:
        if (word in other_word) and (word != other_word):  # 如果 被其他词包含，且 不等于 原词
            included_words.append(other_word)
    if included_words:  # 如果有那些词
        return True, included_words
    return False, []


def remove_include_words(question, word_list):
    record_word_number = {}  # 记录每个词出现的次数
    for word in word_list:
        pos1 = question.find(word, 0)
        num = 0
        while pos1 != -1:  # 如果能找到
            num += 1
            pos1 = question.find(word, pos1 + len(word))
        if num > 0:
            record_word_number[word] = num
    remove_index_list = []  # 移除包含关系的索引
    for rec_word in record_word_number.keys():
        # 如：word为A6，include_words为[A6L,A6K]的关系
        judge_result, include_words = is_include(rec_word, record_word_number.keys())
        if judge_result:
            long_num = 0
            for long_word in include_words:  # 遍历被包含的数据，
                long_num += record_word_number[long_word]
            if long_num >= record_word_number[rec_word]:  # 如果长的词 如A6L出现2次，A6出现1或2次，则表明只有A6L
                remove_index_list.append(rec_word)
    result_word_list = record_word_number.keys()
    for re_word in remove_index_list:
        result_word_list.remove(re_word)
    return result_word_list