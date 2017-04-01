import os
import yaml
from .aldnoah import (
    Aldnoah, preprocess, strategy, retrieve, answerengine,
    router,
)


def _get_abs_path(path):
    return os.path.normpath(os.path.join(os.getcwd(), path))


debug = True

POKE_DICT_NAME = 'pokedict'
router.register_signs(_get_abs_path('yamls/signs.yaml'))
router.register_aggregate(_get_abs_path('yamls/aggregatefunc.yaml'))
router.register_valuefilter(_get_abs_path('yamls/valuefilter.yaml'))
# router.generate_dic(_get_abs_path(POKE_DICT_NAME))

jieba_processor = preprocess.JiebaProcessor(_get_abs_path(POKE_DICT_NAME))

infoextract_strategy = strategy.InfoExtractStrategy(priority=5)
with open(_get_abs_path('yamls/pattern.yaml'), 'r') as f:
    d = yaml.load(f.read())
    for pattern in d['pair']:
        infoextract_strategy.add_pairpattern(pattern)

django_retrieve = retrieve.DjangoRetrieve()

aldnoah = (Aldnoah()
           .add_preprocessor(jieba_processor)
           .add_strategy(infoextract_strategy)
           .set_retrieve(django_retrieve)
           .set_answereg(answerengine.DjangoAnswerEngine())
           )


def answer(question):
    if question:
        return aldnoah.answer(question)
    else:
        return answer_test()


def answer_test():
    def all(d):
        l = []
        for v in d.values():
            l.extend(v)
        return l
    with open(_get_abs_path('yamls/questions.yaml'), 'r') as f:
        d = yaml.load(f.read())
    # questions = d.get('specific')
    # questions = d.get('aggregate')
    # questions = d.get('sign')
    questions = d.get('test')
    # questions = all(d)
    rs = []
    for q in questions:
        rs.append(aldnoah.answer(q))
    return rs
