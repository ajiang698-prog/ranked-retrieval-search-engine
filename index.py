import sys
import os
import re
import json
import shutil
from collections import defaultdict

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

class Indexer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.index = defaultdict(lambda: defaultdict(list))
        self.count_tokens = set() # total number of tokens to index
        self.count_documents = 0

    def revert_token(self, token):
        # singular/plural (noun)
        noun_root = self.lemmatizer.lemmatize(token, pos='n')
        # tense (verb)
        verb_root = self.lemmatizer.lemmatize(token, pos='v')

        if noun_root != token:
            return noun_root
        elif verb_root != token:
            return verb_root
        else:
            return token
    
    def process_token(self, word):
        # invalid token
        if re.fullmatch(r'[^a-z0-9]+', word):
            return []
        
        # remove abbreviations
        word = word.replace('.', '')
        # '-'
        if '-' in word:
            words = word.split('-')
            revert = self.revert_token(words[1])
            token = words[0] + '-' + revert
        else:
            token = self.revert_token(word)
        
        # count tokens
        self.count_tokens.add(token)
        
        # save both original and reverted tokens
        if word != token:
            tokens = [token, word]
        else:
            tokens = [token]

        return tokens
    
    def process_sentence(self, sentence):
        text = sentence
        text = re.sub(r"(\'s|s\')", "", text) # remove 's, s'
        text = re.sub(r'\b([A-Za-z]{3,})-([A-Za-z]+)\b', r'\1 \2', text) # split hyphenated terms whose first part is greater than 3 letters
        text = re.sub(r'(?<=[0-9]),(?=[0-9])', '', text) # remove commas in numeric tokens
        # text = re.sub(r'(\b[0-9]+)\.[0-9]+\b', r'\1', text)
        text = re.sub(r'\.[0-9]+\b', '', text) # remove decimal places
        text = text.lower() # case insensitive
        return text
    
    def split_sentence(self, sentence):
        result=[]
        # split the sentence by word_tokenize()
        for word in word_tokenize(sentence):
            word = self.process_token(word)
            result.append(word)
        return result
    
    def process_document(self, doc_id, doc_path, index_path):
        token_idx = 0 # initialize
        # read document
        with open(doc_path, "r") as f:
            content = f.read().strip()
        
        lines = content.split("\n")
        for lineno, line in enumerate(lines):
            text = self.process_sentence(line)
            tokens = self.split_sentence(text)

            for token in tokens:
                if not token: # invalid token
                    continue
                for tk in token:
                    self.index[tk][doc_id].append((token_idx, lineno))
                token_idx += 1
    
    def to_json(self, directory):
        with open (directory, "w") as f:
            json.dump(self.index, f, default=lambda x: dict(x), indent=4)

    def create_index(self, doc_directory, index_directory):
        os.makedirs(index_directory, exist_ok=True) # index_directory
        index_path = os.path.join(index_directory, 'data') # index_directory/data
        json_path = os.path.join(index_directory, 'index.json') # index_directory/index.json
        os.makedirs(index_path, exist_ok=True) # index_directory/data

        # iterate through all files in doc_directory
        for file in os.listdir(doc_directory):
            doc_path = os.path.join(doc_directory, file)
            # copy all files to index_directory/data
            if os.path.isfile(doc_path):
                shutil.copy(doc_path, index_path)

            self.process_document(file, doc_path, index_path)
            self.count_documents += 1
        
        # convert index directory to a json file
        self.to_json(json_path)

def main():
    if len(sys.argv[1:]) != 2:
        print("Usage: python index.py [folder-of-documents] [folder-of-indexes]")
        sys.exit(1)

    doc_dir = sys.argv[1]
    ind_dir = sys.argv[2]

    indexer = Indexer()
    indexer.create_index(doc_dir, ind_dir)

    print(f"Total number of documents: {indexer.count_documents}")
    print(f"Total number of tokens: {len(indexer.count_tokens):,}")
    print(f"Total number of terms: {len(indexer.index):,}")

if __name__ == "__main__":
    main()