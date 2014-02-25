# -*- coding: utf-8 -*-

import sys
import os
import itertools

from core import Translator

class DirectTranslator(Translator):
    """A `Translator` which performs naive word-to-word translation of
    the source text.

    Serves as the baseline algorithm for this exercise."""

    def translate(self, sentence):
        return [self.dictionary.get(word.lower(), [word])
                for word in sentence]


def main():
    if len(sys.argv) != 3:
        print "Usage: 'python translator.py original_text.txt dictFile.txt'"
        return
    if not os.path.isfile(sys.argv[1]):
        print "Original text file is invalid"
        return
    if not os.path.isfile(sys.argv[2]):
        print "Dictionary file is invalid"
        return

    translator = DirectTranslator(sys.argv[2])
    sentences = translator.translate_sentences(sys.argv[1])

    for sentence in sentences:
        print ' '.join(next(itertools.product(*sentence)))


if __name__ == "__main__":
    main()
