from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import gzip
import logging
import os
import unicodedata
from .vocab import Vocabulary


def _read_content(file_name, unicode_norm=None, lower_case=None):
    try:
        content = ''
        if file_name.endswith('.txt'):
            with open(file_name, 'rb') as f:
                content = f.read().decode('utf-8')

        if file_name.endswith('.txt.gz'):
            with gzip.open(file_name, 'rb') as f:
                content = f.read().decode('utf-8')

        if not len(content):
            logging.warning('Skipping {}'.format(file_name))
            return ''

        if unicode_norm and 'NONE' != unicode_norm:
            content = unicodedata.normalize(unicode_norm, content)

        if lower_case:
            content = content.lower()

        return content
    except Exception as e:
        logging.error(e)
        logging.warning('Skipping {}'.format(file_name))

    return ''


def count_tokens(split_func, item_name, unicode_norm=None, lower_case=None):
    parser = argparse.ArgumentParser(
        description='Build {} frequency vocabulary from text documents'.format(item_name))
    parser.add_argument(
        'src_path',
        type=str,
        help='Path to directory with text files or path to single file')
    parser.add_argument(
        'vocab_file',
        type=str,
        help='Output vocabulary file')
    parser.add_argument(
        '--file_format',
        choices=[
            Vocabulary.FORMAT_BINARY_PICKLE,
            Vocabulary.FORMAT_TSV_WITH_HEADERS,
            Vocabulary.FORMAT_TSV_WITHOUT_HEADERS
        ],
        default=Vocabulary.FORMAT_TSV_WITH_HEADERS,
        help='Output file type')
    if unicode_norm is None:
        parser.add_argument(
            '--unicode_norm',
            choices=['NONE', 'NFC', 'NFKC', 'NFD', 'NFKD'],
            default='NONE',
            help='Normalize unicode')
    if lower_case is None:
        parser.add_argument(
            '--lower_case',
            action='store_true',
            help='Lowercase {}s'.format(item_name))
    parser.add_argument(
        '-batch_size',
        type=int,
        default=100,
        help='Minimum frequency to leave {} in vocabulary'.format(item_name))
    parser.add_argument(
        '-min_freq',
        type=int,
        default=1,
        help='Minimum frequency to leave {} in vocabulary'.format(item_name))

    argv, _ = parser.parse_known_args()
    if not os.path.exists(argv.src_path):
        raise IOError('Source path does not exist')

    if hasattr(argv, 'unicode_norm'):
        unicode_norm = argv.unicode_norm
    if hasattr(argv, 'lower_case'):
        lower_case = argv.lower_case

    if 0 >= argv.batch_size:
        raise ValueError('Batch size should be positive')
    if 0 >= argv.min_freq:
        raise ValueError('Minimum frequency should be positive')

    logging.basicConfig(level=logging.INFO)

    progress = 0
    vocab = Vocabulary()

    if os.path.isfile(argv.src_path):
        content = _read_content(argv.src_path, unicode_norm, lower_case)
        items = split_func([content])
        vocab.update(items)
    else:
        doc_queue = []
        for root, _, files in os.walk(argv.src_path):
            for file in files:
                content = _read_content(os.path.join(root, file), unicode_norm, lower_case)
                doc_queue.append(content)

                if len(doc_queue) == argv.batch_size:
                    items = split_func(doc_queue)
                    vocab.update(items)
                    doc_queue = []

                progress += 1
                if progress % 1000 == 0:
                    logging.info('Processed {}K files'.format(progress // 1000))

        items = split_func(doc_queue)
        vocab.update(items)

    vocab, _ = vocab.split_by_frequency(argv.min_freq)
    vocab.save(argv.vocab_file, format=argv.file_format)


def count_words():
    count_tokens(lambda content_batch: [w for d in content_batch for w in d.split()], 'word')


def count_chars():
    count_tokens(lambda content_batch: list(''.join(content_batch)), 'character')
