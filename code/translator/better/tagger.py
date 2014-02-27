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
        ## presente indicativo ##

        ('o$', 'ar', 'vmip1s0'),
        ('as$', 'ar', 'vmip2s0'),
        ('a$', 'ar', 'vmip3s0'),
        ('amos$', 'ar', 'vmip1p0'),
        ('áis$', 'ar', 'vmip2p0'),
        ('an$', 'ar', 'vmip3p0'),

        ('o$', 'er', 'vmip1s0'),
        ('es$', 'er', 'vmip2s0'),
        ('e$', 'er', 'vmip3s0'),
        ('emos$', 'er', 'vmip1p0'),
        ('éis$', 'er', 'vmip2p0'),
        ('en$', 'er', 'vmip3p0'),

        ('o$', 'ir', 'vmip1s0'),
        ('es$', 'ir', 'vmip2s0'),
        ('e$', 'ir', 'vmip3s0'),
        ('imos$', 'ir', 'vmip1p0'),
        ('ís$', 'ir', 'vmip2p0'),
        ('en$', 'ir', 'vmip3p0'),

        ## preterito imperfecto ##

        ('aba$', 'ar', 'vmii1s0'),
        ('abas$', 'ar', 'vmii2s0'),
        ('ábamos$', 'ar', 'vmii1p0'),
        ('abais$', 'ar', 'vmii2p0'),
        ('aban$', 'ar', 'vmii3p0'),

        ('ía$', 'er', 'vmii1s0'),
        ('ías$', 'er', 'vmii2s0'),
        ('íamos$', 'er', 'vmii1p0'),
        ('íais$', 'er', 'vmii2p0'),
        ('ían$', 'er', 'vmii3p0'),

        ('ía$', 'ir', 'vmii1s0'),
        ('ías$', 'ir', 'vmii2s0'),
        ('íamos$', 'ir', 'vmii1p0'),
        ('íais$', 'ir', 'vmii2p0'),
        ('ían$', 'ir', 'vmii3p0'),

        ## preterito perfecto simple ##

        ('é$', 'ar', 'vmis1s0'),
        ('aste$', 'ar', 'vmis2s0'),
        ('ó$', 'ar', 'vmis3s0'),
        # TODO: 1pl
        ('asteis$', 'ar', 'vmis2p0'),
        ('aron$', 'ar', 'vmis3p0'),

        ('í$', 'er', 'vmis1s0'),
        ('iste$', 'er', 'vmis2s0'),
        ('ió$', 'er', 'vmis3s0'),
        # TODO: 1pl
        ('isteis$', 'er', 'vmis2p0'),
        ('ieron$', 'er', 'vmis3p0'),

        ('í$', 'ir', 'vmis1s0'),
        ('iste$', 'ir', 'vmis2s0'),
        ('ió$', 'ir', 'vmis3s0'),
        # TODO: 1pl
        ('isteis$', 'ir', 'vmis2p0'),
        ('ieron$', 'ir', 'vmis3p0'),

        ## futuro de indicativo ##

        ('aré$', 'ar', 'vmif1s0'),
        ('arás$', 'ar', 'vmif2s0'),
        ('ará$', 'ar', 'vmif3s0'),
        ('aremos$', 'ar', 'vmif1p0'),
        ('aréis$', 'ar', 'vmif2p0'),
        ('arán$', 'ar', 'vmif3p0'),

        ('eré$', 'er', 'vmif1s0'),
        ('erás$', 'er', 'vmif2s0'),
        ('erá$', 'er', 'vmif3s0'),
        ('eremos$', 'er', 'vmif1p0'),
        ('eréis$', 'er', 'vmif2p0'),
        ('erán$', 'er', 'vmif3p0'),

        ('iré$', 'ir', 'vmif1s0'),
        ('irás$', 'ir', 'vmif2s0'),
        ('irá$', 'ir', 'vmif3s0'),
        ('iremos$', 'ir', 'vmif1p0'),
        ('iréis$', 'ir', 'vmif2p0'),
        ('irán$', 'ir', 'vmif3p0'),

        ## condicional ##

        ('aría$', 'ar', 'vmic1s0'),
        ('arías$', 'ar', 'vmic2s0'),
        ('aríamos$', 'ar', 'vmic1p0'),
        ('aríais$', 'ar', 'vmic2p0'),
        ('arían$', 'ar', 'vmic3p0'),

        ('ería$', 'er', 'vmic1s0'),
        ('erías$', 'er', 'vmic2s0'),
        ('eríamos$', 'er', 'vmic1p0'),
        ('eríais$', 'er', 'vmic2p0'),
        ('erían$', 'er', 'vmic3p0'),

        ('iría$', 'ir', 'vmic1s0'),
        ('irías$', 'ir', 'vmic2s0'),
        ('iríamos$', 'ir', 'vmic1p0'),
        ('iríais$', 'ir', 'vmic2p0'),
        ('irían$', 'ir', 'vmic3p0'),

        ## presente de subjuntivo ##

        ('e$', 'ar', 'vmsp1s0'),
        ('es$', 'ar', 'vmsp2s0'),
        ('emos$', 'ar', 'vmsp1p0'),
        ('éis$', 'ar', 'vmsp2p0'),
        ('en$', 'ar', 'vmsp3p0'),

        ('a$', 'er', 'vmsp1s0'),
        ('as$', 'er', 'vmsp2s0'),
        ('amos$', 'er', 'vmsp1p0'),
        ('áis$', 'er', 'vmsp2p0'),
        ('an$', 'er', 'vmsp3p0'),

        ('a$', 'ir', 'vmsp1s0'),
        ('as$', 'ir', 'vmsp2s0'),
        ('amos$', 'ir', 'vmsp1p0'),
        ('áis$', 'ir', 'vmsp2p0'),
        ('an$', 'ir', 'vmsp3p0'),

        ## preterito imperfecto 1 ##

        ('ara$', 'ar', 'vmsi1s0'),
        ('aras$', 'ar', 'vmsi2s0'),
        ('áramos$', 'ar', 'vmsi1p0'),
        ('arais$', 'ar', 'vmsi2p0'),
        ('aran$', 'ar', 'vmsi3p0'),

        ('iera$', 'er', 'vmsi1s0'),
        ('ieras$', 'er', 'vmsi2s0'),
        ('iéramos$', 'er', 'vmsi1p0'),
        ('ierais$', 'er', 'vmsi2p0'),
        ('ieran$', 'er', 'vmsi3p0'),

        ('iera$', 'ir', 'vmsi1s0'),
        ('ieras$', 'ir', 'vmsi2s0'),
        ('iéramos$', 'ir', 'vmsi1p0'),
        ('ierais$', 'ir', 'vmsi2p0'),
        ('ieran$', 'ir', 'vmsi3p0'),

        ## preterito imperfecto 2 ##

        ('ase$', 'ar', 'vmsi1s0'),
        ('ases$', 'ar', 'vmsi1s0'),
        ('ásemos$', 'ar', 'vmsi1s0'),
        ('aseis$', 'ar', 'vmsi1s0'),
        ('asen$', 'ar', 'vmsi1s0'),

        ('iese$', 'er', 'vmsi1s0'),
        ('ieses$', 'er', 'vmsi1s0'),
        ('iésemos$', 'er', 'vmsi1s0'),
        ('ieseis$', 'er', 'vmsi1s0'),
        ('iesen$', 'er', 'vmsi1s0'),

        ('iese$', 'ir', 'vmsi1s0'),
        ('ieses$', 'ir', 'vmsi1s0'),
        ('iésemos$', 'ir', 'vmsi1s0'),
        ('ieseis$', 'ir', 'vmsi1s0'),
        ('iesen$', 'ir', 'vmsi1s0'),

        ## gerundio ##

        ('ando$', 'ar', 'vmg0000'),
        ('iendo$', 'er', 'vmg0000'),
        ('iendo$', 'ir', 'vmg0000'),
    ]

    VERB_INFINITIVE_TRANSITIONS_RE = [
        (re.compile(regex), replacement, resultant_tag)
        for regex, replacement, resultant_tag in VERB_INFINITIVE_TRANSITIONS
    ]

    # Irregular stems joined with their associated verb ending
    IRREGULAR_STEMS = [
        # subjunctive stems
        'hager',

         # conditional / future stems
        'cabrer', 'pondrer', 'dirir', 'habrer', 'saldrir', 'harer',
        'podrer', 'tendrer', 'querrer', 'valdrer', 'sabrer', 'vendrir',

        # preterite stems
        'anduvar', 'estuvar', 'tuver', 'cuper', 'huber', 'puder',
        'puser', 'super', 'hicer', 'quiser', 'vinir',
    ]

    IRREGULAR_STEMS_RE = re.compile('(?:{})$'.format('|'.join(IRREGULAR_STEMS)))

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
                if (test_tag == 'vmn0000'
                    or self.IRREGULAR_STEMS_RE.search(replaced)):
                    # All good! Append the right tag now
                    results.append((i, tag))

        return results
