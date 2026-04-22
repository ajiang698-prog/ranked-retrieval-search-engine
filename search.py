import sys
import os
import re
import json
from itertools import product

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

class Search:
    def __init__(self, index_directory):
        self.index_directory = index_directory
        self.lemmatizer = WordNetLemmatizer()
        self.index = self.load_index(index_directory)
    
    def load_index(self, index_directory):
        path = os.path.join(index_directory, "index.json")
        try:
            with open(path, "r") as f:
                index = json.load(f)
            return index
        except FileNotFoundError:
            print(f"Error: {path} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: {path} is not a valid json file")
            sys.exit(1)

    def revert_word(self, word):
        noun_root = self.lemmatizer.lemmatize(word, pos='n')
        verb_root = self.lemmatizer.lemmatize(word, pos='v')
        if noun_root != word:
            return noun_root
        elif verb_root != word:
            return verb_root
        else:
            return word

    def process_word(self, word):
        if re.fullmatch(r'[^a-z0-9\-]+', word):
            return []
        word = word.replace('.', '')

        if '-' in word:
            words = word.split('-')
            revert = self.revert_word(words[1])
            term = words[0] + '-' + revert
        else:
            term = self.revert_word(word)
        
        if word != term:
            terms = [term, word]
        else:
            terms = [term]
        return terms
    
    def preprocess_query(self, query):
        query = re.sub(r"(\'s|s\')", "", query)
        query = re.sub(r'\b([A-Za-z]{3,})-([A-Za-z]+)\b', r'\1 \2', query)
        query = re.sub(r'(?<=[0-9]),(?=[0-9])', '', query)
        query = re.sub(r'(\b[0-9]+)\.[0-9]+\b', r'\1', query)
        query = query.lower()

        terms = []
        for word in word_tokenize(query):
            term = self.process_word(word)
            terms.append(term)
        return terms

    def find_documents(self, terms):
        # For each term, if variants exists, find positions for all variants
        result = {}
        for idx, variants in enumerate(terms):
            revert = variants[0]
            if revert in self.index:
                for doc_id, positions in self.index[revert].items():
                    if doc_id not in result:
                        result[doc_id] = {}
                    if idx not in result[doc_id]:
                        result[doc_id][idx] = []
                    # result[doc_id][idx].extend(positions)
                    result[doc_id][idx].extend([tuple(pos) for pos in positions])
        return result
    
    def calculate_coverage(self, num_of_term, num_of_idx):
        coverage = float(num_of_idx/num_of_term)
        return coverage       

    def find_cloest_matching_term(self, position_info):
        term_idx = sorted(position_info.keys())
        position_list = [position_info[i] for i in term_idx]
        # if only one term is matched, the proximity and order scores are both 0
        if len(term_idx) == 1:
            min_line = min(l[1] for l in position_list[0])
            return 0, 0, min_line
        
        combinations = list(product(*position_list))

        # initialization
        min_dist = float('inf')
        best_order = float('-inf')
        best_line = float('inf')
        
        for comb in combinations:
            # calculate term distance for each comb
            term_dist = 0
            term_order = 0
            for c in range(len(comb)-1):
                dist = abs(comb[c][0] - comb[c+1][0])-1
                term_dist += max(0, dist)
                if comb[c][0] < comb[c+1][0]:
                    term_order += 1
            # find the minimum lineno
            term_line = min(c[1] for c in comb)

            # find the cloest matching term:
            # 1: term_dist ? min_dist, 
            if term_dist < min_dist:
                min_dist = term_dist
                best_order = term_order
                best_line = term_line
                cloest_matching_term = comb
            # 2: term_dist = min_dist, term_order ? best_order
            elif term_dist == min_dist and term_order > best_order:
                best_order = term_order
                best_line = term_line
                cloest_matching_term = comb
            # 3: term_dist = min_dist, term_order = best_order, term_line ? best_line
            elif term_dist == min_dist and term_order == best_order and term_line < best_line:
                best_line = term_line
                cloest_matching_term = comb
        
        avg_dist = min_dist/(len(term_idx)-1)
        proximity = 1/(1+avg_dist)
        order = best_order*0.1
        return proximity, order, cloest_matching_term

    def rank_documents(self, docs, terms):
        num_of_term = len(terms)
        doc_term_scores = []
        for doc_id, position_info in docs.items():
            num_of_idx = len(position_info)
            coverage = self.calculate_coverage(num_of_term, num_of_idx)
            proximity, order, cloest_matching_term = self.find_cloest_matching_term(position_info)
            score = coverage + proximity + order
            doc_term_scores.append((doc_id, cloest_matching_term, score))

        return doc_term_scores

    def print_line(self, doc_id, cloest_matching_term):
        path = os.path.join(self.index_directory, "data", doc_id)
        try:
            with open(path, "r") as f:
                content = f.read().strip()
            lines = content.split("\n")
            if isinstance(cloest_matching_term, int):
                line = lines[cloest_matching_term]
                print(line)
            else:
                for lineno in sorted(set(n[1] for n in cloest_matching_term)):
                    line = lines[lineno]
                    print(line)
        except FileNotFoundError:
            return

    def process_query(self, query):
        special = False
        
        # query starts with "> "
        if query.startswith("> "):
            query = query.removeprefix("> ")
            special = True

        terms = self.preprocess_query(query) # Big apples => [["big"], ["apple", "apples"]]
        matching_docs = self.find_documents(terms)
        result = self.rank_documents(matching_docs, terms) # doc_id, cloest_matching_term, score
        result.sort(key=lambda x: (-x[2], int(x[0])))
        
        # print out the result
        for doc_id, cloest_matching_term, _ in result:
            if special:
                print(f"> {doc_id}")
                self.print_line(doc_id, cloest_matching_term)
            else:
                print(doc_id)

def main():
    if len(sys.argv[1:]) != 1:
        print("Usage: python3 search.py [folder-of-indexes]")
        sys.exit(1)

    ind_dir = sys.argv[1]
    if not os.path.exists(ind_dir):
        print(f"Error: {ind_dir} not found")
        sys.exit(1)

    search_engine = Search(ind_dir)
    
    for line in sys.stdin:
        query = line.strip()
        if not query: # query is empty
            continue
        search_engine.process_query(query)

if __name__ == "__main__":
    main()