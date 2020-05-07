from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import operator
import re
from builtins import chr
from six.moves import cPickle


class Vocabulary(collections.Counter):
    FORMAT_BINARY_PICKLE = 'BINARY_PICKLE'
    FORMAT_TSV_WITH_HEADERS = 'TSV_WITH_HEADERS'
    FORMAT_TSV_WITHOUT_HEADERS = 'TSV_WITHOUT_HEADERS'

    def split_by_size(self, high_size):
        high, low = Vocabulary(), Vocabulary()

        if high_size >= len(self):
            return Vocabulary(self), low

        for idx, token in enumerate(self.tokens()):
            if idx < high_size:
                high[token] = self[token]
            else:
                low[token] = self[token]

        return high, low

    def split_by_frequency(self, min_high_freq):
        high, low = Vocabulary(), Vocabulary()

        if min_high_freq < 2:
            return Vocabulary(self), low

        for token in list(self.keys()):
            if self[token] >= min_high_freq:
                high[token] = self[token]
            else:
                low[token] = self[token]

        return high, low

    def tokens(self):
        result = self.most_common()
        if not len(result):
            return []

        # Due to different behaviour for tokens with same counts
        # in Python 2 and 3 we should resort result manually
        result.sort(key=operator.itemgetter(0))
        result.sort(key=operator.itemgetter(1), reverse=True)
        result, _ = zip(*result)

        return list(result)

    def save(self, filename, format=FORMAT_BINARY_PICKLE):
        if format not in [
            Vocabulary.FORMAT_BINARY_PICKLE,
            Vocabulary.FORMAT_TSV_WITH_HEADERS,
            Vocabulary.FORMAT_TSV_WITHOUT_HEADERS,
        ]:
            raise ValueError('Unsupported format')

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
        if format not in [
            Vocabulary.FORMAT_BINARY_PICKLE,
            Vocabulary.FORMAT_TSV_WITH_HEADERS,
            Vocabulary.FORMAT_TSV_WITHOUT_HEADERS,
        ]:
            raise ValueError('Unsupported format')

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

    def __add__(self, other):
        return Vocabulary(super(Vocabulary, self).__add__(other))

    def __sub__(self, other):
        return Vocabulary(super(Vocabulary, self).__sub__(other))

    def __or__(self, other):
        return Vocabulary(super(Vocabulary, self).__or__(other))

    def __and__(self, other):
        return Vocabulary(super(Vocabulary, self).__and__(other))

    def __pos__(self):
        raise NotImplementedError()

    def __neg__(self):
        raise NotImplementedError()
