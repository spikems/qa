#!/usr/bin/python
# encoding:utf-8

import re
from extract_short_text import ExtractShortText

#
# feature tags
#
FT_TARGET = 'target'
FT_SENT = 'br'
FT_BRAND = 'brand'
FT_ASPECT = 'aspect'
FT_OPINION = 'opinion'
FT_COMP = 'comp'
FT_COMPR = 'comp_r'
FT_OTHER = 'other'
FT_INQUIRE = 'inquire'
FT_WISH = 'wish'
FT_IF = 'if'
FT_NEG = 'neg'
FT_BUT = 'but'
FT_ALTHOUGH = 'although'
FT_AND = 'and'
FT_SO = 'so'

# cutsep to output the feature as "word/tag"
CUTSEP = '/'
FT_MARKER = '#'
FT_SPACE = '_'
#
# feature dict format
#
FEATURETAG = 0
POSTAG = 1
TARGET = 0

# select feature commands
SEL_FTONLY = 0  # only feature tags
SEL_FTCOMBINE = 1  # combine <target, aspect, opinion> pairs
SEL_FTCOMBINE_PLUS = 2  # combine includes target\aspect\opinion\not\but


class PreDeal():
    def __init__(self):
        pass

    def __getfeats(self, content='', seltype=0):

        result = []
        if seltype == SEL_FTONLY:
            # get feature tag only
            items = content.split()
            for _w in items:
                winfo = _w.split(CUTSEP)
                word = winfo[0]
                if word:
                    # tag = winfo[1].split(FT_MARKER)[0]
                    if winfo[1].find(FT_MARKER) > 0:
                        result.append(winfo[1])
        elif seltype == SEL_FTCOMBINE_PLUS:
            sentences = re.split('。|；|;|？|\?|！|!|，|,', content)
            for sentence in sentences:
                hasNeg = False
                # sentence = sentence.replace(FT_SENT, FT_SENT + '。 ')
                items = sentence.split()
                pos = 0
                feats = []
                ft_pos = {}
                for _w in items:
                    winfo = _w.split(CUTSEP)
                    word = winfo[0].strip()
                    if word:
                        # tag = winfo[1].split(FT_MARKER)[0]
                        if winfo[1].find(FT_MARKER) > 0:
                            feats.append(winfo[1])
                            flag = winfo[1]

                            if flag[:-1] == FT_NEG:
                                hasNeg = True

                            if flag[:-1] in (FT_INQUIRE, FT_BUT, FT_ALTHOUGH, FT_BRAND, FT_TARGET, FT_COMPR, FT_NEG,
                                             FT_ASPECT) or flag.startswith(FT_OPINION) or flag.startswith(FT_COMP):
                                feat = flag[:-1]

                                if flag.startswith(FT_OPINION):
                                    feat = FT_OPINION
                                if flag.startswith(FT_COMP):
                                    feat = FT_COMP
                                if not feat in ft_pos:
                                    ft_pos[feat] = []
                                ft_pos[feat].append(pos)
                            pos += 1
                # extract combine feature
                com_feats, deal_feats, del_neg_index = self.extract_combine_feature_plus(feats, ft_pos, hasNeg)
                feats.extend(com_feats)
                feats0 = []
                for i in range(len(feats)):
                    if i in del_neg_index:
                        continue
                    feats0.append(feats[i])
                feats = feats0
                feats = [feat for feat in feats if feat not in deal_feats]

                result.extend(feats)

        elif seltype == SEL_FTCOMBINE:
            sentences = re.split('。|；|;|？|\?|！|!|，|,', content)
            for sentence in sentences:
                s_replace = '%s#' % FT_SENT
                sentence = sentence.replace(s_replace, s_replace + '。')
                items = sentence.split()
                pos = 0
                feats = []
                ft_pos = {}
                for _w in items:
                    winfo = _w.split(CUTSEP)
                    word = winfo[0]
                    if word:
                        # tag = winfo[1].split(FT_MARKER)[0]
                        if winfo[1].find(FT_MARKER) > 0:
                            feats.append(winfo[1])
                            flag = winfo[1]

                            if flag[:-1] in (FT_BRAND, FT_TARGET, FT_ASPECT) or \
                                    flag.startswith(FT_OPINION) or flag.startswith(FT_COMP):
                                feat = flag[:-1]

                                if flag.startswith(FT_OPINION):
                                    feat = FT_OPINION
                                if flag.startswith(FT_COMP):
                                    feat = FT_COMP
                                if not feat in ft_pos:
                                    ft_pos[feat] = []
                                ft_pos[feat].append(pos)
                            pos += 1
                # extract combine feature
                com_feats = self.extract_combine_feature(feats, ft_pos)
                feats.extend(com_feats)
                result.extend(feats)

        return ' '.join(result)

    def extract_combine_feature_plus(self, feats, ft_pos, hasNeg):

        com_feats = []
        del_feats = {}
        del_neg_index = {}

        # compare
        if (FT_COMP in ft_pos or FT_COMPR in ft_pos) and FT_TARGET in ft_pos and FT_OPINION in ft_pos:
            compind0, c_label = (ft_pos[FT_COMP][0], FT_COMP) if FT_COMP in ft_pos else (ft_pos[FT_COMPR][0], FT_COMPR)
            targetind0 = ft_pos[FT_TARGET][0]
            com_feat = '%s_%s' % (c_label, FT_TARGET) if compind0 < targetind0 else '%s_%s' % (FT_TARGET, c_label)
            for pos in ft_pos[FT_OPINION]:
                if pos < compind0:
                    continue
                opinion = feats[pos]
                if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                    del_neg_index[pos - 1] = 1
                    del_feats[opinion] = 1
                    opinion = 'not_%s' % opinion
                com_feat0 = '%s_%s' % (com_feat, opinion)
                del_feats[opinion] = 1
                com_feats.append(com_feat0)

        else:

            if FT_BRAND in ft_pos and FT_OPINION in ft_pos and not FT_TARGET in ft_pos:
                for pos in ft_pos[FT_OPINION]:
                    opinion = feats[pos]
                    if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                        del_neg_index[pos - 1] = 1
                        del_feats[opinion] = 1
                        opinion = 'not_%s' % opinion
                    small = ft_pos[FT_BRAND][0]
                    big = ft_pos[FT_BRAND][-1]
                    for pos_b in ft_pos[FT_BRAND]:
                        com_feat = self.extract_opinion_com_feature(opinion, pos, 'brand', pos_b, (small, big))
                        com_feats.append(com_feat)

            if FT_TARGET in ft_pos and FT_OPINION in ft_pos and not FT_BRAND in ft_pos:
                for pos in ft_pos[FT_OPINION]:
                    opinion = feats[pos]
                    if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                        del_neg_index[pos - 1] = 1
                        del_feats[opinion] = 1
                        opinion = 'not_%s' % opinion
                    small = ft_pos[FT_TARGET][0]
                    big = ft_pos[FT_TARGET][-1]
                    for pos_b in ft_pos[FT_TARGET]:
                        com_feat = self.extract_opinion_com_feature(opinion, pos, 'target', pos_b, (small, big))
                        com_feats.append(com_feat)
        if FT_ASPECT in ft_pos and FT_OPINION in ft_pos:
            for pos in ft_pos[FT_OPINION]:
                opinion = feats[pos]
                if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                    del_neg_index[pos - 1] = 1
                    del_feats[opinion] = 1
                    opinion = 'not_%s' % opinion
                small = ft_pos[FT_ASPECT][0]
                big = ft_pos[FT_ASPECT][-1]
                for pos_a in ft_pos[FT_ASPECT]:
                    com_feat = self.extract_opinion_com_feature(opinion, pos, 'aspect', pos_a, (small, big))
                    com_feats.append(com_feat)
        # neg
        if hasNeg and FT_OPINION in ft_pos:
            for pos in ft_pos[FT_OPINION]:
                opinion = feats[pos]
                if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                    del_neg_index[pos - 1] = 1
                    del_feats[opinion] = 1
                    com_feat = 'not_%s' % opinion
                    com_feats.append(com_feat)

        if (FT_BUT in ft_pos or FT_ALTHOUGH in ft_pos) and FT_OPINION in ft_pos:
            syns, syns_index = (FT_BUT, ft_pos[FT_BUT][0]) if FT_BUT in ft_pos else (
                FT_ALTHOUGH, ft_pos[FT_ALTHOUGH][0])
            for pos in ft_pos[FT_OPINION]:
                opinion = feats[pos]
                if pos > syns_index:
                    if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_NEG:
                        del_neg_index[pos - 1] = 1
                        del_feats[opinion] = 1
                        opinion = 'not_%s' % opinion
                    com_feat = '%s_%s' % (syns, opinion)
                    del_feats[opinion] = 1
                    com_feats.append(com_feat)

        if FT_OPINION in ft_pos:
            for pos in ft_pos[FT_OPINION]:
                opinion = feats[pos]
                if pos - 1 >= 0 and feats[pos - 1][:-1] == FT_INQUIRE:
                    com_feat = 'inquire_%s' % opinion
                    com_feats.append(com_feat)
                elif pos + 1 < len(feats) and feats[pos + 1][:-1] == FT_INQUIRE:
                    com_feat = '%s_inquire' % opinion
                    com_feats.append(com_feat)

        return com_feats, del_feats, del_neg_index

    def extract_opinion_com_feature(self, opinion, pos_opinion, type, type_pos_cur, type_pos_range=(-1, -1)):

        big = type_pos_range[1]
        small = type_pos_range[0]

        if small == big:
            if pos_opinion > type_pos_cur:
                com_feat = '%s_%s' % (type, opinion)
            else:
                com_feat = '%s_%s' % (opinion, type)
        else:
            if pos_opinion > big:
                com_feat = '%s_%s' % (type, opinion)
            elif pos_opinion < small:
                com_feat = '%s_%s' % (opinion, type)
            elif (big - pos_opinion) > (pos_opinion - small):
                com_feat = '%s_%s' % (type, opinion)
            else:
                com_feat = '%s_%s' % (opinion, type)
        return com_feat

    def extract_combine_feature(self, feats, ft_pos):

        com_feats = []
        if FT_OPINION in ft_pos:
            if FT_TARGET in ft_pos and (FT_COMP in ft_pos or FT_COMPR in ft_pos):
                compind0 = ft_pos[FT_COMP][0]
                c_label = feats[compind0]
                targetind0 = ft_pos[FT_TARGET][0]
                com_feat = '%s_%s' % (c_label, FT_TARGET) if compind0 < targetind0 else '%s_%s' % (FT_TARGET, c_label)
                for pos in ft_pos[FT_OPINION]:
                    if pos < compind0:
                        continue
                    opinion = feats[pos]
                    com_feat0 = '%s_%s' % (com_feat, opinion)
                    com_feats.append(com_feat0)
            elif FT_TARGET in ft_pos and FT_BRAND not in ft_pos:
                for pos in ft_pos[FT_OPINION]:
                    opinion = feats[pos]
                    com_feat = '%s_%s' % (FT_TARGET, opinion)
                    com_feats.append(com_feat)
            elif FT_BRAND in ft_pos and FT_TARGET not in ft_pos and not (FT_COMP in ft_pos or FT_COMPR in ft_pos):
                for pos in ft_pos[FT_OPINION]:
                    opinion = feats[pos]
                    com_feat = '%s_%s' % (FT_BRAND, opinion)
                    com_feats.append(com_feat)

        return com_feats

    def __gettag(self, tag):
        return '%s#' % tag

    def __getword(self, tag, word):
        return '%s#%s' % (tag, word.replace(' ', '_'))

    def __maketag(self, sent, wordmap, target):

        result = []
        # cut

        words = sent.split(' ')

        output = ''
        for word in words:
            # all convert to lower case

            if word.strip() == '...':
                continue
            if word in wordmap:
                # check the feature tag
                if wordmap[word][FEATURETAG] == FT_BRAND:
                    # check if the brand is target
                    if (target in word) or (word in target):
                        output = self.__gettag(FT_TARGET)
                    else:
                        output = self.__gettag(FT_BRAND)
                elif wordmap[word][FEATURETAG] in (FT_ASPECT, FT_OPINION, FT_COMP, FT_OTHER):
                    output = self.__getword(wordmap[word][FEATURETAG], word)
                else:
                    output = self.__gettag(wordmap[word][FEATURETAG])

                # append this feature
                feature = '%s%s%s' % (word, CUTSEP, output)
                result.append(feature)
            else:
                feature = '%s%sposttag' % (word, CUTSEP)
                result.append(feature)
        if output:
            result.append('...' + CUTSEP + self.__gettag(FT_SENT))

        return ' '.join(result)

    def getSent(self, target, sent, iRange=200):
        sent = ExtractShortText().extract_short_text(target, sent, iRange)
        return sent.encode('utf-8')

    def getModelFeats(self, sent, wordmap, target, seltype=1):

        result = ''
        result = self.__maketag(sent, wordmap, target)
        result = self.__getfeats(content=result, seltype=seltype)
        if result.find(FT_OPINION) == -1 or result.find(FT_TARGET) == -1:
            result = ''
        return result

    def run(self, sent, wordmap, target, seltype=2):
        result = ''
        iRange = 200
        sent = ExtractShortText().extract_short_text(target, sent, iRange)
        result = self.__maketag(sent.encode('utf-8'), wordmap, target)
        result = self.__getfeats(content=result, seltype = seltype)
        if result.find(FT_OPINION) == -1 or result.find(FT_TARGET) == -1:
            result = ''
        return result


if __name__ == '__main__':
    sent = '本田 汽车 比 召回 凯美瑞 不好 开'
    wordmap = {'召回': ['opinion'], '本田': ['brand'], '比': ['comp']}
    target = '本田'
    print PreDeal().run(sent, wordmap, target)
