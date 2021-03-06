import unittest
from . import urimanager


class UrimanagerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_schema(self):
        uri = 'qaq://Pokemon:name'
        schema = urimanager.schema(uri)
        self.assertEqual(schema, 'qaq')

    def test_setschema(self):
        uri = 'qaq://Pokemon:name'
        uri = urimanager.setschema(uri, 'newqaq')
        self.assertEqual(uri, 'newqaq://Pokemon:name')

    def test_removeschema(self):
        uri = 'qaq://Pokemon:name'
        uri = urimanager.removeschema(uri)
        self.assertEqual(uri, 'Pokemon:name')

    def test_separate(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.separate(uri)
        self.assertTupleEqual(s, ('qaq://Pokemon:name', '', ''))

        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.separate(uri)
        self.assertTupleEqual(s, ('qaq://Pokemon:name', '=', '皮卡丘'))

        uri = 'qaq://Pokemon:name/forms:name/types:name'
        s = urimanager.separate(uri)
        self.assertTupleEqual(s, ('qaq://Pokemon:name/forms:name/types:name', '', ''))

        uri = 'qaq://Pokemon:name/forms:name/types:name=火'
        s = urimanager.separate(uri)
        self.assertTupleEqual(s, ('qaq://Pokemon:name/forms:name/types:name', '=', '火'))

        uri = 'qaq://Pokemon:name/moves:name.count=90'
        s = urimanager.separate(uri)
        self.assertTupleEqual(s, ('qaq://Pokemon:name/moves:name.count', '=', '90'))

        uri = 'qaq://Pokemon:name/moves:name.count=90'
        s = urimanager.separate(uri, showextensions=False)
        self.assertTupleEqual(s, ('qaq://Pokemon:name/moves:name', '=', '90'))

        uri = 'qaq://Pokemon:name'
        s = urimanager.separate(uri, showschema=False, showindex=False)
        self.assertTupleEqual(s, ('Pokemon/name', '', ''))

        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.separate(uri, showschema=False, showindex=False)
        self.assertTupleEqual(s, ('Pokemon/name', '=', '皮卡丘'))

        uri = 'qaq://Pokemon:name/forms:name/types:name'
        s = urimanager.separate(uri, showschema=False, showindex=False)
        self.assertTupleEqual(s, ('Pokemon/forms/types/name', '', ''))

        uri = 'qaq://Pokemon:name/forms:name/types:name=火'
        s = urimanager.separate(uri, showschema=False, showindex=False)
        self.assertTupleEqual(s, ('Pokemon/forms/types/name', '=', '火'))

        uri = 'qaq://Pokemon:name/forms:name/types:name.count'
        s = urimanager.separate(uri, showschema=False, showindex=False, showextensions=False)
        self.assertTupleEqual(s, ('Pokemon/forms/types/name', '', ''))

    def test_path(self):
        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.path(uri)
        self.assertEqual(s, 'qaq://Pokemon:name')

        uri = 'qaq://Pokemon:name/forms:name/types:name=火'
        s = urimanager.path(uri)
        self.assertEqual(s, 'qaq://Pokemon:name/forms:name/types:name')

        uri = 'qaq://Pokemon:name/moves:name.count=80'
        s = urimanager.path(uri, showindex=False, showextensions=False)
        self.assertEqual(s, 'qaq://Pokemon/moves/name')

    def test_basename(self):
        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.basename(uri)
        self.assertEqual(s, 'Pokemon:name')

        uri = 'qaq://Pokemon:name/moves:name.count=80'
        s = urimanager.basename(uri, showextensions=False)
        self.assertEqual(s, 'moves:name')

        uri = 'qaq://Pokemon:name/moves:name.count=80'
        s = urimanager.basename(uri, showindex=False, showextensions=False)
        self.assertEqual(s, 'moves')

    def test_setbasename(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.setbasename(uri, 'basename')
        self.assertEqual(s, 'qaq://basename')

        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.setbasename(uri, 'basename')
        self.assertEqual(s, 'qaq://basename=皮卡丘')

        uri = 'qaq://Pokemon:name/moves:name.count'
        s = urimanager.setbasename(uri, 'basename')
        self.assertEqual(s, 'qaq://Pokemon:name/basename')

        uri = 'qaq://Pokemon:name/moves:name.count=20'
        s = urimanager.setbasename(uri, 'basename')
        self.assertEqual(s, 'qaq://Pokemon:name/basename=20')

    def test_dirname(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.dirname(uri)
        self.assertEqual(s, '')

        uri = 'qaq://Pokemon:name/moves:name/power'
        s = urimanager.dirname(uri)
        self.assertEqual(s, 'qaq://Pokemon:name/moves:name')

    def test_sign(self):
        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.sign(uri)
        self.assertEqual(s, '=')

        uri = 'qaq://Pokemon:name/forms:name/types:name=火'
        s = urimanager.sign(uri)
        self.assertEqual(s, '=')

    def test_value(self):
        uri = 'qaq://Pokemon:name=皮卡丘'
        s = urimanager.value(uri)
        self.assertEqual(s, '皮卡丘')

        uri = 'qaq://Pokemon:name/forms:name/types:name=火'
        s = urimanager.value(uri)
        self.assertEqual(s, '火')

    def test_related(self):
        uri1 = 'qaq://Pokemon:name'
        uri2 = 'qaq://Pokemon:name/moves:name'
        s = urimanager.related(uri1, uri2)
        self.assertTrue(s)

        uri1 = 'qaq://Pokemon:name'
        uri2 = 'qaq://Move:name'
        s = urimanager.related(uri1, uri2)
        self.assertFalse(s)

    def test_urilen(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.urilen(uri)
        self.assertEqual(s, 1)

        uri = 'qaq://Pokemon:name/moves:name'
        s = urimanager.urilen(uri)
        self.assertEqual(s, 2)

    def test_modelname(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.modelname(uri)
        self.assertEqual(s, 'Pokemon')

    def test_append(self):
        uri = ''
        s = urimanager.append(uri, path='moves:name')
        self.assertEqual(s, 'moves:name')

        uri = 'qaq://Pokemon:name'
        s = urimanager.append(uri, path='moves:name')
        self.assertEqual(s, 'qaq://Pokemon:name/moves:name')

        s = urimanager.append(uri, path='moves:name', sign='=')
        self.assertEqual(s, 'qaq://Pokemon:name/moves:name=')

        s = urimanager.append(uri, path='moves:name', sign='=', value='十万伏特')
        self.assertEqual(s, 'qaq://Pokemon:name/moves:name=十万伏特')

    def test_index(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.index(uri)
        self.assertEqual(s, 'name')

        s = urimanager.index(uri)
        self.assertEqual(s, 'name')
        uri = 'qaq://Pokemon:name/moves:name'

    def test_setindex(self):
        uri = 'qaq://Pokemon'
        s = urimanager.setindex(uri, 'name')
        self.assertEqual(s, 'qaq://Pokemon:name')

    def test_attribute_extensions(self):
        uri = 'qaq://Pokemon:name.count'
        s = urimanager.basename(uri)
        self.assertEqual(s, 'Pokemon:name.count')
        s = urimanager.attribute_extensions(uri)
        self.assertListEqual(s, ['count'])

        uri = 'qaq://Pokemon:name/moves:name.count.max'
        s = urimanager.attribute_extensions(uri)
        self.assertListEqual(s, ['count', 'max'])

        uri = 'qaq://Pokemon:name/moves:name.count=90'
        s = urimanager.attribute_extensions(uri)
        self.assertListEqual(s, ['count'])

    def test_set_attribute_extension(self):
        uri = 'qaq://Pokemon:name'
        s = urimanager.set_attribute_extension(uri, 'count')
        self.assertEqual(s, 'qaq://Pokemon:name.count')
