import itertools
import logging
import os.path
import sys

from translator.better import BetterTranslator
from translator.direct import DirectTranslator


def main():
    if len(sys.argv) != 3:
        print "Usage: 'python translate.py original_text.txt dictFile.txt'"
        return
    if not os.path.isfile(sys.argv[1]):
        print "Original text file is invalid"
        return
    if not os.path.isfile(sys.argv[2]):
        print "Dictionary file is invalid"
        return

    logging.getLogger().setLevel(logging.DEBUG)

    translators = [DirectTranslator, BetterTranslator]

    for translator_class in translators:
        translator = translator_class(sys.argv[2])
        sentences = translator.translate_sentences(sys.argv[1])

        print '----- %s' % translator_class
        for sentence in sentences:
            print ' '.join(next(itertools.product(*sentence)))


if __name__ == '__main__':
    main()
