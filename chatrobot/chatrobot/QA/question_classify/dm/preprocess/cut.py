#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Cutword for sentiment dataset

input format:
    id sentitype text

Usage:
    cut -t [pos] -c [hidden]  -f <file name> --template <template path> --brands <brand path or single brand name>
        -t  ; save pos tag
        -c  ; output <hidden, text cut>, otherwise output <senti,  text cut> by default
        -f  ; input file name
        --template ; template file path
        --brands ; brand list , if brand is a brand name, we will just deal the single word.but a path we will read the path text;
"""

import string
import sys,time
import os, os.path
import logging
#from jieba.norm import norm_cut, norm_seg
from optparse import OptionParser
import chardet

cur_path = os.path.dirname(os.path.abspath(__file__))
jieba_path = '%s/../../common/wcut' % cur_path
sys.path.insert(0, jieba_path)
from jieba.dict_norm import CutWord


def load_template_feature(result_with_flag, posList, lFeatureTemplate, sBrand):
    '''
        add template feature to vector
    '''

    lWords_Flag = result_with_flag.split(" ")
    lAddFeature = []
    lAfterQueue = posList
    lBeforeQueue = {'all':[]}
    
    # key word dict 
    dKeyWords = {}
    iPos = 0
    for sWord_Flag in lWords_Flag:
        
        sFlag = sWord_Flag.split('_')[-1]
        if sFlag == '':
            continue
        
        #delete first word from lAfterQueue
        lAfterQueue[sFlag] = lAfterQueue[sFlag][1:]
        lAfterQueue['all'] = lAfterQueue['all'][1:]
 
        #pre deal
        if len(sWord_Flag.split('_')) < 2:
            continue
        sWord = sWord_Flag.split('_')[0]
        sFlag = sWord_Flag.split('_')[-1]

        if not sFlag in lBeforeQueue:
            lBeforeQueue[sFlag] = []

        if sBrand == sWord:
            for sItem in lFeatureTemplate:
                lFlagNum = sItem.split("_")
                sPosFlag = lFlagNum[0]
                if not sPosFlag in lAfterQueue:
                    lAfterQueue[sPosFlag] = []
                    
                if not sPosFlag in lBeforeQueue:
                    lBeforeQueue[sPosFlag] = []

                if len(lFlagNum) == 2:
                    iNum = int(lFlagNum[1])
                    if iNum > 0:
                        sFeature = 'local_brand_%s' % "_".join(lAfterQueue[sPosFlag][:iNum])
                    else:
                        sFeature = 'local_%s_brand' % "_".join(lBeforeQueue[sPosFlag][iNum:])
                else:
                    iMax, iSmall = (int(lFlagNum[1]), int(lFlagNum[2])) if int(lFlagNum[1]) > int(lFlagNum[2]) else (int(lFlagNum[2]), int(lFlagNum[1]))
                    if iMax * iSmall > 0:
                        if iMax > 0:
                            sFeature = 'local_brand_%s' % "_".join(lAfterQueue[sPosFlag][iSmall - 1:iMax])
                        else:
                            if iMax == -1:
                                sFeature = 'local_%s_brand' % "_".join(lBeforeQueue[sPosFlag][iSmall : ])
                            else:
                                sFeature = 'local_%s_brand' % "_".join(lBeforeQueue[sPosFlag][iSmall : iMax + 1])
                    else:
                        sFeature = 'local_%s_brand_%s' % ("_".join(lBeforeQueue[sPosFlag][iSmall:]), "_".join(lAfterQueue[sPosFlag][:iMax]))
                lAddFeature.append(sFeature)
        
        #add word to lBeforeQueue
        lBeforeQueue[sFlag].append(sWord)
        lBeforeQueue['all'].append(sWord)
        iPos = iPos + 1
     
    #add keyword count feature
    if len(dKeyWords) > 1:
        lAddFeature.append("local_many_keyword")

    return (" ").join(lAddFeature)         

def cut_input_plus(input, sBrand, o_cw):
    '''
    cut a input string, return utf-8 string
    '''
    result = o_cw.cut_seg(input)
    wordsList = []
    wordsPosList = []
    posDict = {'all':[]}
    bIsBrand = False
    sBrand0 = ""
    for w in result:
        if w.word.strip() == '' or w.flag.strip() == '':
            continue
        w.word = w.word.strip().encode('utf8')
        w.flag = w.flag.strip().encode('utf8')
            
        if sBrand == w.word:
            bIsBrand = True
        
        if len(w.word.split(' ')) > 1:
            w.word = "#kong#".join(w.word.split(' '))
            if bIsBrand:
                sBrand0 = w.word
         
        wordsList.append(w.word)
        wordsPosList.append(w.word + '_' + w.flag)
        if not w.flag in posDict:
            posDict[w.flag] = []
        posDict[w.flag].append(w.word)
        posDict['all'].append(w.word)

    words_posFlag = " ".join(wordsPosList)
    words = " ".join(wordsList)
 
    if sBrand0 != "":
        sBrand = sBrand0

    return bIsBrand, words, words_posFlag, posDict, sBrand

def cut_text_plus(content, posFlag, lFeatureTemplate, sBrand, o_cw):

    '''
     cut text and add context feature

    '''

    bIsBrand, result, result_with_flag, posList, sBrand = cut_input_plus(content, sBrand, o_cw)
        

    template_feature = ''
    if bIsBrand and len(lFeatureTemplate):
        template_feature = load_template_feature(result_with_flag, posList, lFeatureTemplate, sBrand)
            
    if bIsBrand and posFlag:
        result = result_with_flag

    return bIsBrand, '%s,%s' % (result,template_feature)

def cut(l_texts =  '', d_text_colname = "", pos_flag = False, l_feature_template = [], special_words = [], industrys = []):

    '''
    :param file_name: file name
    :param pos_flag:  use pos flag or not
    :param l_feature_template: feature template
    :param target: target
    :return:
    '''
    lRes = []
    l_targets = []
    o_cw = CutWord(special_words = special_words, industrys = industrys)
    for line in l_texts:
        fs = line.split('\t')
        label = fs[d_text_colname['label']]
        id = fs[d_text_colname['id']]
        title = fs[d_text_colname['title']]
        abst = fs[d_text_colname['abst']]
        target = fs[d_text_colname['target']]
        text = '%s,%s' % (title, abst)
        s_words = ''
        if len(l_feature_template) == 0 or target == '':
            s_words = cut_input(text, o_cw)
        else:
            bIsBrand, s_words = cut_text_plus(text, pos_flag, l_feature_template, target, o_cw)
        if s_words.strip() == '':
            s_words = 'no_feature'
        res = '%s %s %s' % (label, id, s_words)
        l_targets.append(target)
        lRes.append(res)
    o_cw.release()
    return lRes, l_targets

def cut_input(input, o_cw, flag = False):
    '''
    cut a input string, return utf-8 string
    '''

    result = o_cw.cut_seg(input)
    wordsList = []
    for w in result:
        if w.word.strip() == '' or w.flag.strip() == '':
            continue
        if flag:
            wordsList.append(w.word + '_' + w.flag)
        else:
            wordsList.append(w.word)

    return " ".join(wordsList).encode('utf8')


def cut_text(content):

    '''
     cut text and add context feature

    '''

    result = cut_input(content)

    return result

        
def cut_file(fileName, posFlag, lFeatureTemplate, dBrand):
    '''
    cut from file and output to filename.cut
    '''
    dir, name = os.path.splitext(fileName)
    middle = '_pos' if posFlag else ''
    writer = open( dir + middle + '.cut', 'w')
    reader = open(fileName, 'rb')
 
    reccnt = 0
    #
    # parse the records
    # id label hidden text
    #
    for line in reader:
        #add a id 
        if line[0] == ' ':
            pos0 = line.find(' ')+1
        else:
            pos0 = 0
        pos1 = line.find(' ',pos0)+1
        pos2 = line.find(' ',pos1)+1

        if pos2 > 0:
            label = int(float(line[pos0:pos1-1]))
            stype = int(float(line[pos1:pos2-1]))
            content = line[pos2:-1]

            result, result_with_flag, posList = cut_input(content)
            template_feature = ''
            if len(lFeatureTemplate) and len(dBrand):
                template_feature = load_template_feature(result_with_flag, posList, dBrand, lFeatureTemplate)
            
            if posFlag:
                result = result_with_flag

            writer.write('%d %d '%(label, stype) + result + template_feature + '\n')

        reccnt += 1

    reader.close()
    writer.close()


if __name__=="__main__":
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    # logging configure
    import logging.config
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.DEBUG)
    logger.info("running %s" % ' '.join(sys.argv))

    # cmd argument parser
    usage = 'cut -t [pos] -f <file path> --template <template path> --brands <brand path or single brand name>'
    parser = OptionParser(usage)
    parser.add_option("-f", dest="pathName")
    parser.add_option("-t", dest="type", action="store_true")
    parser.add_option("--template", dest = "templatePath")
    parser.add_option("--brands", dest = "brands")

    opt, args = parser.parse_args()
    if opt.pathName is None:
        logger.error(globals()['__doc__'] % locals())
        sys.exit(1)

    posFlag = False
    if not (opt.type is None):
        posFlag = True
    
    dBrand = {}
    if not opt.brands is None:
       if os.path.exists(opt.brands):
           oReader = open(opt.brands, 'rb')
           for sLine in oReader.readlines():
               dBrand[sLine.strip().lower()] = 1 
       else:
           dBrand[opt.brands.strip().lower()] = 1
 
    lFeatureTemplate = []
    if not opt.templatePath is None:
        if os.path.exists(opt.templatePath):
            oReader = open(opt.templatePath, 'rb')
            for sLine in oReader.readlines():
                lFeatureTemplate.append(sLine.strip())

    arg_name = opt.pathName 
    if os.path.isdir(arg_name):
        for root, dirs, files in os.walk(arg_name):
            #print root, dirs, files
            for file_name in files:
                cut_file( root + '/' + file_name, posFlag, lFeatureTemplate, dBrand)
            break    
    else:
        cut_file( arg_name, posFlag, lFeatureTemplate, dBrand)
