#encodig:utf-8

algorithm_conf = {

    'LR-5' : {
        'classifier' : 'lrl1',
        'vectorizer_type' : 'count',
        'balanced' : True,
        'debug' : True
    },
    'xgb': {
        'classifier': 'xgb',
        'vectorizer_type': 'count',
        'balanced': False,
        'debug': True,
    },

}