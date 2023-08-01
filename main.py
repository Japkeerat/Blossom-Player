import os
import pickle
from argparse import ArgumentParser
from collections import Counter, defaultdict

import streamlit as st


class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.end_of_word

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    def _dfs(self, node, prefix, allowed_letters, first_letter_used):
        if node.end_of_word and first_letter_used:
            yield prefix
        for char, child_node in node.children.items():
            if char in allowed_letters:
                yield from self._dfs(child_node, prefix + char, allowed_letters, first_letter_used or char == allowed_letters[0])

    def get_words_with_letters(self, allowed_letters):
        yield from self._dfs(self.root, "", allowed_letters, False)


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("--center", "-c", type=str)
    parser.add_argument("--others", "-o", type=str, nargs="+")
    arguments = parser.parse_args()
    return arguments

def calculate_score(word, all_letters):
    length = len(word)
    if length == 4:
        score = 2
    elif length == 5:
        score = 4
    elif length == 6:
        score = 6
    elif length == 7:
        score = 12
    else:
        score = 12 + 3 * (length - 7)
    
    if set(word) >= set(all_letters):
        score += 7
    
    letter_counts = Counter(word)
    del letter_counts[all_letters[0]]
    if letter_counts:
        most_common_letter, count = letter_counts.most_common(1)[0]
        score += 5 * count
    else:
        most_common_letter = None

    return score, most_common_letter

def main(trie: Trie):
    st.set_page_config(page_title='Blossom Word Finder', page_icon='🔠', layout="wide")
    st.title('Blossom Word Finder')
    center = st.text_input('Center Letter')
    st.text('Enter the other letters, separated by spaces:')
    others = st.text_input('Other Letters', value='', placeholder='E.g. a b c d e f g')
    
    if st.button('Calculate Scores'):
        if center and others:
            all_letters = [center.lower()] + [o.lower() for o in others.split()]
            words_and_scores = defaultdict(list)
            for word in trie.get_words_with_letters(all_letters):
                if len(word) < 4:
                    continue
                else:
                    score, most_common_letter = calculate_score(word, all_letters)
                    words_and_scores[most_common_letter].append((score, word))
            
            cols = st.columns(len(words_and_scores))
            for col, (most_common_letter, words) in zip(cols, words_and_scores.items()):
                words.sort(reverse=True)
                col.subheader(f"Max scoring words with '{most_common_letter.upper()}'")
                for score, word in words[:5]:
                    col.text(f"{word}: {score}")
        else:
            st.error('Please enter both center and other letters.')



if __name__ == "__main__":
    trie = Trie()
    
    if not os.path.exists('trie.pkl'):
        with open('enable1.txt', 'r') as f:
            words = [line.strip() for line in f]
        
        for word in words:
            trie.insert(word.lower())
            
        with open('trie.pkl', 'wb') as f:
            pickle.dump(trie, f)
        
    else:
        with open('trie.pkl', 'rb') as f:
            trie = pickle.load(f)

    main(trie)
