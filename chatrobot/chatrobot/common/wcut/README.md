#正常切词,返回一个iteration
from wcut.jieba.norm import norm_cut

#带词性切分
from wcut.jieba.norm import norm_seg
for word in norm_seg(line):
    print word.word,word.flag

#行业字典
{0:新词,2:汽车,7:美妆行业} 目前就三个字典
加载行业字典
from jieba.norm import load_industrydict
load_industrydict([2,7]) 接收行业字典

#结巴不可切分字典,默认自动加载
如果含有空格切割的字典
userdict_special  可以切分任何指定的词 ,主要解决两个词中间有空格等符号

#正常字典,默认自动加载
normalize.dict

#jieba默认字典
一般不改 dict.txt

#计算频率
import jieba.suggest_freq
