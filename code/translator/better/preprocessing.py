# -*- coding: utf-8 -*-
"""Defines preprocessing operations -- functions which operate on and
annotate source-language text."""

import logging
import os.path
import pickle
import re

from nltk import BigramTagger, UnigramTagger
from nltk.corpus import cess_esp

from translator.better.tagger import BetterTagger


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
    (('lo', 'que'), None, 'v......'): ('qué', 'dt0cn0'),

    (('de', 'que'), None, '(n|d)......|v.s....|pp...a..'): ('que', 'cs'),

    # 'para', 'de' followed by an infinitive verb translates to English
    # "to"
    (('para',), None, 'v.n....'): ('a', 'sps00'),
    (('de',), None, 'v.n....'): ('a', 'sps00'),
}

def join_phrases(sentence, annotations, phrases=None):
    """Joins phrases which occur in certain part-of-speech contexts,
    replacing the phrase with a new single value."""

    if phrases is None:
        phrases = PHRASES

    if 'pos' not in annotations:
        raise ValueError('Phrase joining requires POS annotations -- '
                         'insert the POS annotator into the pipeline '
                         'before the phrase joiner')

    results = {}

    for (tokens, before_context,
       after_context), (replacement, replacement_pos) in phrases.items():
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
            results[instance_start] = (len(tokens), replacement,
                                       replacement_pos)

    # Now build a result sentence
    sentence_ret = []
    pos_ret = []

    i = 0
    while i < len(sentence):
        if i in results:
            original_length, replacement, replacement_pos = results[i]
            sentence_ret.append(replacement)
            pos_ret.append((replacement, replacement_pos))

            i += original_length
        else:
            sentence_ret.append(sentence[i])
            pos_ret.append((sentence[i], annotations['pos'][i][1]))

            i += 1

    annotations['pos'] = pos_ret

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
            TAGGER = BetterTagger(bigram_tagger)

            with open(TAGGER_FILENAME, 'w') as f:
                pickle.dump(TAGGER, f)

    parts_of_speech = TAGGER.tag([t.lower() for t in sentence])

    annotations['pos'] = parts_of_speech
    return sentence, annotations


def revert_by_pos(pos_before, pos_after):
    """Build a preprocessing function which swaps one or more instances
    of tokens with the POS `pos_before` with one or more instances of
    tokens with the POS `pos_after` when the latter tokens directly
    succeed the former."""

    before_re = (pos_before and re.compile(pos_before)) or None
    after_re = (pos_after and re.compile(pos_after)) or None

    def revert_fn(sentence, annotations):
        # TODO: Support more than two-element swap
        pos = annotations['pos']
        pos_bigrams = zip(pos, pos[1:])

        to_swap = []
        skip_next = False

        for i, ((t1, pos_tag_1), (_, pos_tag_2)) in enumerate(pos_bigrams):
            if skip_next:
                skip_next = False
                continue

            before_match = ((pos_tag_1 is None and before_re is None)
                            or (pos_tag_1 is not None and before_re is not None
                               and before_re.match(pos_tag_1)))
            after_match = ((pos_tag_2 is None and after_re is None)
                           or (pos_tag_2 is not None and after_re is not None
                              and after_re.match(pos_tag_2)))

            if before_match and after_match:
                to_swap.append(i)
                skip_next = True

        for i in to_swap:
            sentence[i], sentence[i + 1] = sentence[i + 1], sentence[i]
            pos[i + 1], pos[i] = pos[i], pos[i + 1]

        return sentence, annotations


    return revert_fn
