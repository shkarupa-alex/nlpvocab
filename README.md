# nlpvocab

Tokens frequency counter with save/load features.
Supports save/load with Pickle and TSV formats.


## Usage


```python

from nlpvocab import Vocabulary

text  = 'token1 token2 token1 token2 token3'

vocab = Vocabulary()
vocab.update(text.split())
vocab.save('vocab.tsv', format=Vocabulary.FORMAT_TSV_WITH_HEADERS)
```
