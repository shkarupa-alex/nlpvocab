nlpvocab
========

Python tokens frequency counter with save/load features


Usage
-----

.. code:: python

    from nlpvocab import Vocabulary

    vocab = Vocabulary()
    text  = 'token1 token2 token1 token2 token3'
    vocab.update(text.split())
    vocab.save('vocab.tsv', format`=Vocabulary.FORMAT_TSV_WITH_HEADERS)


