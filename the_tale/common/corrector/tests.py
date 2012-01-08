# coding: utf-8

import unittest

from .corrector import Marker, Corrector

class TestMarker(unittest.TestCase):

    def test_full(self):
        m = Marker(u'![hero:uuid][a;b;c][dependence2;dependence1]!')
        self.assertEqual(m.uuid, 'uuid')
        self.assertEqual(m.name, u'hero')
        self.assertEqual(m.attrs, set([u'a', u'b', u'c']))
        self.assertEqual(m.dependences, [u'dependence2', 'dependence1'])

    def test_missing_uuid(self):
        m = Marker(u'![hero:][a;c;b]!')
        self.assertEqual(m.uuid, None)
        self.assertEqual(m.name, u'hero')
        self.assertEqual(m.attrs, set([u'a', u'b', u'c']))
        self.assertEqual(m.dependences, [])
                   
    def test_missing_dependences(self):
        m = Marker(u'![hero][a;c;b]!')
        self.assertEqual(m.uuid, None)
        self.assertEqual(m.name, u'hero')
        self.assertEqual(m.attrs, set([u'a', u'b', u'c']))
        self.assertEqual(m.dependences, [])

    def test_missing_attrs(self):
        m = Marker(u'![hero]!')
        self.assertEqual(m.uuid, None)
        self.assertEqual(m.name, u'hero')
        self.assertEqual(m.attrs, set())
        self.assertEqual(m.dependences, [])


class TestCorrector(unittest.TestCase):

    def test_base(self):
        c = Corrector(u'![hero]! попросили доставить ![object]! в ![place]!')
        self.assertEqual(c.templated_text, u'%(m_0)s попросили доставить %(m_1)s в %(m_2)s')
        self.assertEqual(c.markers['m_0'].name, 'hero')
        self.assertEqual(c.markers['m_1'].name, 'object')
        self.assertEqual(c.markers['m_2'].name, 'place')

    def test_substitute_base(self):
        c = Corrector(u'![hero][вн]! попросили доставить ![object][вн]! в ![place][вн]!')       
        substitute = c.substitute({'hero': u'герой',
                                   'object': u'письмо',
                                   'place': u'деревня'})
        self.assertEqual(substitute, u'героя попросили доставить письмо в деревню')

    def test_dependences(self):
        c = Corrector(u'![characteristic][][h1]! ![hero:h1][вн]!')       
        substitute = c.substitute({'hero': u'герой', 'characteristic': u'красивый'})
        self.assertEqual(substitute, u'красивого героя')

        c = Corrector(u'![characteristic][][h1]! ![hero:h1][вн]!')       
        substitute = c.substitute({'hero': u'герой', 'characteristic': u'слабый'})
        self.assertEqual(substitute, u'слабого героя')

        c = Corrector(u'![characteristic][][h1]! ![hero:h1][вн]!')       
        substitute = c.substitute({'hero': u'фея', 'characteristic': u'слабый'})
        self.assertEqual(substitute, u'слабую фею')

    def test_inline(self):
        c = Corrector(u'![hero:h1]! ![доставить][прш][h1]! в срок')
        substitute = c.substitute({'hero': u'Джульета'})
        self.assertEqual(substitute, u'Джульета доставила в срок')

        c = Corrector(u'![hero:h1]! ![доставил][][h1]! в срок')
        substitute = c.substitute({'hero': u'Джульета'})
        self.assertEqual(substitute, u'Джульета доставила в срок')


