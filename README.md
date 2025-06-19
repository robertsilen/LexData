# Python bot framework for Lexemes on Wikidata

This is a small library to create bots, scripts and tools about Wikidata
Lexemes. It's philosophy is to have a transparent thin layer on top of the
internal datastuctures enriched with convenient functions without hiding the
power of the access to the internals.

LexData is still in beta phase and there fore some features are missing and
functions might be renamed in future.

## Features

- Create and manage Wikidata Lexemes
- Add forms and senses to lexemes
- Add claims to lexemes, forms, and senses (including external-id properties)
- Search and find existing lexemes
- Support for various Wikidata data types (entities, strings, external-ids, etc.)

The code of AitalvivemBot was used as a starting point, but probably theres not
a single line of code that wasn't rewritten.

Install from pypi:
```
 $ pip install LexData
```

Read the docs: [https://nudin.github.io/LexData/](https://nudin.github.io/LexData/)
