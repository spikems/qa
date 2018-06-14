#encoding:utf-8
from .question_classify.classify import classify
from .preprocess.preprocess import Preprocess
from .search.query_word import Query
from .keyword.QA_Extract import NewQAExtractWord
from .preprocess.sent_vec import sent_vec
from common_code import keywords,replace_product,compute_length
import json
import logging
logger = logging.getLogger('qa_run')
import logging.config
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
# logger.info('task is start')


def run(question, context=''):

    question = question.encode('utf-8').strip() if type(question) == unicode  else question.strip()
    # context = context.encode('utf-8').strip() if type(context) == unicode  else context.strip()

    #1. preprocess
    # rule, s_new_question = Preprocess().run(question, context)
    # if not rule:
    #      s_answer = '该问题不规范，请调整后继续查询'
    #      return json.dumps([])
    if not 4<len(question.decode('utf-8','ignore'))<50:
        s_answer = '该问题字数少于5或者大于50'
        logger.info(s_answer)
        return json.dumps(s_answer)


    #2. question classify
    question_type = classify(question)
    logger.info('question_type:%s'%question_type)

    #3. keyword extract
    o_extract = NewQAExtractWord()
    dic = o_extract.extract_master(question)
    for k,v in dic.items():
        if isinstance(v,list):
            logger.info('%s:%s'%(k,' '.join(v)))
        else:
            logger.info('%s:%s'%(k,v))

    #compute sent vec
    replace_product(dic)
    # dic['sentvec'] = sent_vec(dic['question'])
    # kwords = keywords(dic)
    # if kwords:    #if no keywords
    #     dic['keyword_vec'] = sent_vec(kwords)
    # else:
    #     dic['keyword_vec'] = None
    # print '****************', dic

    #4. search
    # dic = {"question": "大众油耗怎么样", "product": "途观"}
    l_answers = Query().run(dic)
    j_res = json.dumps(l_answers)
    return j_res







