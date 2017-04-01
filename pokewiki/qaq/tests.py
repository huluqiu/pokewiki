from django.test import TestCase
from qaq import aldnoahpoke


class AldnoahTestCase(TestCase):
    def setup(self):
        pass

    def test_answer(self):
        r = aldnoahpoke.answer('皮卡丘的属性')
        self.assertEqual(r['type'], 'specific')
