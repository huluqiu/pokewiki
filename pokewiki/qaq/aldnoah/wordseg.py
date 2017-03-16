import jieba
import jieba.posseg as pseg
import os
from pathlib import PurePath


def generatedic():
    user_dic = os.path.join(PurePath(os.path.realpath(__file__)).parent, 'jieba_dic_pokewiki')
    return user_dic


jieba.load_userdict(generatedic())


def tag(text):
    cuts = pseg.cut(text, HMM=False)
    return list(cuts)
