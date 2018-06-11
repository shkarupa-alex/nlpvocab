from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from setuptools import setup

setup(
    name='nlpvocab',
    version='1.0.0',
    description='Frequency vocabulary for NLP purposes',
    url='https://github.com/shkarupa-alex/nlpvocab',
    author='Shkarupa Alex',
    author_email='shkarupa.alex@gmail.com',
    license='MIT',
    packages=['nlpvocab'],
    test_suite='nose.collector',
    tests_require=['nose']
)
