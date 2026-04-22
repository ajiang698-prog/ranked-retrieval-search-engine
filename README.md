# Ranked Retrieval Search Engine

This project implements a simple search engine in Python using an inverted index with positional information. It support document indexing and ranked retrieval based on term coverage, proximity between matched terms, and preservation of query term order. 

## Features

- Positional inverted index
- Case-intensitive search
- Token normalization (lemmatization)
- Handling of plural forms and verb tenses
- Basic punctuation and numeric processing
- Ranked retrieval based on:
    - Term coverage
    - Term proximity
    - Query term order
- Optional display of matching lines (`> query` mode)

## Project Structure

```
.
├── index.py
├── search.py
├── sample_docs/
├── sample_queries.txt
├── requirements.txt
└── README.md
```

## Setup

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Download required NLTK resources:
```bash
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('punkt_tab')"
python -c "import nltk; nltk.download('wordnet')"
python -c "import nltk; nltk.download('omw-1.4')"
```

## Usage

1. Build index
```bash
python index.py sample_docs sample_index
```

2. Run search
```bash
python search.py sample_index
```
Then type queries in the terminal.

## Example Queries

```
garlic bread
> garlic bread
apple
u.s. company
breach
```

## Example Output

```
> garlic bread
> 1
Garlic bread is very popular in restaurants. 
> 2
Bread garlic combinations appears in some recipes.
> 3
Garlic is used in many traditional dishes.
Bread is often served at the end of the meal.
> 4
Garlic is widely used in cooking.
apple
5
u.s. company
6
9
breach
9
```

## Ranking Strategy

Documents are ranked based on:

- **Coverage**: proportion of query terms matched
- **Proximity**: distance between matched terms
- **Order**: whether term order matches the query

Documents with more matched terms, closer term positions, and correct order are ranked higher. 

## Notes

- Both lemmatized tokens and original tokens are stored to improve recall and allow flexible matching.
- This project was originally developed as coursework and later refined for demonstration purposes.
