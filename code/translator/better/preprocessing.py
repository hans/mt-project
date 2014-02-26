# -*- coding: utf-8 -*-
"""Defines preprocessing operations -- functions which operate on and
annotate source-language text."""

import logging
import os.path
import pickle
import re

from nltk import BigramTagger, UnigramTagger
from nltk.corpus import cess_esp


def find_sublist(xs, sublist):
    """Yields the `(start, end)` indices of the instances of `sublist`
    within `xs`, where `sublist` begins at `start` and runs up to (but
    not including) `end`."""

    sublist_len = len(sublist)
    for i in xrange(0, len(xs)):
        xs_sub = xs[i:i+sublist_len]
        if tuple(xs_sub) == tuple(sublist):
            yield i, i + sublist_len

# Mapping of the form
#
#     (phrase, before_POS_context, after_POS_context) => replacement
PHRASES = {
    # 'lo que' followed by a verb translates to English "what"
    (('lo', 'que'), None, 'v......'): 'qué',

    (('de', 'que'), None, '(n|d)......'): 'que',
}

def join_phrases(sentence, annotations):
    """Joins phrases which occur in certain part-of-speech contexts,
    replacing the phrase with a new single value."""

    if 'pos' not in annotations:
        raise ValueError('Phrase joining requires POS annotations -- '
                         'insert the POS annotator into the pipeline '
                         'before the phrase joiner')

    results = {}

    for (tokens, before_context, after_context), replacement in PHRASES.items():
        for instance_start, instance_end in find_sublist(sentence, tokens):
            # Check before POS context
            if before_context is not None:
                if instance_start == 0:
                    continue

                before_pos = annotations['pos'][instance_start - 1][1] or ''
                before_match = re.match(before_context, before_pos)
                if not before_match:
                    continue

            # Check after POS context
            if after_context is not None:
                if instance_end == len(sentence):
                    continue

                after_pos = annotations['pos'][instance_end][1] or ''
                after_match = re.match(after_context, after_pos)

                if not after_match:
                    continue

            # Context matches went all right -- add this phrase mapping
            # to our results
            results[instance_start] = (len(tokens), replacement)

    # Now build a result sentence
    sentence_ret = []
    i = 0
    while i < len(sentence):
        if i in results:
            original_length, replacement = results[i]
            sentence_ret.append(replacement)
            i += original_length
        else:
            sentence_ret.append(sentence[i])
            i += 1

    return sentence_ret, annotations


TAGGER = None
TAGGER_FILENAME = 'pos_tagger.pickle'
def annotate_pos(sentence, annotations):
    """Produce part-of-speech annotations for a source-language
    sentence."""

    global TAGGER
    if TAGGER is None:
        logging.debug('Training part-of-speech tagger..')

        if os.path.isfile(TAGGER_FILENAME):
            with open(TAGGER_FILENAME, 'r') as f:
                TAGGER = pickle.load(f)
        else:
            training_data = cess_esp.tagged_sents()
            unigram_tagger = UnigramTagger(training_data)
            bigram_tagger = BigramTagger(training_data, backoff=unigram_tagger)

            TAGGER = bigram_tagger

            with open(TAGGER_FILENAME, 'w') as f:
                pickle.dump(TAGGER, f)

    parts_of_speech = TAGGER.tag(sentence)

    annotations['pos'] = parts_of_speech
    return sentence, annotations
