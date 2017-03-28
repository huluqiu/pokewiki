import os
from .aldnoah import (
    Aldnoah, preprocess, strategy, retrieve, answerengine,
    router,
)


def _get_abs_path(path):
    return os.path.normpath(os.path.join(os.getcwd(), path))


debug = True

POKE_DICT_NAME = 'pokedict'
# router.register(_get_abs_path('map.yaml'))
# router.generate_dic(_get_abs_path(POKE_DICT_NAME))

aldnoah = (Aldnoah()
           .add_preprocessor(preprocess.JiebaProcessor(_get_abs_path(POKE_DICT_NAME)))
           .add_strategy(strategy.InfoExtractStrategy(priority=5))
           .set_retrieve(retrieve.DjangoRetrieve())
           .set_answereg(answerengine.DjangoAnswerEngine())
           )


def answer(question):
    if question:
        return aldnoah.answer(question)
    else:
        return answer_test()


def answer_test():
    questions = []
    rs = []
    with open(_get_abs_path('questions'), 'r') as f:
        questions = f.readlines()
        questions = list(map(lambda n: n.strip(), questions))

    for q in questions:
        rs.append(aldnoah.answer(q))
    return rs
