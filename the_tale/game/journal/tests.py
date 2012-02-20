# cpding: utf-8
from django.test import TestCase

from .template import Template, Formatter


class TemplateTest(TestCase):

    def test_external_args_normalization(self):
        f = Formatter(data={'a;b': 'word1', 'd;c': 'word2'})
        self.assertEqual(set(f.data.keys()), set(['a;b', 'c;d']))


    def test_external_initialization(self):
        t = Template('[[h1|args]]')
        self.assertEqual(t.template, '%(e_0)s')
        self.assertEqual(t.externals, [('h1', 'e_0', 'args')])

        t = Template('![[h1|args]] asdasda [[h2|args2]]')
        self.assertEqual(t.template, '!%(e_0)s asdasda %(e_1)s')
        self.assertEqual(t.externals, [('h1', 'e_0', 'args'), ('h2', 'e_1', 'args2')])


    def test_inline_initialization(self):
        t = Template('[[h1|args]{inline1|arg1}{inline2|arg2}]')
        self.assertEqual(t.template, '%(i_0)s')
        self.assertEqual(t.inlines, [ ('h1', 'args', 'i_0', {'arg1': 'inline1', 'arg2': 'inline2'}) ])

        t = Template('![[h1|args]{inline1|arg1}{inline2|arg2}] asdasda [[h2|arg2]{in1|a1}{in2|a2}]')
        self.assertEqual(t.template, '!%(i_0)s asdasda %(i_1)s')
        self.assertEqual(t.inlines, [ ('h1', 'args', 'i_0', {'arg1': 'inline1', 'arg2': 'inline2'}),
                                      ('h2', 'arg2', 'i_1', {'a1': 'in1', 'a2': 'in2'}) ])

    def test_plane_initialization(self):
        t = Template('%(h1)s')
        self.assertEqual(t.template, '%(h1)s')

        t = Template('!%(h1)s asdasda %(h2)s')
        self.assertEqual(t.template, '!%(h1)s asdasda %(h2)s')


    def test_external_format(self):

        f1 = Formatter(data={'args': 'word1', 'args2': 'word2'})

        f2 = Formatter(data={'args': 'drow1', 'args2': 'drow2'})

        t = Template('[[h1|args]]')
        self.assertEqual(t.substitute(h1=f1), 'word1')
        self.assertEqual(t.substitute(h1=f2), 'drow1')

        t = Template('![[h1|args]] asdasda [[h2|args2]]')
        self.assertEqual(t.substitute(h1=f1, h2=f2), '!word1 asdasda drow2')
        self.assertEqual(t.substitute(h1=f2, h2=f1), '!drow1 asdasda word2')


    def test_internal_format(self):

        f1 = Formatter(properties={'prop1': 'word1','prop2': 'word2'})
        f2 = Formatter(properties={'prop1': 'drow1', 'prop2': 'drow2'})

        t = Template('[[h1|prop1]{inline1|word1}{inline2|word2}]')
        self.assertEqual(t.substitute(h1=f1), 'inline1')

        t = Template('[[h1|prop2]{inline1|word1}{inline2|word2}]')
        self.assertEqual(t.substitute(h1=f1), 'inline2')

        t = Template('![[h1|prop1]{inline1|word1}{inline2|word2}] asdasda [[h2|prop2]{inline11|drow1}{inline22|drow2}]')
        self.assertEqual(t.substitute(h1=f1, h2=f2), '!inline1 asdasda inline22')


    def test_plane_format(self):

        f1 = Formatter(data={'args': 'word1', 'args2': 'word2'})

        f2 = Formatter(data={'args': 'drow1', 'args2': 'drow2'})

        t = Template('[[h1|args]] %(number)d')
        self.assertEqual(t.substitute(h1=f1, number=1), 'word1 1')
        self.assertEqual(t.substitute(h1=f2, number=666), 'drow1 666')
