import os
from .aldnoah import (
    Aldnoah, JiebaProcessor, InfoExtractStrategy,
    DjangoRetrieve, DjangoAnswerEngine,
    router
)


def _get_abs_path(path):
    return os.path.normpath(os.path.join(os.getcwd(), path))


POKE_DICT_NAME = 'pokedict'
# router.register(_get_abs_path('map.yaml'))
# router.generate_dic(_get_abs_path(POKE_DICT_NAME))

aldnoah = (Aldnoah()
           .add_preprocessor(JiebaProcessor(_get_abs_path(POKE_DICT_NAME)))
           .add_strategy(InfoExtractStrategy(priority=5))
           .set_retrieve(DjangoRetrieve())
           .set_answereg(DjangoAnswerEngine())
           )


def answer(question):
    return aldnoah.answer(question)


def answer_test():
    questions = []
    rs = []
    with open(_get_abs_path('questions'), 'r') as f:
        questions = f.readlines()
        questions = list(map(lambda n: n.strip(), questions))

    for q in questions:
        rs.append(answer(q))
    return rs
