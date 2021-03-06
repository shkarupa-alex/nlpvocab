# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import tempfile
import unittest
from .. import Vocabulary


class TestVocabulary(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def testEmpty(self):
        vocab = Vocabulary()
        self.assertEqual([], vocab.tokens())

    def testFit(self):
        vocab = Vocabulary()
        vocab.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        self.assertEqual([' ', '1', '2', '\t', '\n', '.', '3'], vocab.tokens())

    def test_split_size_1(self):
        vocab = Vocabulary()
        vocab.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        high, low = vocab.split_by_size(10)
        self.assertEqual([' ', '1', '2', '\t', '\n', '.', '3'], high.tokens())
        self.assertIsInstance(low, Vocabulary)
        self.assertEqual([], low.tokens())

    def test_split_size_2(self):
        vocab = Vocabulary()
        vocab.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        high, low = vocab.split_by_size(3)
        self.assertEqual([' ', '1', '2'], high.tokens())
        self.assertIsInstance(low, Vocabulary)
        self.assertEqual(['\t', '\n', '.', '3'], low.tokens())

    def test_split_frequency_1(self):
        vocab = Vocabulary()
        vocab.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        high, low = vocab.split_by_frequency(1)
        self.assertEqual([' ', '1', '2', '\t', '\n', '.', '3'], high.tokens())
        self.assertIsInstance(low, Vocabulary)
        self.assertEqual([], low.tokens())

    def test_split_frequency_2(self):
        vocab = Vocabulary()
        vocab.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        high, low = vocab.split_by_frequency(2)
        self.assertEqual([' ', '1', '2'], high.tokens())
        self.assertIsInstance(low, Vocabulary)
        self.assertEqual(['\t', '\n', '.', '3'], low.tokens())

    def test_save_load_pickle(self):
        vocab_filename = os.path.join(self.temp_dir, 'vocab.pkl')

        vocab1 = Vocabulary()
        vocab1.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', '3', '.'])
        vocab1.save(vocab_filename)

        vocab2 = Vocabulary.load(vocab_filename)
        self.assertEqual(vocab1.tokens(), vocab2.tokens())

        vocab1, _ = vocab1.split_by_frequency(2)
        self.assertNotEqual(vocab1.tokens(), vocab2.tokens())

    def test_save_tsv(self):
        vocab_filename = os.path.join(self.temp_dir, 'vocab.tsv')

        vocab1 = Vocabulary()
        vocab1.update(['1', ' ', '2', ' ', '1', '\n', '2', '\t', u'а', '.'])
        vocab1.save(vocab_filename, format=Vocabulary.FORMAT_TSV_WITH_HEADERS)

        expected = u'token\tfrequency\n\\u0020\t2\n1\t2\n2\t2\n\\u0009\t1\n\\u000a\t1\n.\t1\nа\t1\n'
        with open(vocab_filename, 'rb') as vf:
            result = vf.read().decode('utf-8')
        self.assertEqual(expected, result)

        vocab2 = Vocabulary.load(vocab_filename, format=Vocabulary.FORMAT_TSV_WITH_HEADERS)
        self.assertEqual(vocab1.tokens(), vocab2.tokens())

        vocab1, _ = vocab1.split_by_frequency(2)
        self.assertNotEqual(vocab1.tokens(), vocab2.tokens())

    def test_add(self):
        vocab1 = Vocabulary(['1', ' ', '2', ' ', '1'])
        vocab2 = Vocabulary(['\n', '2', '\t', '3', '.'])
        vocab3 = vocab1 + vocab2
        self.assertIsInstance(vocab3, Vocabulary)
        self.assertEqual([' ', '1', '2', '\t', '\n', '.', '3'], vocab3.tokens())
