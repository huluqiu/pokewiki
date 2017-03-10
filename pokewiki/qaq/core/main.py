import jieba
import jieba.posseg as pseg

jieba.load_userdict('jieba_dic_pokewiki')

questions = [
    '妙蛙种子的属性',
    '属性不为火的宝可梦是',
    '妙蛙种子能学会什么技能',
    '妙蛙种子能学会哪些技能',
    '能学会飞叶快刀的宝可梦有',
    '火属性的宝可梦有',
    '妙蛙种子如何进化',
    '妙蛙种子怎么进化'
]

for q in questions:
    seg_list = pseg.cut(q, HMM=False)
    s = []
    for word, flag in seg_list:
        s.append('%s(%s)' % (word, flag))
    s = ''.join(s)
    print(s)
