from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from six.moves import cPickle
import collections
import operator
import re


class Vocabulary(collections.Counter):
    FORMAT_BINARY_PICKLE = 0
    FORMAT_TSV_WITH_HEADERS = 1
    FORMAT_TSV_WITHOUT_HEADERS = 2

    def trim(self, min_freq):
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
