# -*- coding: utf-8 -*-
"""Defines a `Translator` interface."""

from nltk.tokenize import word_tokenize


class Translator(object):
    """An abstract class which defines helpers for performing machine
    translation.

    Subclasses need to implement the `translate` method."""

    def __init__(self, dictionary_path):
        self.dictionary = self.load_dictionary(dictionary_path)

    def load_dictionary(self, dictionary_path):
        """Load a dictionary from a dictionary file. Returns a
        dictionary mapping from source-language word to candidate
        target-language phrases."""

        dictionary = {}
        with open(dictionary_path, 'r') as dictionary_f:
            for line in dictionary_f:
                entry = line.strip().split(',')
                dictionary[entry[0]] = entry[1:]

        return dictionary

    def tokenize_sentence(self, sentence):
        """Tokenize a sentence loaded from a file. Returns a list of
        word tokens."""

        sentence = sentence.replace('—', '--')
        sentence = sentence.replace('…', '...')
        sentence = sentence.replace('¿', '¿ ')

        return word_tokenize(sentence)

    def load_sentences(self, sentences_path):
        """Load sentences from a sentences file. Returns a list of
        tokenized sentences."""

        sentences = []
        with open(sentences_path, 'r') as sentences_f:
            for line in sentences_f:
                sentences.append(self.tokenize_sentence(line))

        return sentences

    def translate(self, sentence):
        """Translate a tokenized Spanish sentence into English. Returns
        an English string."""

        raise NotImplementedError

    def translate_sentences(self, sentences_path):
        """Translate a list of Spanish sentences stored at
        `sentences_path` to English. Returns a list of English
        strings."""

        return [self.translate(sentence)
                for sentence in self.load_sentences(sentences_path)]
