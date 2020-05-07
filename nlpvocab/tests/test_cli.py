# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import os
import shutil
import tempfile
import unittest
from ..cli import _read_content


class TestReadContent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def testTxt(self):
        file_name = os.path.join(self.temp_dir, 'test.txt')
        source_content = u'Test\nТест'
        with open(file_name, 'wb') as f:
            f.write(source_content.encode('utf-8'))

        actual_content = _read_content(file_name)
        self.assertEqual(actual_content, source_content)

    def testGz(self):
        file_name = os.path.join(self.temp_dir, 'test.txt.gz')
        source_content = u'Test\nТест'
        with gzip.open(file_name, 'wb') as f:
            f.write(source_content.encode('utf-8'))

        actual_content = _read_content(file_name)
        self.assertEqual(actual_content, source_content)
