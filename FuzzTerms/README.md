# FuzzTerms

FuzzTerms is a python module for storing, searching and matching named entities and their terms in a SQLite database.

Searching optionally supports fuzzy string matching, vector similarity searching, with reranking via hybrid (reciprocal
rank fusion) and model-based rerankers.

## Getting Started


## Installation

Available on [PyPI](https://pypi.org/project/FuzzTerms/):

```bash
pip install fuzzterms
```

Fuzzy matching requires rapidfuzz:

```bash
pip install sqlite-vss
```

Semantic matching requires sentence-transformers and sqlite-vss:

```bash
pip install sqlite-vss
```

Note: For sqlite-vss to work, your configuration of Python and SQLite need to allow for loading extensions.


## Maintainer

FuzzTerms was created by [Ian Maurer](https://x.com/imaurer), the CTO of [GenomOncology](https://genomoncology.com).

This MIT-based open-source project was extracted from our product which includes the ability to normalize biomedical
data for use in precision oncology clinical decision support systems. Contact me to learn more about our product
offerings.


