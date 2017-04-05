from django.test import TestCase
from qaq import aldnoahpoke
from collections import Counter


class AldnoahTestCase(TestCase):

    def _compare(self, x, y):
        return Counter(x) == Counter(y)

    def _formatter(self, l):
        return [(e['uri'], e['flag']) for e in l]

    def _test_answer(self, question, except_type, except_uris, except_query):
        answer = aldnoahpoke.answer(question)
        uris = self._formatter(answer['cells'])
        middle = answer['query']['middle']
        target = self._formatter(answer['query']['target'])
        condition = self._formatter(answer['query']['condition'])
        qtype = answer['type']
        self.assertListEqual(uris, except_uris)
        # self.assertTrue(self._compare(uris, except_uris))
        # self.assertTrue(self._compare(middle, except_query['middle']))
        # self.assertTrue(self._compare(target, except_query['target']))
        # self.assertTrue(self._compare(condition, except_query['condition']))

    def setUp(self):
        pass

    def test_answer_entity_attribute(self):
        question = '皮卡丘的英文名'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/name_en', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/name_en', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_attribute_double(self):
        question = '皮卡丘的英文名和日文名'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/name_en', 'wa'),
            ('qaq://Pokemon:name/name_jp', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/name_en', ''),
                ('qaq://Pokemon:name/name_jp', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_attribute_recursive(self):
        question = '皮卡丘的属性'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/forms:name/types:name', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/forms:name/types:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_attribute_recursive_double(self):
        question = '皮卡丘的属性和身高'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/forms:name/types:name', 'wa'),
            ('qaq://Pokemon:name/forms:name/height', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/forms:name/types:name', ''),
                ('qaq://Pokemon:name/forms:name/height', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_condition_attribute(self):
        question = '皮卡丘有哪些电系技能'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/moves:name/type:name=电', 'wp'),
            ('qaq://Pokemon:name/moves:name', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/moves:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
                ('qaq://Pokemon:name/moves:name/type:name=电', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_condition_entity(self):
        question = '威力为80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_exclude_condition_entity(self):
        question = '威力不为80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power!=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power!=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_condition_recursive_entity(self):
        question = '有静电特性的的宝可梦'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/forms:name/abilities:name@>静电', 'wp'),
            ('qaq://Pokemon:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/forms:name/abilities:name@>静电', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_exclude_condition_recursive_entity(self):
        question = '没有静电特性的的宝可梦'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/forms:name/abilities:name!@>静电', 'wp'),
            ('qaq://Pokemon:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/forms:name/abilities:name!@>静电', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_wav_entity(self):
        question = '变化技能有哪些'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/kind:name=变化', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/kind:name=变化', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_relation_entity(self):
        question = '皮卡丘能学会什么技能'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/moves:name', 'wr'),
            ('qaq://Pokemon:name/moves:name', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/moves:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_relation_entityindex_entity(self):
        question = '谁能学会十万伏特'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/moves:name', 'wr'),
            ('qaq://Pokemon:name/moves:name=十万伏特', 'wp'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/moves:name=十万伏特', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_double_entityindex_attribute(self):
        question = '十万伏特和飞叶快刀的属性是啥'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name=十万伏特', 'wi'),
            ('qaq://Move:name=飞叶快刀', 'wi'),
            ('qaq://Move:name/type:name', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name/type:name', ''),
            ],
            'condition': [
                ('qaq://Move:name=十万伏特', ''),
                ('qaq://Move:name=飞叶快刀', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_double_condition_entity(self):
        question = '属性是水和火的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/type:name=水', 'wp'),
            ('qaq://Move:name/type:name=火', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/type:name=水', ''),
                ('qaq://Move:name/type:name=火', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_attribute_sign_entity(self):
        question = '威力等于80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力大于80的技能有'
        except_uris = [
            ('qaq://Move:name/power>80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power>80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力小于80的技能有'
        except_uris = [
            ('qaq://Move:name/power<80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power<80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_exclude_attribute_sign_entity(self):
        question = '威力不等于80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power!=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power!=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力不大于80的技能有'
        except_uris = [
            ('qaq://Move:name/power!>80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power!>80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力不小于80的技能有'
        except_uris = [
            ('qaq://Move:name/power!<80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power!<80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_attribute_combine_sign_entity(self):
        question = '威力大于等于80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power>=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power>=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力小于等于80的技能有'
        except_uris = [
            ('qaq://Move:name/power<=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power<=80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_exclude_attribute_combine_sign_entity(self):
        question = '威力不大于等于80的技能有'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power!>=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
            ],
            'condition': [
                ('qaq://Move:name/power!>=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力不小于等于80的技能有'
        except_uris = [
            ('qaq://Move:name/power!<=80', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query['condition'] = [
            ('qaq://Move:name/power!<=80', ''),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_count_entity(self):
        question = '宝可梦的数量'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name.count', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name', 'count'),
            ],
            'condition': []
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '有多少宝可梦'
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_count_attribute(self):
        question = '皮卡丘技能的数量'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/moves:name.count', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/moves:name', 'count'),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '皮卡丘有多少技能'
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_count_condition_entity(self):
        question = '技能数量为80的宝可梦'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/moves:name.count=80', 'wp'),
            ('qaq://Pokemon:name', 'we'),
        ]
        except_query = {
            'middle': [
                ('qaq://Pokemon:name/moves:name', 'count'),
            ],
            'target': [
                ('qaq://Pokemon:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/count_moves=80', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '哪个宝可梦有80个技能'
        except_uris = [
            ('qaq://Pokemon:name', 'we'),
            ('qaq://Pokemon:name/moves:name.count=80', 'wp'),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_max_attribute(self):
        question = '威力最大的技能'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power.max', 'wa'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
                ('qaq://Move:name/power', ''),
            ],
            'condition': [
                ('qaq://Move:name/power', 'max'),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '威力最大值'
        except_uris = [
            ('qaq://Move:name/power.max', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name/power', 'max'),
            ],
            'condition': [
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_avg_attribute(self):
        question = '威力平均值'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power.avg', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name/power', 'avg'),
            ],
            'condition': []
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '技能威力的平均值'
        except_uris = [
            ('qaq://Move:name', 'we'),
            ('qaq://Move:name/power.avg', 'wa'),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_entityindex_max_condition_attribute(self):
        question = '皮卡丘威力最大的技能'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/moves:name/power.max', 'wa'),
            ('qaq://Pokemon:name/moves:name', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/moves:name', ''),
                ('qaq://Pokemon:name/moves:name/power', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
                ('qaq://Pokemon:name/moves:name/power', 'max'),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_max_attribute_entity(self):
        question = '威力最大的水属性技能'
        except_type = 'specific'
        except_uris = [
            ('qaq://Move:name/power.max', 'wa'),
            ('qaq://Move:name/type:name=水', 'wp'),
            ('qaq://Move:name', 'we'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Move:name', ''),
                ('qaq://Move:name/power', ''),
            ],
            'condition': [
                ('qaq://Move:name/power', 'max'),
                ('qaq://Move:name/type:name=水', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_max_count_condition_entity(self):
        question = '技能数量最多的宝可梦'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/moves:name.count.max', 'wa'),
            ('qaq://Pokemon:name', 'we'),
        ]
        except_query = {
            'middle': [
                ('qaq://Pokemon:name/moves:name', 'count'),
            ],
            'target': [
                ('qaq://Pokemon:name', ''),
                ('qaq://Pokemon:name/count_moves', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/count_moves', 'max'),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

        question = '哪个宝可梦技能最多'
        except_uris = [
            ('qaq://Pokemon:name', 'we'),
            ('qaq://Pokemon:name/moves:name.count.max', 'wa'),
        ]
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_func_attribute(self):
        question = '皮卡丘的种族值'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/forms:name/stats.species', 'wa'),
        ]
        except_query = {
            'middle': [],
            'target': [
                ('qaq://Pokemon:name/forms:name/stats', 'species'),
            ],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_func_condition_entity(self):
        question = '种族值为500的宝可梦'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/forms:name/stats.species=500', 'wp'),
            ('qaq://Pokemon:name', 'we'),
        ]
        except_query = {
            'middle': [
                ('qaq://Pokemon:name/forms:name/stats', 'species'),
            ],
            'target': [
                ('qaq://Pokemon:name', ''),
            ],
            'condition': [
                ('qaq://Pokemon:name/species_stats=500', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_avg_func(self):
        question = '平均种族值'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/forms:name/stats.species.avg', 'wa'),
        ]
        except_query = {
            'middle': [
                ('qaq://Pokemon:name/forms:name/stats', 'species'),
            ],
            'target': [
                ('qaq://Pokemon:name/species_stats', 'avg'),
            ],
            'condition': []
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_max_func(self):
        question = '最大种族值'
        except_type = 'specific'
        except_uris = [
            ('qaq://Pokemon:name/forms:name/stats.species.max', 'wa'),
        ]
        except_query = {
            'middle': [
                ('qaq://Pokemon:name/forms:name/stats', 'species'),
            ],
            'target': [
                ('qaq://Pokemon:name/species_stats', 'max'),
            ],
            'condition': []
        }
        self._test_answer(question, except_type, except_uris, except_query)

    def test_answer_bool(self):
        question = '皮卡丘的特性有静电'
        except_type = 'bool'
        except_uris = [
            ('qaq://Pokemon:name=皮卡丘', 'wi'),
            ('qaq://Pokemon:name/forms:name/abilities:name@>静电', 'wp')
        ]
        except_query = {
            'middle': [],
            'target': [],
            'condition': [
                ('qaq://Pokemon:name=皮卡丘', ''),
                ('qaq://Pokemon:name/forms:name/abilities:name@>静电', ''),
            ]
        }
        self._test_answer(question, except_type, except_uris, except_query)
