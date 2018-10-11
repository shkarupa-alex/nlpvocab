from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import collections
import logging
import operator
import os
import re
from six.moves import cPickle


class Vocabulary(collections.Counter):
    FORMAT_BINARY_PICKLE = 0
    FORMAT_TSV_WITH_HEADERS = 1
    FORMAT_TSV_WITHOUT_HEADERS = 2

    def trim(self, min_freq):
        if min_freq < 2:
            return

        for token in list(self.keys()):
            if self[token] < min_freq:
                del self[token]

    def tokens(self):
        result = self.most_common()
        if not len(result):
            return []

        # Due to different behaviour
        # for tokens with same counts in Python 2 and 3
        # we should resort result ourselves
        result.sort(key=operator.itemgetter(0))
        result.sort(key=operator.itemgetter(1), reverse=True)
        result, _ = zip(*result)

        return list(result)

    def save(self, filename, format=FORMAT_BINARY_PICKLE):
        assert format in [
            Vocabulary.FORMAT_BINARY_PICKLE,
            Vocabulary.FORMAT_TSV_WITH_HEADERS,
            Vocabulary.FORMAT_TSV_WITHOUT_HEADERS,
        ]

        with open(filename, 'wb') as fout:
            if Vocabulary.FORMAT_BINARY_PICKLE == format:
                cPickle.dump(self, fout, protocol=2)
            else:
                if format == Vocabulary.FORMAT_TSV_WITH_HEADERS:
                    fout.write(u'token\tfrequency\n'.encode('utf-8'))

                for token in self.tokens():
                    token_ = re.sub(
                        r'[^\S]',
                        lambda match: '\\u{0:04x}'.format(ord(match.group(0))),
                        token,
                        flags=re.UNICODE
                    )
                    line = u'{}\t{}\n'.format(token_, self[token])
                    fout.write(line.encode('utf-8'))

    @staticmethod
    def load(filename, format=FORMAT_BINARY_PICKLE):
        assert format in [
            Vocabulary.FORMAT_BINARY_PICKLE,
            Vocabulary.FORMAT_TSV_WITH_HEADERS,
            Vocabulary.FORMAT_TSV_WITHOUT_HEADERS,
        ]

        with open(filename, 'rb') as fin:
            if Vocabulary.FORMAT_BINARY_PICKLE == format:
                instance = cPickle.load(fin)
            else:
                data = {}
                for line in fin:
                    parts = line.decode('utf-8').strip().split('\t')
                    if len(parts) != 2 or parts[1] == 'frequency':
                        continue

                    token, frequency = parts[0], int(parts[1])
                    token = re.sub(
                        r'\\u([\da-f]{4})',
                        lambda match: chr(int(match.group(1), 16)),
                        token,
                        flags=re.UNICODE
                    )
                    data[token] = frequency

                instance = Vocabulary()
                instance.update(data)

        return instance


def _count_tokens(split_func, item_name, format=Vocabulary.FORMAT_TSV_WITH_HEADERS):
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
    assert os.path.exists(argv.src_path)
    assert 0 < argv.batch_size
    assert 0 < argv.min_freq

    logging.basicConfig(level=logging.INFO)

    progress = 0
    vocab = Vocabulary()

    if os.path.isfile(argv.src_path):
        if not argv.src_path.endswith('.txt'):
            logging.warning('Skipping {}'.format(argv.src_path))
            return

        try:
            with open(argv.src_path, 'rb') as sf:
                content = sf.read().decode('utf-8')
                items = split_func([content])
                vocab.update(items)
        except Exception as e:
            logging.error(e)
    else:
        doc_queue = []
        for root, _, files in os.walk(argv.src_path):
            for file in files:
                if not file.endswith('.txt'):
                    logging.warning('Skipping {}'.format(file))
                    continue

                try:
                    with open(os.path.join(root, file), 'rb') as sf:
                        content = sf.read().decode('utf-8')
                        doc_queue.append(content)
                except Exception as e:
                    logging.error(e)

                if len(doc_queue) == argv.batch_size:
                    items = split_func(doc_queue)
                    vocab.update(items)
                    doc_queue = []

                progress += 1
                if progress % 1000 == 0:
                    logging.info('Processed {}K files'.format(progress // 1000))

        items = split_func(doc_queue)
        vocab.update(items)

    vocab.trim(argv.min_freq)
    vocab.save(argv.vocab_file, format=format)


def count_words():
    _count_tokens(lambda content_batch: [w for d in content_batch for w in d.split()], 'word')


def count_chars():
    _count_tokens(lambda content_batch: list(''.join(content_batch)), 'character')
