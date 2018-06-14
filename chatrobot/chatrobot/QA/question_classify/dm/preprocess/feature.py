#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,time
import os, os.path
import esm
from semeval_preprocess import  PreDeal


def all_by_self_defined_feature(l_self_features, l_features, algorithm, l_targets, syntax_file):
    """
    :param l_self_features: self-defined features,
    :param l_features: l_features, a list for feature string. format as . label id cuted_text
    :return: l_ret_feats : a list for feature string. format as . label id cuted_text
    """

    #完全使用自定义的特征
    l_ret_feats = []
    if algorithm == 'xgb':
        d_word_map = {}
        for record in l_self_features:
            record = record.split('\t')
            name = record[0].lower().strip()
            Type = record[1].lower().strip()
            d_word_map[name] = [Type]
        with open(syntax_file, 'r') as fr:
            for line in fr:
                fs = line.split('\t')
                name = fs[0].strip().lower()
                Type = fs[1].strip().lower()
                d_word_map[name] = [Type]
        l_ret_feats = xgb_semeval_feature(l_self_features, l_features, l_targets, d_word_map)
        return l_ret_feats

    index = esm.Index()
    for feature in l_self_features:
        feature = feature.strip()
        index.enter(feature)
    index.fix()

    for s_features in l_features:
        label = s_features.split()[0]
        id = s_features.split()[1]
        ret = index.query(s_features)
        words = []
        for item in ret:
            feature = item[1]
            words.append(feature)
        words = " ".join(words)
        if words.strip() == '':
            words = 'no_feature' 
        feat_r = " ".join([label, id, words])
        l_ret_feats.append(feat_r)
    return l_ret_feats

def xgb_semeval_feature(l_self_features, l_features, l_targets, d_word_map):
    l_ret_feats = []
    for i in range(len(l_features)):
        target = l_targets[i]
        sent = l_features[i]
        label = sent.split()[0]
        id = sent.split()[1]
        sent = " ".join(sent.split()[2:])
        feats = [label, id]
        words = PreDeal().run(sent, d_word_map, target, 2)
        if words.strip() == '':
            words = 'no_feature'
        feats.append(words)
        feat_r = " ".join(feats)
        l_ret_feats.append(feat_r)
    return l_ret_feats


def extra_by_self_feature(l_self_features, l_features):
    '''
    :param l_self_features: self-defined features,
    :param l_features: l_features, a list for feature string. format as . label id cuted_text
    :return: a list for feature string. format as . label id cuted_text
    '''
    #辅助使用自定义特征，将自定义特征加入特征向量
    # 完全使用自定义的特征
    index = esm.Index()
    for feature in l_self_features:
        feature = feature.strip()
        index.enter(feature)
    index.fix()

    l_ret_feats = []
    for s_features in l_features:
        ret = index.query(s_features)
        for item in ret:
            feature = item[1]
            s_features = '%s self_defined_feature_%s' % (s_features, feature)
        l_ret_feats.append(s_features)
    return l_ret_feats
