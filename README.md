# nlpvocab

Tokens frequency counter with save/load features.
Supports save/load with Pickle and TSV formats.

Provides 2 command-line scripts for building words and characters frequency vocabularies.

## Usage from Python


```python

from nlpvocab import Vocabulary

text  = 'token1 token2 token1 token2 token3'

vocab = Vocabulary()
vocab.update(text.split())
vocab.save('vocab.tsv', format=Vocabulary.FORMAT_TSV_WITH_HEADERS)
```


## Usage from command line


```bash

nlpvocab-chars /a/b/d/e dir_chars_vocab.tsv
nlpvocab-words /a/b/d/e dir_words_vocab.tsv
nlpvocab-chars /a/b.txt file_chars_vocab.tsv
nlpvocab-words /a/b.txt file_words_vocab.tsv
```
