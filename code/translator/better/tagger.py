# -*- coding: utf-8 -*-
"""Adds a layer of heuristics on top of NLTK's probabilistic Spanish POS
tagger."""

import re

from nltk.tag.api import TaggerI


class BetterTagger(TaggerI):
    """Defines a Spanish part-of-speech tagger which adds a layer of
    heuristics onto another tagger. This tagger runs the
    dependency-injected tagger and adjusts its output."""

    def __init__(self, tagger):
        self.tagger = tagger

    def tag(self, tokens):
        tagged_tokens = self.tagger.tag(tokens)

        # Collect untagged tokens and their indices
        untagged = [(i, token) for i, (token, tag)
                    in enumerate(tagged_tokens)
                    if tag is None]

        adjustments = []

        adjustments.extend(self.add_verb_tags(untagged, tokens))

        for index, new_pos in adjustments:
            tagged_tokens[index] = (tagged_tokens[index][0], new_pos)

        return tagged_tokens

    # Regular-expression replacements which may bring us from a
    # conjugated verb form to an infinitive form, and the corresponding
    # POS tag that should result if we actually do reach an infinitive
    # form via this replacement
    VERB_INFINITIVE_TRANSITIONS = [
        ('é$', 'ar', 'vmis1s0'),
        ('aste$', 'ar', 'vmis2s0'),
        ('ó$', 'ar', 'vmis3s0'),
        # TODO lots more
    ]

    VERB_INFINITIVE_TRANSITIONS_RE = [
        (re.compile(regex), replacement, resultant_tag)
        for regex, replacement, resultant_tag in VERB_INFINITIVE_TRANSITIONS
    ]

    def add_verb_tags(self, untagged_tokens, sentence):
        """Given a list of untagged tokens of the form `(sentence_index,
        token)` and the containing sentence `sentence`, attempt to
        provide accurate part-of-speech tags for mistakenly untagged
        verbs.

        Returns a potentially empty list of the form `[(sentence_index,
        tag)]`, where each element in the list describes a tag
        discovered by the method."""

        results = []
        for i, u_token in untagged_tokens:
            for regex, replacement, tag in self.VERB_INFINITIVE_TRANSITIONS_RE:
                replaced = regex.sub(replacement, u_token)
                if replaced == u_token:
                    continue

                # See if what we have now is an infinitive
                test_tag = self.tagger.tag([replaced])[0][1]
                if test_tag == 'vmn0000':
                    # All good! Append the right tag now
                    results.append((i, tag))

        return results
